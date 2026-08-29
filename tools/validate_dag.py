#!/usr/bin/env python3
import json
from collections import defaultdict, deque
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "dependency_graph.yaml"
CLAIMS_PATH = ROOT / "claims.jsonl"
REPOS_PATH = ROOT / "repos.yaml"

PROMOTED_AUTHORITIES = {"CANONICAL", "CANONICAL_CROSS_REPO", "CANONICAL_FRONTIER"}
ALLOWED_AUTHORITIES = PROMOTED_AUTHORITIES | {"CANDIDATE_ONLY"}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        fail(f"{path.name} must contain a mapping")
    return data


def load_claims():
    rows = []
    with CLAIMS_PATH.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                fail(f"claims.jsonl line {line_no}: {exc}")
            if not isinstance(row, dict):
                fail(f"claims.jsonl line {line_no}: row must be an object")
            rows.append(row)
    return rows


def assert_promoted_dag(node_set, edges):
    indegree = {node: 0 for node in node_set}
    adjacency = defaultdict(list)
    for edge in edges:
        if edge["authority"] not in PROMOTED_AUTHORITIES:
            continue
        src, dst = edge["from"], edge["to"]
        adjacency[src].append(dst)
        indegree[dst] += 1

    queue = deque(node for node, degree in indegree.items() if degree == 0)
    seen = 0
    while queue:
        node = queue.popleft()
        seen += 1
        for dst in adjacency[node]:
            indegree[dst] -= 1
            if indegree[dst] == 0:
                queue.append(dst)

    if seen != len(node_set):
        cyclic = sorted(node for node, degree in indegree.items() if degree > 0)
        fail(f"promoted dependency graph contains a cycle involving {cyclic}")


def main() -> None:
    graph = load_yaml(GRAPH_PATH)
    repos = load_yaml(REPOS_PATH).get("repositories", {})
    if not repos:
        fail("repos.yaml must define repositories")

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    if not isinstance(nodes, list) or not isinstance(edges, list):
        fail("graph nodes and edges must be lists")

    node_ids = [node.get("claim_id") for node in nodes]
    if any(not claim_id for claim_id in node_ids):
        fail("every graph node must have claim_id")
    if len(node_ids) != len(set(node_ids)):
        fail("duplicate claim_id in dependency_graph.yaml")

    node_map = {node["claim_id"]: node for node in nodes}
    node_set = set(node_map)
    for claim_id, node in node_map.items():
        if node.get("repository") not in repos:
            fail(f"{claim_id}: unknown repository {node.get('repository')}")
        if not node.get("status"):
            fail(f"{claim_id}: missing status")
        if not (node.get("source") or node.get("source_evidence")):
            fail(f"{claim_id}: missing source/source_evidence")

    edge_keys = set()
    for idx, edge in enumerate(edges, 1):
        src = edge.get("from")
        dst = edge.get("to")
        authority = edge.get("authority")
        if src not in node_set:
            fail(f"edge {idx}: missing source node {src}")
        if dst not in node_set:
            fail(f"edge {idx}: missing target node {dst}")
        if src == dst:
            fail(f"edge {idx}: self dependency {src}")
        if authority not in ALLOWED_AUTHORITIES:
            fail(f"edge {idx}: invalid authority {authority}")

        key = (src, dst, authority)
        if key in edge_keys:
            fail(f"edge {idx}: duplicate edge {key}")
        edge_keys.add(key)

        cross_repo = node_map[src]["repository"] != node_map[dst]["repository"]
        if authority == "CANONICAL" and cross_repo:
            fail(f"edge {idx}: cross-repository canonical edge must use CANONICAL_CROSS_REPO")
        if authority == "CANONICAL_CROSS_REPO" and not cross_repo:
            fail(f"edge {idx}: CANONICAL_CROSS_REPO used for intra-repository edge")

        if authority == "CANDIDATE_ONLY":
            if not edge.get("promotion_required", False):
                fail(f"edge {idx}: candidate edge must declare promotion_required=true")
            if not edge.get("promotion_gate"):
                fail(f"edge {idx}: candidate edge must declare promotion_gate")

    assert_promoted_dag(node_set, edges)

    claim_rows = load_claims()
    claim_ids = [row.get("claim_id") for row in claim_rows]
    if any(not claim_id for claim_id in claim_ids):
        fail("every claims.jsonl row must have claim_id")
    if len(claim_ids) != len(set(claim_ids)):
        fail("duplicate claim_id in claims.jsonl")

    claim_map = {row["claim_id"]: row for row in claim_rows}
    if set(claim_map) != node_set:
        missing_registry = sorted(node_set - set(claim_map))
        missing_graph = sorted(set(claim_map) - node_set)
        fail(
            "graph/claim registry mismatch: "
            f"missing_registry={missing_registry}, missing_graph={missing_graph}"
        )

    for claim_id, node in node_map.items():
        row = claim_map[claim_id]
        if row.get("repository") != node.get("repository"):
            fail(f"{claim_id}: repository mismatch graph={node.get('repository')} claims={row.get('repository')}")
        if row.get("status") != node.get("status"):
            fail(f"{claim_id}: status mismatch graph={node.get('status')} claims={row.get('status')}")
        if not row.get("evidence_class"):
            fail(f"{claim_id}: missing evidence_class in claims.jsonl")

    candidate_count = sum(edge["authority"] == "CANDIDATE_ONLY" for edge in edges)
    cross_repo_count = sum(
        node_map[edge["from"]]["repository"] != node_map[edge["to"]]["repository"]
        for edge in edges
    )
    print(
        "PASS: canonical DAG structurally valid; "
        f"nodes={len(nodes)} edges={len(edges)} claims={len(claim_rows)} "
        f"cross_repo_edges={cross_repo_count} candidate_edges={candidate_count}"
    )


if __name__ == "__main__":
    main()
