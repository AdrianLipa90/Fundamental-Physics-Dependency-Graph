#!/usr/bin/env python3
"""Generate a source DEPENDENCY_EXPORT.json from the effective FPDG surface.

Bootstrap/migration aid only. Source authority begins after review in the corresponding
source repository.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from federation_surface import (  # noqa: E402
    FederationSurfaceError,
    load_effective_claims,
    load_effective_graph,
    repository_registry,
)

HEX40 = re.compile(r"^[0-9a-f]{40}$")


def build_export(repo_id: str, source_commit: str, generated_at: str | None = None) -> dict[str, Any]:
    registry = repository_registry()
    if repo_id not in registry:
        raise ValueError(f"unknown repository_id {repo_id!r}")
    if not HEX40.fullmatch(source_commit):
        raise ValueError("source_commit must be a 40-character lowercase hex SHA")

    graph = load_effective_graph()
    claims_registry = {row["claim_id"]: row for row in load_effective_claims()}
    node_ids = [
        node["claim_id"]
        for node in graph.get("nodes", [])
        if node.get("repository") == repo_id
    ]
    node_set = set(node_ids)
    claims = []
    for claim_id in node_ids:
        row = dict(claims_registry[claim_id])
        row.pop("repository", None)
        claims.append(row)
    local_edges = [
        dict(edge)
        for edge in graph.get("edges", [])
        if edge.get("from") in node_set and edge.get("to") in node_set
    ]
    out = {
        "schema": "FPDG_DEPENDENCY_EXPORT_V0_1",
        "repository_id": repo_id,
        "repository": registry[repo_id]["repository"],
        "source_commit": source_commit,
        "claims": claims,
        "local_edges": local_edges,
    }
    if generated_at:
        out["generated_at"] = generated_at
    return out


def main() -> int:
    registry = repository_registry()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository_id", choices=sorted(registry))
    parser.add_argument("source_commit")
    parser.add_argument("--generated-at", default=None)
    args = parser.parse_args()
    try:
        out = build_export(args.repository_id, args.source_commit, args.generated_at)
    except (OSError, json.JSONDecodeError, FederationSurfaceError, ValueError) as exc:
        raise SystemExit(f"FAIL: {exc}") from exc
    print(json.dumps(out, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
