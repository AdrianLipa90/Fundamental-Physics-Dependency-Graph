#!/usr/bin/env python3
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "dependency_graph.yaml"
CLAIMS_PATH = ROOT / "claims.jsonl"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def load_graph():
    with GRAPH_PATH.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        fail("dependency_graph.yaml must contain a mapping")
    return data


def load_claims():
    claims = []
    with CLAIMS_PATH.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                claims.append(json.loads(line))
            except json.JSONDecodeError as exc:
                fail(f"claims.jsonl line {line_no}: {exc}")
    return claims


def main() -> None:
    graph = load_graph()
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])

    node_ids = [n.get("claim_id") for n in nodes]
    if any(not x for x in node_ids):
        fail("every graph node must have claim_id")
    if len(node_ids) != len(set(node_ids)):
        fail("duplicate claim_id in dependency_graph.yaml")

    node_set = set(node_ids)
    for idx, edge in enumerate(edges, 1):
        src = edge.get("from")
        dst = edge.get("to")
        authority = edge.get("authority")
        if src not in node_set:
            fail(f"edge {idx}: missing source node {src}")
        if dst not in node_set:
            fail(f"edge {idx}: missing target node {dst}")
        if authority == "CANDIDATE_ONLY" and not edge.get("promotion_required", False):
            fail(f"edge {idx}: candidate edge must declare promotion_required=true")

    claim_rows = load_claims()
    claim_ids = [row.get("claim_id") for row in claim_rows]
    if any(not x for x in claim_ids):
        fail("every claims.jsonl row must have claim_id")
    if len(claim_ids) != len(set(claim_ids)):
        fail("duplicate claim_id in claims.jsonl")

    if set(claim_ids) != node_set:
        missing_registry = sorted(node_set - set(claim_ids))
        missing_graph = sorted(set(claim_ids) - node_set)
        fail(
            "graph/claim registry mismatch: "
            f"missing_registry={missing_registry}, missing_graph={missing_graph}"
        )

    print(
        "PASS: canonical DAG structurally valid; "
        f"nodes={len(nodes)} edges={len(edges)} claims={len(claim_rows)}"
    )


if __name__ == "__main__":
    main()
