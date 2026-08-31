#!/usr/bin/env python3
import json
from collections import defaultdict, deque
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from federation_surface import (  # noqa: E402
    FederationSurfaceError,
    load_effective_claims,
    load_effective_graph,
    repository_registry,
)

PROMOTED_AUTHORITIES = {"CANONICAL", "CANONICAL_CROSS_REPO", "CANONICAL_FRONTIER"}
ALLOWED_AUTHORITIES = PROMOTED_AUTHORITIES | {"CANDIDATE_ONLY"}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


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
    try:
        graph = load_effective_graph()
        repos = repository_registry()
        claim_rows = load_effective_claims()
    except (OSError, json.JSONDecodeError, FederationSurfaceError) as exc:
        fail(str(exc))

    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    if not isinstance(nodes, list) or not isinstance(edges, list):
        fail("graph nodes and edges must be lists")

    node_ids = [node.get("claim_id") for node in nodes]
    if any(not claim_id for claim_id in node_ids):
        fail("every graph node must have claim_id")
    if len(node_ids) != len(set(node_ids)):
        fail("duplicate claim_id in effective dependency graph")

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

    claim_ids = [row.get("claim_id") for row in claim_rows]
    if any(not claim_id for claim_id in claim_ids):
        fail("every effective claim row must have claim_id")
    if len(claim_ids) != len(set(claim_ids)):
        fail("duplicate claim_id in effective claim registry")

    claim_map = {row["claim_id"]: row for row in claim_rows}
    if set(claim_map) != node_set:
        fail(
            "effective graph/claim registry mismatch: "
            f"missing_registry={sorted(node_set - set(claim_map))}, "
            f"missing_graph={sorted(set(claim_map) - node_set)}"
        )

    for claim_id, node in node_map.items():
        row = claim_map[claim_id]
        if row.get("repository") != node.get("repository"):
            fail(f"{claim_id}: repository mismatch")
        if row.get("status") != node.get("status"):
            fail(
                f"{claim_id}: status mismatch graph={node.get('status')} "
                f"claims={row.get('status')}"
            )
        if not row.get("evidence_class"):
            fail(f"{claim_id}: missing evidence_class")

    candidate_count = sum(edge["authority"] == "CANDIDATE_ONLY" for edge in edges)
    cross_repo_count = sum(
        node_map[edge["from"]]["repository"] != node_map[edge["to"]]["repository"]
        for edge in edges
    )
    print(
        "PASS: effective canonical DAG structurally valid; "
        f"nodes={len(nodes)} edges={len(edges)} claims={len(claim_rows)} "
        f"repositories={len(repos)} overlays={len(graph.get('effective_federation_overlays', []))} "
        f"cross_repo_edges={cross_repo_count} candidate_edges={candidate_count}"
    )


if __name__ == "__main__":
    main()
