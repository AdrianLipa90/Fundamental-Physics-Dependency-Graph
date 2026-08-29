#!/usr/bin/env python3
"""Resolve a localized FPDG pain frontier to exact dependency/interface seams.

This layer does not infer physical causation. It takes an already deterministic
FPDG_INCONSISTENCY_DIAGNOSIS_V0_1 and exposes the exact promoted entry/exit seams,
source locations and cross-repository interface contracts that must be probed first.

CANDIDATE_ONLY edges are excluded. Missing cross-repository interface registration is
itself reported as an exact integration pain point rather than silently guessed.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "dependency_graph.yaml"
INTERFACES_PATH = ROOT / "interfaces" / "cross_repo_interfaces.yaml"
BUILD_DIR = ROOT / "build"

PROMOTED = {"CANONICAL", "CANONICAL_CROSS_REPO", "CANONICAL_FRONTIER"}


class SeamError(RuntimeError):
    pass


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    if not isinstance(value, dict):
        raise SeamError(f"{path}: expected mapping")
    return value


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise SeamError(f"{path}: expected JSON object")
    return value


def graph_indexes(graph: dict[str, Any]):
    nodes = {row["claim_id"]: row for row in graph.get("nodes", [])}
    incoming: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    outgoing: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in graph.get("edges", []):
        if edge.get("authority") not in PROMOTED:
            continue
        incoming[edge["to"]].append(edge)
        outgoing[edge["from"]].append(edge)
    return nodes, incoming, outgoing


def interface_index(payload: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    rows = payload.get("interfaces")
    if not isinstance(rows, list):
        raise SeamError("cross_repo_interfaces.yaml: interfaces must be a list")
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise SeamError("interface row must be an object")
        upstream = row.get("upstream_claim")
        downstream = row.get("downstream_claim")
        if not isinstance(upstream, str) or not isinstance(downstream, str):
            raise SeamError("interface requires upstream_claim and downstream_claim")
        key = (upstream, downstream)
        if key in index:
            raise SeamError(f"duplicate interface edge {upstream} -> {downstream}")
        index[key] = row
    return index


def edge_signature(edge: dict[str, Any]) -> tuple[str, str, str]:
    return edge["from"], edge["to"], edge["authority"]


def seam_record(
    edge: dict[str, Any],
    role: str,
    nodes: dict[str, dict[str, Any]],
    interfaces: dict[tuple[str, str], dict[str, Any]],
) -> dict[str, Any]:
    src = edge["from"]
    dst = edge["to"]
    src_repo = nodes[src].get("repository")
    dst_repo = nodes[dst].get("repository")
    cross_repo = src_repo != dst_repo
    interface = interfaces.get((src, dst)) if cross_repo else None

    if cross_repo and interface is None:
        registration = "MISSING_CROSS_REPO_INTERFACE_CONTRACT"
    elif cross_repo:
        registration = "REGISTERED_CROSS_REPO_INTERFACE"
    else:
        registration = "LOCAL_DEPENDENCY_EDGE"

    record: dict[str, Any] = {
        "seam_id": interface.get("interface_id") if interface else f"EDGE.{src}->{dst}",
        "role": role,
        "from": src,
        "to": dst,
        "authority": edge["authority"],
        "from_repository": src_repo,
        "to_repository": dst_repo,
        "scope": "CROSS_REPOSITORY" if cross_repo else "LOCAL_REPOSITORY",
        "registration_status": registration,
        "from_source": nodes[src].get("source"),
        "to_source": nodes[dst].get("source"),
    }
    if interface:
        record["interface_id"] = interface.get("interface_id")
        record["contract"] = interface.get("contract", {})
        record["upstream_repository"] = interface.get("upstream_repository")
        record["downstream_repository"] = interface.get("downstream_repository")
    return record


def dedupe_seams(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str, str]] = set()
    out = []
    for row in rows:
        key = (row["from"], row["to"], row["authority"], row["role"])
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return sorted(out, key=lambda row: (row["role"], row["from"], row["to"]))


def localize(
    diagnosis: dict[str, Any],
    graph: dict[str, Any],
    interfaces_payload: dict[str, Any],
) -> dict[str, Any]:
    if diagnosis.get("schema") != "FPDG_INCONSISTENCY_DIAGNOSIS_V0_1":
        raise SeamError(f"unsupported diagnosis schema {diagnosis.get('schema')!r}")

    nodes, incoming, outgoing = graph_indexes(graph)
    interfaces = interface_index(interfaces_payload)
    zones = []
    all_missing = []

    for zone in diagnosis.get("pain_zones", []):
        frontier = zone.get("frontier_claim")
        if not isinstance(frontier, str) or frontier not in nodes:
            raise SeamError(f"unknown frontier claim {frontier!r}")

        seam_rows: list[dict[str, Any]] = []
        for edge in incoming.get(frontier, []):
            seam_rows.append(seam_record(edge, "ENTRY_TO_FRONTIER", nodes, interfaces))
        for edge in outgoing.get(frontier, []):
            seam_rows.append(seam_record(edge, "EXIT_FROM_FRONTIER", nodes, interfaces))

        # Preserve wider zone boundaries as secondary probes when the witness region is larger
        # than the frontier node itself.
        frontier_sigs = {
            edge_signature(edge)
            for edge in incoming.get(frontier, []) + outgoing.get(frontier, [])
        }
        for edge in zone.get("incoming_boundary_edges", []):
            if edge_signature(edge) not in frontier_sigs:
                seam_rows.append(seam_record(edge, "ZONE_ENTRY_BOUNDARY", nodes, interfaces))
        for edge in zone.get("outgoing_boundary_edges", []):
            if edge_signature(edge) not in frontier_sigs:
                seam_rows.append(seam_record(edge, "ZONE_EXIT_BOUNDARY", nodes, interfaces))

        seams = dedupe_seams(seam_rows)
        missing = [row for row in seams if row["registration_status"] == "MISSING_CROSS_REPO_INTERFACE_CONTRACT"]
        all_missing.extend(missing)

        probe_targets = [
            {
                "kind": "CLAIM_SOURCE",
                "claim_id": frontier,
                "repository": nodes[frontier].get("repository"),
                "source": nodes[frontier].get("source"),
                "status": nodes[frontier].get("status"),
            }
        ]
        for seam in seams:
            target = {
                "kind": "DEPENDENCY_SEAM",
                "seam_id": seam["seam_id"],
                "role": seam["role"],
                "from": seam["from"],
                "to": seam["to"],
                "scope": seam["scope"],
                "registration_status": seam["registration_status"],
            }
            if "interface_id" in seam:
                target["interface_id"] = seam["interface_id"]
                contract = seam.get("contract", {})
                target["contract_status"] = contract.get("status")
                for key in (
                    "relation",
                    "quantity",
                    "validation",
                    "remaining_gate",
                    "executable_interface",
                    "bridge",
                    "bridge_chain",
                    "source",
                    "source_upstream",
                    "source_downstream",
                ):
                    if key in contract:
                        target[key] = contract[key]
            probe_targets.append(target)

        zones.append(
            {
                "frontier_claim": frontier,
                "repository": nodes[frontier].get("repository"),
                "claim_source": nodes[frontier].get("source"),
                "claim_status": nodes[frontier].get("status"),
                "seams": seams,
                "seam_count": len(seams),
                "cross_repo_seam_count": sum(1 for row in seams if row["scope"] == "CROSS_REPOSITORY"),
                "unregistered_cross_repo_seam_count": len(missing),
                "probe_targets": probe_targets,
            }
        )

    integration_targets = []
    for point in diagnosis.get("integration_pain_points", []):
        integration_targets.append(
            {
                "kind": "INTEGRATION_METADATA_LOCATION",
                "location": point.get("location"),
                "repository": point.get("repository"),
                "witness_locations": point.get("witness_locations", []),
                "details": point,
            }
        )

    status = "LOCALIZED"
    if not zones and not integration_targets:
        status = "NO_LOCALIZED_TARGETS"
    elif all_missing:
        status = "LOCALIZED_WITH_UNREGISTERED_CROSS_REPO_SEAMS"

    return {
        "schema": "FPDG_PAIN_SEAM_REPORT_V0_1",
        "status": status,
        "candidate_edges_included": False,
        "source_diagnosis_schema": diagnosis.get("schema"),
        "localization_mode": diagnosis.get("localization_mode"),
        "zones": zones,
        "integration_targets": integration_targets,
        "unregistered_cross_repo_seams": all_missing,
        "gremlin_role": "CONSUME_EXACT_SEAMS_AS_CANDIDATE_PATTERN_CONTEXT_ONLY",
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = ["# FPDG Pain Seam Report", "", f"Status: **{report['status']}**", ""]
    for zone in report.get("zones", []):
        lines.append(f"## `{zone['frontier_claim']}`")
        lines.append("")
        lines.append(f"Claim source: `{zone.get('claim_source')}`")
        lines.append("")
        for seam in zone.get("seams", []):
            lines.append(
                f"- `{seam['role']}` — `{seam['from']} -> {seam['to']}` "
                f"[{seam['authority']}] — {seam['registration_status']}"
            )
            if seam.get("interface_id"):
                lines.append(f"  - interface: `{seam['interface_id']}`")
            contract = seam.get("contract", {})
            if contract.get("remaining_gate"):
                lines.append(f"  - remaining gate: `{contract['remaining_gate']}`")
            if contract.get("validation"):
                lines.append(f"  - validation: `{contract['validation']}`")
        lines.append("")

    for point in report.get("integration_targets", []):
        lines.append(f"- integration target: `{point.get('location')}`")

    lines.extend(
        [
            "",
            "This report identifies deterministic probe coordinates. It does not promote a causal explanation.",
            "GREMLIN may compare these seams with prior relational failure shapes only as CANDIDATE_ONLY context.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("diagnosis", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        diagnosis = load_json(args.diagnosis)
        report = localize(diagnosis, load_yaml(GRAPH_PATH), load_yaml(INTERFACES_PATH))
        BUILD_DIR.mkdir(exist_ok=True)
        (BUILD_DIR / "PAIN_SEAM_REPORT.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        (BUILD_DIR / "PAIN_SEAM_REPORT.md").write_text(render_markdown(report), encoding="utf-8")
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(
                f"{report['status']}: zones={len(report['zones'])} "
                f"integration_targets={len(report['integration_targets'])} "
                f"unregistered_cross_repo_seams={len(report['unregistered_cross_repo_seams'])}"
            )
        return 0 if report["status"] != "NO_LOCALIZED_TARGETS" else 2
    except (OSError, json.JSONDecodeError, yaml.YAMLError, SeamError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
