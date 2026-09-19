#!/usr/bin/env python3
"""Generate every registered source export and reconcile it with the effective DAG."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from bootstrap_export import build_export  # noqa: E402
from federation_surface import load_effective_graph  # noqa: E402
from import_exports import (  # noqa: E402
    ExportError,
    load_yaml,
    reconcile,
    repo_registry,
    validate_export,
)


def main() -> int:
    source_heads = load_yaml(ROOT / "source_heads.yaml")
    sources = source_heads.get("sources", {})
    registry = repo_registry()
    graph = load_effective_graph()
    if set(sources) != set(registry):
        print(
            f"FAIL: source_heads repositories mismatch: "
            f"sources={sorted(sources)} registry={sorted(registry)}",
            file=sys.stderr,
        )
        return 1

    out_root = ROOT / "build" / "exports"
    if out_root.exists():
        shutil.rmtree(out_root)
    out_root.mkdir(parents=True)
    all_problems = []
    summary = []
    try:
        for repo_id in sorted(registry):
            source = sources[repo_id]
            source_commit = source.get("commit")
            export = build_export(repo_id, source_commit, source_heads.get("captured_at"))
            path = out_root / f"{repo_id}.DEPENDENCY_EXPORT.json"
            path.write_text(json.dumps(export, indent=2) + "\n", encoding="utf-8")
            validate_export(export, path, registry)
            problems = reconcile(graph, export)
            all_problems.extend(problems)
            summary.append({
                "repository_id": repo_id,
                "source_commit": source_commit,
                "claims": len(export["claims"]),
                "local_edges": len(export.get("local_edges", [])),
                "status": "PASS" if not problems else "DRIFT",
                "path": str(path.relative_to(ROOT)),
            })
    except (OSError, ValueError, ExportError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    receipt = {
        "schema": "FPDG_SOURCE_EXPORT_ROUNDTRIP_V0_2",
        "source_heads_schema": source_heads.get("schema"),
        "captured_at": source_heads.get("captured_at"),
        "repository_count": len(registry),
        "effective_overlays": graph.get("effective_federation_overlays", []),
        "exports": summary,
        "problems": all_problems,
        "status": "PASS" if not all_problems else "DRIFT",
    }
    receipt_path = ROOT / "build" / "SOURCE_EXPORT_ROUNDTRIP.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    if all_problems:
        return 2
    print(f"PASS: {len(registry)}-source dependency export roundtrip reconciles")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
