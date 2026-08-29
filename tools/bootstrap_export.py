#!/usr/bin/env python3
"""Generate a source-repository DEPENDENCY_EXPORT.json from the current canonical graph.

This is a bootstrap/migration aid only. The generated export becomes source-authoritative
only after review in the corresponding source repository.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise SystemExit(f"FAIL: {path} must contain a mapping")
    return data


def load_claims(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            claim_id = row.get("claim_id")
            if not claim_id:
                raise SystemExit(f"FAIL: claims.jsonl line {line_no} missing claim_id")
            rows[claim_id] = row
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository_id", choices=["TIR", "IDT", "RFC", "SOH"])
    parser.add_argument("source_commit")
    parser.add_argument("--generated-at", default=None)
    args = parser.parse_args()

    if not HEX40.fullmatch(args.source_commit):
        raise SystemExit("FAIL: source_commit must be a 40-character lowercase hex SHA")

    registry = load_yaml(ROOT / "repos.yaml")["repositories"]
    graph = load_yaml(ROOT / "dependency_graph.yaml")
    claims_registry = load_claims(ROOT / "claims.jsonl")

    repo_id = args.repository_id
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

    local_edges = []
    for edge in graph.get("edges", []):
        if edge.get("from") in node_set and edge.get("to") in node_set:
            local_edges.append(dict(edge))

    out = {
        "schema": "FPDG_DEPENDENCY_EXPORT_V0_1",
        "repository_id": repo_id,
        "repository": registry[repo_id]["repository"],
        "source_commit": args.source_commit,
        "claims": claims,
        "local_edges": local_edges,
    }
    if args.generated_at:
        out["generated_at"] = args.generated_at

    print(json.dumps(out, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
