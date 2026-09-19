#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict, deque
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from federation_surface import BASE_GRAPH_PATH, load_effective_graph  # noqa: E402

GRAPH_PATH = BASE_GRAPH_PATH
PROMOTED_AUTHORITIES = {"CANONICAL", "CANONICAL_CROSS_REPO", "CANONICAL_FRONTIER"}


def load_graph(path=GRAPH_PATH):
    return load_effective_graph(path)


def compute_impact(graph, claim_id, include_candidates=False):
    nodes = {node["claim_id"]: node for node in graph.get("nodes", [])}
    if claim_id not in nodes:
        raise KeyError(claim_id)

    allowed = set(PROMOTED_AUTHORITIES)
    if include_candidates:
        allowed.add("CANDIDATE_ONLY")

    adjacency = defaultdict(list)
    for edge in graph.get("edges", []):
        if edge.get("authority") in allowed:
            adjacency[edge["from"]].append(edge)

    queue = deque([(claim_id, 0)])
    seen = {claim_id}
    impacted = []
    while queue:
        src, depth = queue.popleft()
        for edge in adjacency.get(src, []):
            dst = edge["to"]
            if dst in seen:
                continue
            seen.add(dst)
            next_depth = depth + 1
            node = nodes[dst]
            impacted.append({
                "claim_id": dst,
                "repository": node["repository"],
                "status": node["status"],
                "distance": next_depth,
                "via_authority": edge["authority"],
            })
            queue.append((dst, next_depth))
    return impacted


def main():
    parser = argparse.ArgumentParser(
        description="Compute downstream revalidation impact for one changed claim."
    )
    parser.add_argument("claim_id")
    parser.add_argument("--include-candidates", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    graph = load_graph()
    try:
        impacted = compute_impact(graph, args.claim_id, args.include_candidates)
    except KeyError:
        raise SystemExit(f"Unknown claim_id: {args.claim_id}")

    if args.json:
        print(json.dumps({
            "changed_claim": args.claim_id,
            "include_candidates": args.include_candidates,
            "impacted_count": len(impacted),
            "impacted": impacted,
        }, indent=2))
        return

    print(f"changed: {args.claim_id}")
    print(f"impacted: {len(impacted)}")
    for row in impacted:
        print(
            f"{row['distance']:>2}  {row['repository']:<3}  "
            f"{row['claim_id']}  [{row['status']}]"
        )


if __name__ == "__main__":
    main()
