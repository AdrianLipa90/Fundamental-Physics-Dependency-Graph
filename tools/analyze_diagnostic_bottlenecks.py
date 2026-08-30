#!/usr/bin/env python3
"""Identify mandatory promoted-DAG nodes/edges on observed symptom paths.

For each already localized frontier, this tool asks a structural question: which promoted
claims or dependency edges are unavoidable on every route from the frontier to each
observed symptom anchor? A node/edge is reported as mandatory only when removing it
breaks all promoted paths to the target. This is graph dominance evidence, not physical
causation.

CANDIDATE_ONLY edges are excluded.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "dependency_graph.yaml"
BUILD_DIR = ROOT / "build"
PROMOTED = {"CANONICAL", "CANONICAL_CROSS_REPO", "CANONICAL_FRONTIER"}


class BottleneckError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise BottleneckError(f"{path}: expected JSON object")
    return value


def load_graph(path: Path = GRAPH_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    if not isinstance(value, dict):
        raise BottleneckError("dependency graph must be a mapping")
    return value


def promoted_indexes(graph: dict[str, Any]):
    nodes = {row["claim_id"] for row in graph.get("nodes", [])}
    outgoing: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in graph.get("edges", []):
        if edge.get("authority") not in PROMOTED:
            continue
        if edge.get("from") not in nodes or edge.get("to") not in nodes:
            raise BottleneckError("promoted edge references unknown claim")
        outgoing[edge["from"]].append(edge)
    for source in outgoing:
        outgoing[source] = sorted(
            outgoing[source], key=lambda row: (row["to"], row["authority"])
        )
    return nodes, outgoing


def reachable(
    outgoing: dict[str, list[dict[str, Any]]],
    source: str,
    target: str,
    *,
    blocked_node: str | None = None,
    blocked_edge: tuple[str, str, str] | None = None,
) -> bool:
    if source == blocked_node or target == blocked_node:
        return False
    if source == target:
        return True
    seen = {source}
    queue = deque([source])
    while queue:
        current = queue.popleft()
        for edge in outgoing.get(current, []):
            sig = (edge["from"], edge["to"], edge["authority"])
            if blocked_edge is not None and sig == blocked_edge:
                continue
            nxt = edge["to"]
            if nxt == blocked_node or nxt in seen:
                continue
            if nxt == target:
                return True
            seen.add(nxt)
            queue.append(nxt)
    return False


def reachable_region(
    outgoing: dict[str, list[dict[str, Any]]], source: str
) -> set[str]:
    seen = {source}
    queue = deque([source])
    while queue:
        current = queue.popleft()
        for edge in outgoing.get(current, []):
            nxt = edge["to"]
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def reverse_reachable_to_target(
    outgoing: dict[str, list[dict[str, Any]]], target: str
) -> set[str]:
    incoming: defaultdict[str, list[str]] = defaultdict(list)
    for source, edges in outgoing.items():
        for edge in edges:
            incoming[edge["to"]].append(source)
    seen = {target}
    queue = deque([target])
    while queue:
        current = queue.popleft()
        for prev in incoming.get(current, []):
            if prev not in seen:
                seen.add(prev)
                queue.append(prev)
    return seen


def candidate_subgraph(
    outgoing: dict[str, list[dict[str, Any]]], source: str, target: str
) -> tuple[set[str], list[dict[str, Any]]]:
    from_source = reachable_region(outgoing, source)
    to_target = reverse_reachable_to_target(outgoing, target)
    nodes = from_source & to_target
    edges = [
        edge
        for src in nodes
        for edge in outgoing.get(src, [])
        if edge["to"] in nodes
    ]
    return nodes, edges


def analyze_target(
    outgoing: dict[str, list[dict[str, Any]]], source: str, target: str
) -> dict[str, Any]:
    if not reachable(outgoing, source, target):
        return {
            "target": target,
            "reachable": False,
            "mandatory_nodes": [],
            "mandatory_edges": [],
        }

    path_nodes, path_edges = candidate_subgraph(outgoing, source, target)
    mandatory_nodes = []
    for node in sorted(path_nodes - {source, target}):
        if not reachable(outgoing, source, target, blocked_node=node):
            mandatory_nodes.append(node)

    mandatory_edges = []
    for edge in sorted(
        path_edges, key=lambda row: (row["from"], row["to"], row["authority"])
    ):
        sig = (edge["from"], edge["to"], edge["authority"])
        if not reachable(outgoing, source, target, blocked_edge=sig):
            mandatory_edges.append(
                {
                    "from": edge["from"],
                    "to": edge["to"],
                    "authority": edge["authority"],
                }
            )

    return {
        "target": target,
        "reachable": True,
        "candidate_path_node_count": len(path_nodes),
        "candidate_path_edge_count": len(path_edges),
        "mandatory_nodes": mandatory_nodes,
        "mandatory_edges": mandatory_edges,
    }


def intersection_edges(target_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    reachable_rows = [row for row in target_rows if row.get("reachable")]
    if not reachable_rows:
        return []
    sets = [
        {
            (edge["from"], edge["to"], edge["authority"])
            for edge in row.get("mandatory_edges", [])
        }
        for row in reachable_rows
    ]
    common = set.intersection(*sets) if sets else set()
    return [
        {"from": src, "to": dst, "authority": authority}
        for src, dst, authority in sorted(common)
    ]


def analyze(diagnosis: dict[str, Any], graph: dict[str, Any]) -> dict[str, Any]:
    if diagnosis.get("schema") != "FPDG_INCONSISTENCY_DIAGNOSIS_V0_1":
        raise BottleneckError("unsupported diagnosis schema")
    nodes, outgoing = promoted_indexes(graph)
    zones = []

    for zone in diagnosis.get("pain_zones", []):
        frontier = zone.get("frontier_claim")
        if not isinstance(frontier, str) or frontier not in nodes:
            raise BottleneckError(f"unknown frontier claim {frontier!r}")
        targets = sorted(
            {
                target
                for target in zone.get("symptom_anchors", [])
                if isinstance(target, str) and target in nodes and target != frontier
            }
        )
        target_rows = [analyze_target(outgoing, frontier, target) for target in targets]
        reachable_rows = [row for row in target_rows if row.get("reachable")]

        node_sets = [set(row.get("mandatory_nodes", [])) for row in reachable_rows]
        mandatory_nodes = sorted(set.intersection(*node_sets)) if node_sets else []
        mandatory_edges = intersection_edges(target_rows)

        zones.append(
            {
                "frontier_claim": frontier,
                "symptom_targets": targets,
                "mandatory_nodes": mandatory_nodes,
                "mandatory_edges": mandatory_edges,
                "target_analyses": target_rows,
                "interpretation": (
                    "MANDATORY_PROMOTED_WITNESS_PATH_STRUCTURE_ONLY; "
                    "NO_PHYSICAL_CAUSALITY_INFERRED"
                ),
            }
        )

    return {
        "schema": "FPDG_DIAGNOSTIC_BOTTLENECKS_V0_1",
        "status": "ANALYZED" if zones else "NO_ZONES",
        "candidate_edges_included": False,
        "causal_inference_performed": False,
        "zones": zones,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = ["# FPDG Diagnostic Bottlenecks", "", f"Status: **{report['status']}**", ""]
    for zone in report.get("zones", []):
        lines.append(f"## `{zone['frontier_claim']}`")
        lines.append("")
        lines.append(
            "Observed symptom targets: "
            + (", ".join(f"`{x}`" for x in zone["symptom_targets"]) or "none")
        )
        lines.append("")
        if zone["mandatory_nodes"]:
            lines.append("Mandatory promoted nodes common to all reachable symptom targets:")
            for node in zone["mandatory_nodes"]:
                lines.append(f"- `{node}`")
        else:
            lines.append("No non-endpoint promoted node is mandatory across all reachable symptom targets.")
        lines.append("")
        if zone["mandatory_edges"]:
            lines.append("Mandatory promoted edges common to all reachable symptom targets:")
            for edge in zone["mandatory_edges"]:
                lines.append(
                    f"- `{edge['from']} -> {edge['to']}` [{edge['authority']}]"
                )
        else:
            lines.append("No promoted edge is mandatory across all reachable symptom targets.")
        lines.append("")
    lines.extend(
        [
            "Removing a reported mandatory node/edge disconnects the frontier from every analyzed reachable symptom target in the promoted DAG.",
            "This is graph-dominance evidence only; it does not assert physical causation.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("diagnosis", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        report = analyze(load_json(args.diagnosis), load_graph())
        BUILD_DIR.mkdir(exist_ok=True)
        (BUILD_DIR / "DIAGNOSTIC_BOTTLENECKS.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        (BUILD_DIR / "DIAGNOSTIC_BOTTLENECKS.md").write_text(
            render_markdown(report), encoding="utf-8"
        )
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"{report['status']}: zones={len(report['zones'])}")
        return 0
    except (OSError, json.JSONDecodeError, yaml.YAMLError, BottleneckError, KeyError, TypeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
