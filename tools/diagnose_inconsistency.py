#!/usr/bin/env python3
"""Localize an FPDG inconsistency to the smallest observed promoted-dependency frontier.

This tool is deterministic. It does not ask GREMLIN to decide what is canonically wrong.
It maps structured failure evidence to exact claims/edges/source paths, finds the earliest
observed failing claims in the promoted DAG, builds witness paths, identifies boundary
seams, and projects the downstream revalidation blast radius.

GREMLIN consumes the resulting diagnosis only as a candidate-mining surface.
CANDIDATE_ONLY edges never participate in canonical localization or invalidation.
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
CLAIMS_PATH = ROOT / "claims.jsonl"
BUILD_DIR = ROOT / "build"

sys.path.insert(0, str(ROOT / "tools"))
from impact import compute_impact  # noqa: E402

PROMOTED = {"CANONICAL", "CANONICAL_CROSS_REPO", "CANONICAL_FRONTIER"}


class DiagnosisError(RuntimeError):
    pass


def load_graph(path: Path = GRAPH_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        graph = yaml.safe_load(fh)
    if not isinstance(graph, dict):
        raise DiagnosisError("dependency graph must be a mapping")
    return graph


def load_claims(path: Path = CLAIMS_PATH) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise DiagnosisError(f"claims.jsonl line {line_no}: {exc}") from exc
            if not isinstance(row, dict):
                raise DiagnosisError(f"claims.jsonl line {line_no}: row must be an object")
            rows.append(row)
    return rows


def load_evidence(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise DiagnosisError("evidence must be a JSON object")
    if value.get("schema") != "FPDG_INCONSISTENCY_EVIDENCE_V0_1":
        raise DiagnosisError(f"unsupported evidence schema {value.get('schema')!r}")
    observations = value.get("observations")
    if not isinstance(observations, list) or not observations:
        raise DiagnosisError("evidence observations must be a non-empty list")
    return value


def graph_indexes(graph: dict[str, Any]):
    nodes = {row["claim_id"]: row for row in graph.get("nodes", [])}
    outgoing: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    incoming: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in graph.get("edges", []):
        if edge.get("authority") not in PROMOTED:
            continue
        outgoing[edge["from"]].append(edge)
        incoming[edge["to"]].append(edge)
    for table in (outgoing, incoming):
        for key in table:
            table[key] = sorted(
                table[key], key=lambda row: (row["from"], row["to"], row["authority"])
            )
    return nodes, outgoing, incoming


def _candidate_claims_for_path(
    source_path: str,
    repository: str | None,
    claims: list[dict[str, Any]],
) -> list[str]:
    matches = []
    for row in claims:
        if row.get("source_path") != source_path:
            continue
        if repository and row.get("repository") != repository:
            continue
        if isinstance(row.get("claim_id"), str):
            matches.append(row["claim_id"])
    return sorted(set(matches))


def anchor_observation(
    observation: dict[str, Any],
    nodes: dict[str, dict[str, Any]],
    claims: list[dict[str, Any]],
) -> dict[str, Any]:
    obs_id = observation.get("observation_id")
    if not isinstance(obs_id, str) or not obs_id:
        raise DiagnosisError("every observation requires observation_id")

    anchors: list[str] = []
    method = "UNANCHORED"
    precision = "NONE"

    claim_id = observation.get("claim_id")
    if isinstance(claim_id, str) and claim_id in nodes:
        anchors = [claim_id]
        method = "EXACT_CLAIM"
        precision = "EXACT"
    elif isinstance(observation.get("edge"), dict):
        edge = observation["edge"]
        endpoints = [edge.get("from"), edge.get("to")]
        anchors = sorted({item for item in endpoints if isinstance(item, str) and item in nodes})
        if anchors:
            method = "EXACT_EDGE_ENDPOINTS"
            precision = "EXACT"
    elif isinstance(observation.get("source_path"), str):
        anchors = _candidate_claims_for_path(
            observation["source_path"], observation.get("repository"), claims
        )
        if anchors:
            method = "EXACT_SOURCE_PATH"
            precision = "EXACT" if len(anchors) == 1 else "MULTI_CLAIM_PATH"

    if not anchors and isinstance(observation.get("repository"), str):
        repository = observation["repository"]
        anchors = sorted(
            row["claim_id"]
            for row in claims
            if row.get("repository") == repository and row.get("claim_id") in nodes
        )
        if anchors:
            method = "REPOSITORY_FALLBACK"
            precision = "COARSE"

    return {
        "observation_id": obs_id,
        "kind": observation.get("kind", "UNSPECIFIED"),
        "repository": observation.get("repository"),
        "claim_id": observation.get("claim_id"),
        "edge": observation.get("edge"),
        "source_path": observation.get("source_path"),
        "expected": observation.get("expected"),
        "observed": observation.get("observed"),
        "evidence_refs": observation.get("evidence_refs", []),
        "anchors": anchors,
        "anchor_method": method,
        "precision": precision,
        "external_subject": claim_id if isinstance(claim_id, str) and claim_id not in nodes else None,
    }


def reachable(outgoing: dict[str, list[dict[str, Any]]], source: str) -> set[str]:
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


def minimal_observed_frontier(
    anchors: set[str], outgoing: dict[str, list[dict[str, Any]]]
) -> list[str]:
    reach = {claim_id: reachable(outgoing, claim_id) for claim_id in anchors}
    frontier = []
    for claim_id in sorted(anchors):
        has_upstream_observed_anchor = any(
            other != claim_id and claim_id in reach[other] for other in anchors
        )
        if not has_upstream_observed_anchor:
            frontier.append(claim_id)
    return frontier


def shortest_path(
    outgoing: dict[str, list[dict[str, Any]]], source: str, target: str
) -> list[str] | None:
    if source == target:
        return [source]
    parent: dict[str, str | None] = {source: None}
    queue = deque([source])
    while queue:
        current = queue.popleft()
        for edge in outgoing.get(current, []):
            nxt = edge["to"]
            if nxt in parent:
                continue
            parent[nxt] = current
            if nxt == target:
                path = [target]
                while path[-1] != source:
                    path.append(parent[path[-1]])  # type: ignore[arg-type]
                return list(reversed(path))
            queue.append(nxt)
    return None


def zone_for_frontier(
    frontier_claim: str,
    observed_anchors: set[str],
    nodes: dict[str, dict[str, Any]],
    outgoing: dict[str, list[dict[str, Any]]],
    incoming: dict[str, list[dict[str, Any]]],
    anchored_observations: list[dict[str, Any]],
    graph: dict[str, Any],
) -> dict[str, Any]:
    symptom_anchors = sorted(
        target
        for target in observed_anchors
        if target == frontier_claim or shortest_path(outgoing, frontier_claim, target) is not None
    )

    witness_paths: list[list[str]] = []
    zone_nodes = {frontier_claim}
    for target in symptom_anchors:
        path = shortest_path(outgoing, frontier_claim, target)
        if path:
            witness_paths.append(path)
            zone_nodes.update(path)

    boundary_in = []
    boundary_out = []
    for node in sorted(zone_nodes):
        for edge in incoming.get(node, []):
            if edge["from"] not in zone_nodes:
                boundary_in.append(edge)
        for edge in outgoing.get(node, []):
            if edge["to"] not in zone_nodes:
                boundary_out.append(edge)

    relevant_obs = []
    for observation in anchored_observations:
        if any(anchor in symptom_anchors for anchor in observation["anchors"]):
            relevant_obs.append(observation["observation_id"])

    impact = compute_impact(graph, frontier_claim, include_candidates=False)
    immediate_parents = sorted(edge["from"] for edge in incoming.get(frontier_claim, []))
    immediate_children = sorted(edge["to"] for edge in outgoing.get(frontier_claim, []))

    return {
        "frontier_claim": frontier_claim,
        "repository": nodes[frontier_claim].get("repository"),
        "status": nodes[frontier_claim].get("status"),
        "source": nodes[frontier_claim].get("source") or nodes[frontier_claim].get("source_evidence"),
        "symptom_anchors": symptom_anchors,
        "observation_ids": sorted(set(relevant_obs)),
        "witness_paths": witness_paths,
        "witness_nodes": sorted(zone_nodes),
        "immediate_promoted_parents": immediate_parents,
        "immediate_promoted_children": immediate_children,
        "incoming_boundary_edges": boundary_in,
        "outgoing_boundary_edges": boundary_out,
        "downstream_revalidation": impact,
        "downstream_revalidation_count": len(impact),
    }


def diagnose(
    graph: dict[str, Any],
    claims: list[dict[str, Any]],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    nodes, outgoing, incoming = graph_indexes(graph)
    anchored = [anchor_observation(obs, nodes, claims) for obs in evidence["observations"]]
    exact_anchors = {
        claim_id
        for obs in anchored
        if obs["precision"] != "COARSE"
        for claim_id in obs["anchors"]
    }
    coarse_anchors = {
        claim_id
        for obs in anchored
        if obs["precision"] == "COARSE"
        for claim_id in obs["anchors"]
    }
    observed_anchors = exact_anchors or coarse_anchors
    frontier = minimal_observed_frontier(observed_anchors, outgoing) if observed_anchors else []
    zones = [
        zone_for_frontier(
            claim_id,
            observed_anchors,
            nodes,
            outgoing,
            incoming,
            anchored,
            graph,
        )
        for claim_id in frontier
    ]

    unanchored = [obs["observation_id"] for obs in anchored if not obs["anchors"]]
    coarse = [obs["observation_id"] for obs in anchored if obs["precision"] == "COARSE"]
    mode = "EXACT" if exact_anchors else ("COARSE_FALLBACK" if coarse_anchors else "UNLOCALIZED")

    return {
        "schema": "FPDG_INCONSISTENCY_DIAGNOSIS_V0_1",
        "status": "LOCALIZED" if frontier else "UNLOCALIZED",
        "localization_mode": mode,
        "candidate_edges_included": False,
        "observations": anchored,
        "observed_claim_anchors": sorted(observed_anchors),
        "minimal_failing_frontier": frontier,
        "pain_zones": zones,
        "coarse_observation_ids": coarse,
        "unanchored_observation_ids": unanchored,
        "gremlin_role": "CANDIDATE_PATTERN_MINING_ONLY",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = ["# FPDG Inconsistency Diagnosis", ""]
    lines.append(f"Status: **{report['status']}**")
    lines.append(f"Localization: **{report['localization_mode']}**")
    lines.append("")
    if report["minimal_failing_frontier"]:
        lines.append("## Minimal failing frontier")
        lines.append("")
        for zone in report["pain_zones"]:
            lines.append(
                f"- `{zone['frontier_claim']}` — {zone['repository']} — "
                f"downstream revalidation: {zone['downstream_revalidation_count']}"
            )
            if zone["incoming_boundary_edges"]:
                lines.append("  - incoming seams:")
                for edge in zone["incoming_boundary_edges"]:
                    lines.append(
                        f"    - `{edge['from']} -> {edge['to']}` [{edge['authority']}]"
                    )
            if zone["witness_paths"]:
                lines.append("  - witness paths:")
                for path in zone["witness_paths"]:
                    lines.append("    - `" + " -> ".join(path) + "`")
    else:
        lines.append("No claim-level frontier could be localized from the supplied evidence.")

    if report["coarse_observation_ids"]:
        lines.extend(["", "Coarse repository fallback was required for: " + ", ".join(report["coarse_observation_ids"])])
    if report["unanchored_observation_ids"]:
        lines.extend(["", "Unanchored observations: " + ", ".join(report["unanchored_observation_ids"])])
    lines.extend(
        [
            "",
            "`CANDIDATE_ONLY` edges are excluded. GREMLIN may mine candidate patterns from this report but cannot alter the deterministic frontier.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", type=Path, help="FPDG_INCONSISTENCY_EVIDENCE_V0_1 JSON")
    parser.add_argument("--json", action="store_true", help="print diagnosis JSON")
    args = parser.parse_args()

    try:
        graph = load_graph()
        claims = load_claims()
        evidence = load_evidence(args.evidence)
        report = diagnose(graph, claims, evidence)
        BUILD_DIR.mkdir(exist_ok=True)
        (BUILD_DIR / "INCONSISTENCY_DIAGNOSIS.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        (BUILD_DIR / "INCONSISTENCY_DIAGNOSIS.md").write_text(
            render_markdown(report), encoding="utf-8"
        )
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(
                f"{report['status']}: mode={report['localization_mode']} "
                f"frontier={report['minimal_failing_frontier']}"
            )
        return 0 if report["status"] == "LOCALIZED" else 2
    except (OSError, json.JSONDecodeError, yaml.YAMLError, DiagnosisError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
