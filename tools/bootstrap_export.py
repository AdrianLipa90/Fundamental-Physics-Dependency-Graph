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
REPOSITORY_IDS = ("TIR", "IDT", "RFC", "SOH")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a mapping")
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
                raise ValueError(f"claims.jsonl line {line_no} missing claim_id")
            rows[claim_id] = row
    return rows


def build_export(repo_id: str, source_commit: str, generated_at: str | None = None) -> dict[str, Any]:
    if repo_id not in REPOSITORY_IDS:
        raise ValueError(f"unknown repository_id {repo_id!r}")
    if not HEX40.fullmatch(source_commit):
        raise ValueError("source_commit must be a 40-character lowercase hex SHA")

    registry = load_yaml(ROOT / "repos.yaml")["repositories"]
    graph = load_yaml(ROOT / "dependency_graph.yaml")
    claims_registry = load_claims(ROOT / "claims.jsonl")

    node_ids = [
        node["claim_id"]
        for node in graph.get("nodes", [])
        if node.get("repository") == repo_id
    ]
    node_set = set(node_ids)

    claims: list[dict[str, Any]] = []
    for claim_id in node_ids:
        row = dict(claims_registry[claim_id])
        row.pop("repository", None)
        claims.append(row)

    local_edges = [
        dict(edge)
        for edge in graph.get("edges", [])
        if edge.get("from") in node_set and edge.get("to") in node_set
    ]

    out: dict[str, Any] = {
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository_id", choices=REPOSITORY_IDS)
    parser.add_argument("source_commit")
    parser.add_argument("--generated-at", default=None)
    args = parser.parse_args()

    try:
        out = build_export(args.repository_id, args.source_commit, args.generated_at)
    except (OSError, json.JSONDecodeError, yaml.YAMLError, ValueError) as exc:
        raise SystemExit(f"FAIL: {exc}") from exc

    print(json.dumps(out, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
