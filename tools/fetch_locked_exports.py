#!/usr/bin/env python3
"""Fetch and identity-check every registered locked DEPENDENCY_EXPORT.json snapshot."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from federation_surface import FederationSurfaceError, repository_registry  # noqa: E402

LOCK_PATH = ROOT / "source_exports.lock.json"


def raw_url(repository: str, commit: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{repository}/{commit}/{path}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / ".source_exports")
    args = parser.parse_args()
    try:
        lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        if lock.get("schema") not in {
            "FPDG_SOURCE_EXPORT_LOCK_V0_1",
            "FPDG_SOURCE_EXPORT_LOCK_V0_2",
            "FPDG_SOURCE_EXPORT_LOCK_V0_3",
        }:
            raise RuntimeError("unsupported source export lock schema")
        sources = lock.get("sources")
        registry = repository_registry()
        if not isinstance(sources, dict) or set(sources) != set(registry):
            raise RuntimeError(
                f"lock/registry source mismatch: lock={sorted(sources or {})} "
                f"registry={sorted(registry)}"
            )
        args.out.mkdir(parents=True, exist_ok=True)
        for repo_id in sorted(registry):
            entry = sources[repo_id]
            if entry.get("repository") != registry[repo_id].get("repository"):
                raise RuntimeError(f"{repo_id}: repository identity mismatch")
            url = raw_url(entry["repository"], entry["export_commit"], entry["path"])
            request = urllib.request.Request(
                url, headers={"User-Agent": "FPDG-source-export-fetcher/0.3"}
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = response.read().decode("utf-8")
            export = json.loads(payload)
            if export.get("repository_id") != repo_id:
                raise RuntimeError(f"{repo_id}: repository_id mismatch")
            if export.get("repository") != entry["repository"]:
                raise RuntimeError(f"{repo_id}: repository mismatch")
            if export.get("source_commit") != entry["source_commit"]:
                raise RuntimeError(
                    f"{repo_id}: source_commit mismatch: "
                    f"{export.get('source_commit')} != {entry['source_commit']}"
                )
            out_path = args.out / f"{repo_id}.json"
            out_path.write_text(json.dumps(export, indent=2) + "\n", encoding="utf-8")
            print(
                f"{repo_id}: FETCHED export_commit={entry['export_commit']} "
                f"source_commit={entry['source_commit']} "
                f"repository_head={entry.get('repository_head', entry['source_commit'])}"
            )
        print(f"PASS: all {len(registry)} locked source exports fetched and verified")
        return 0
    except (
        OSError,
        KeyError,
        json.JSONDecodeError,
        RuntimeError,
        FederationSurfaceError,
        urllib.error.URLError,
    ) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
