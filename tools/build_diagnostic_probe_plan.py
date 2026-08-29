#!/usr/bin/env python3
"""Build a deterministic probe order for an already localized FPDG inconsistency.

The plan answers "what exact coordinate should be inspected first?" without assigning
causal probabilities. Directly observed sub-claim coordinates outrank inferred seam and
claim-source probes. Historical GREMLIN recurrence matches are appended only as
CANDIDATE_ONLY hints and never outrank deterministic coordinates.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build"


class ProbePlanError(RuntimeError):
    pass


MICRO_PRIORITY = {
    "SOURCE_RANGE": 0,
    "EQUATION": 1,
    "SYMBOL": 2,
    "VALIDATOR_OR_TEST": 3,
    "RECEIPT": 4,
    "INTERFACE_CONTRACT": 5,
    "SOURCE_PATH": 6,
    "CLAIM": 7,
    "UNSPECIFIED": 8,
}

SEAM_PRIORITY = {
    "ENTRY_TO_FRONTIER": 10,
    "ZONE_ENTRY_BOUNDARY": 11,
    "EXIT_FROM_FRONTIER": 20,
    "ZONE_EXIT_BOUNDARY": 21,
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise ProbePlanError(f"{path}: expected JSON object")
    return value


def validate_inputs(
    seam_report: dict[str, Any],
    micro_report: dict[str, Any],
    matches: dict[str, Any] | None,
) -> None:
    if seam_report.get("schema") != "FPDG_PAIN_SEAM_REPORT_V0_1":
        raise ProbePlanError("unsupported seam report schema")
    if micro_report.get("schema") != "FPDG_PAIN_MICRO_COORDINATES_V0_1":
        raise ProbePlanError("unsupported micro-coordinate schema")
    if micro_report.get("causal_inference_performed") is not False:
        raise ProbePlanError("micro-coordinate input must remain non-causal")
    if micro_report.get("candidate_edges_included") is not False:
        raise ProbePlanError("micro-coordinate input must exclude candidate edges")
    if matches is not None and matches.get("schema") != "FPDG_PAIN_SIGNATURE_MATCHES_V0_1":
        raise ProbePlanError("unsupported incident match schema")


def micro_probe(row: dict[str, Any]) -> dict[str, Any]:
    precision = row.get("precision", "UNSPECIFIED")
    return {
        "probe_id": f"PROBE.{row['coordinate_id']}",
        "kind": "OBSERVED_EVIDENCE_COORDINATE",
        "priority": MICRO_PRIORITY.get(precision, 8),
        "authority": "DETERMINISTIC_DIAGNOSTIC_COORDINATE",
        "precision": precision,
        "coordinate_id": row["coordinate_id"],
        "repository": row.get("repository"),
        "claim_id": row.get("claim_id"),
        "anchored_claims": row.get("anchored_claims", []),
        "source_locator": row.get("source_locator", {}),
        "evidence_refs": row.get("evidence_refs", []),
        "reason": "directly observed evidence coordinate; inspect before broader dependency probes",
    }


def seam_probe(row: dict[str, Any]) -> dict[str, Any]:
    role = row.get("role", "UNKNOWN")
    registration = row.get("registration_status")
    reason = "probe promoted dependency seam adjacent to the localized frontier"
    if role in {"ENTRY_TO_FRONTIER", "ZONE_ENTRY_BOUNDARY"}:
        reason = "probe the promoted dependency seam entering the localized failing region"
    elif role in {"EXIT_FROM_FRONTIER", "ZONE_EXIT_BOUNDARY"}:
        reason = "probe the promoted seam carrying the localized failure toward downstream symptoms"
    if registration == "MISSING_CROSS_REPO_INTERFACE_CONTRACT":
        reason += "; cross-repository interface registration is missing"

    return {
        "probe_id": f"PROBE.SEAM.{row['seam_id']}.{role}",
        "kind": "DEPENDENCY_SEAM",
        "priority": SEAM_PRIORITY.get(role, 25),
        "authority": "DETERMINISTIC_DIAGNOSTIC_COORDINATE",
        "seam_id": row.get("seam_id"),
        "role": role,
        "from": row.get("from"),
        "to": row.get("to"),
        "scope": row.get("scope"),
        "registration_status": registration,
        "interface_id": row.get("interface_id"),
        "contract": row.get("contract", {}),
        "reason": reason,
    }


def claim_probe(zone: dict[str, Any]) -> dict[str, Any]:
    return {
        "probe_id": f"PROBE.CLAIM.{zone['frontier_claim']}",
        "kind": "FRONTIER_CLAIM_SOURCE",
        "priority": 15,
        "authority": "DETERMINISTIC_DIAGNOSTIC_COORDINATE",
        "frontier_claim": zone["frontier_claim"],
        "repository": zone.get("repository"),
        "claim_source": zone.get("claim_source"),
        "claim_status": zone.get("claim_status"),
        "reason": "inspect the localized frontier claim source after any finer direct evidence coordinate",
    }


def integration_probe(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "probe_id": f"PROBE.{row['coordinate_id']}",
        "kind": "INTEGRATION_METADATA_LOCATION",
        "priority": 0,
        "authority": "DETERMINISTIC_DIAGNOSTIC_COORDINATE",
        "coordinate_id": row["coordinate_id"],
        "location": row.get("location"),
        "repository": row.get("repository"),
        "witness_locations": row.get("witness_locations", []),
        "reason": "exact integration-layer coordinate; inspect before projecting failure onto scientific claims",
    }


def dedupe_and_sort(probes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    out = []
    for row in probes:
        key = row["probe_id"]
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return sorted(out, key=lambda row: (row["priority"], row["probe_id"]))


def build_plan(
    seam_report: dict[str, Any],
    micro_report: dict[str, Any],
    matches: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_inputs(seam_report, micro_report, matches)

    coords_by_id = {
        row["coordinate_id"]: row
        for row in micro_report.get("coordinates", [])
        if isinstance(row, dict) and isinstance(row.get("coordinate_id"), str)
    }
    micro_zone_by_frontier = {
        row["frontier_claim"]: row
        for row in micro_report.get("zones", [])
        if isinstance(row, dict) and isinstance(row.get("frontier_claim"), str)
    }

    zones = []
    for seam_zone in seam_report.get("zones", []):
        frontier = seam_zone.get("frontier_claim")
        if not isinstance(frontier, str):
            raise ProbePlanError("seam zone requires frontier_claim")
        probes = []

        micro_zone = micro_zone_by_frontier.get(frontier, {})
        for coordinate_id in micro_zone.get("coordinate_ids", []):
            coordinate = coords_by_id.get(coordinate_id)
            if coordinate is None:
                raise ProbePlanError(
                    f"micro zone {frontier} references unknown coordinate {coordinate_id}"
                )
            probes.append(micro_probe(coordinate))

        for seam in seam_zone.get("seams", []):
            if not isinstance(seam, dict) or not isinstance(seam.get("seam_id"), str):
                raise ProbePlanError(f"invalid seam in zone {frontier}")
            probes.append(seam_probe(seam))

        probes.append(claim_probe(seam_zone))
        probes = dedupe_and_sort(probes)
        zones.append(
            {
                "frontier_claim": frontier,
                "probes": probes,
                "first_probe": probes[0] if probes else None,
                "causal_root_asserted": False,
            }
        )

    integration_probes = dedupe_and_sort(
        [
            integration_probe(row)
            for row in micro_report.get("integration_coordinates", [])
            if isinstance(row, dict) and isinstance(row.get("coordinate_id"), str)
        ]
    )

    gremlin_hints = []
    if matches is not None:
        for index, row in enumerate(matches.get("matches", []), 1):
            if not isinstance(row, dict):
                continue
            gremlin_hints.append(
                {
                    "hint_id": f"GREMLIN.RECURRENCE.{index:03d}",
                    "kind": "INCIDENT_RECURRENCE_CANDIDATE",
                    "authority": "CANDIDATE_ONLY",
                    "incident_path": row.get("incident_path"),
                    "signature_hash": row.get("signature_hash"),
                    "exact_structural_match": row.get("exact_structural_match", False),
                    "feature_jaccard": row.get("feature_jaccard"),
                    "exact_coordinates": row.get("exact_coordinates", {}),
                    "incident_review": row.get("incident_review"),
                    "reason": "historical structural recurrence may guide GREMLIN candidate search but cannot outrank deterministic current-incident coordinates",
                }
            )

    total = sum(len(zone["probes"]) for zone in zones) + len(integration_probes)
    return {
        "schema": "FPDG_DIAGNOSTIC_PROBE_PLAN_V0_1",
        "status": "READY" if total else "NO_PROBES",
        "causal_inference_performed": False,
        "candidate_edges_included": False,
        "zones": zones,
        "integration_probes": integration_probes,
        "gremlin_hints": gremlin_hints,
        "ordering_rule": (
            "direct observed micro-coordinate > entering promoted seam > frontier claim source > "
            "outgoing promoted seam; GREMLIN incident recurrence is candidate-only context"
        ),
    }


def render_markdown(plan: dict[str, Any]) -> str:
    lines = ["# FPDG Diagnostic Probe Plan", "", f"Status: **{plan['status']}**", ""]
    for zone in plan.get("zones", []):
        lines.append(f"## `{zone['frontier_claim']}`")
        lines.append("")
        first = zone.get("first_probe")
        if first:
            lines.append(f"First deterministic probe: `{first['probe_id']}`")
            lines.append("")
        for row in zone.get("probes", []):
            lines.append(
                f"- P{row['priority']:02d} `{row['probe_id']}` — {row['kind']}"
            )
            lines.append(f"  - {row['reason']}")
        lines.append("")
    for row in plan.get("integration_probes", []):
        lines.append(f"- P{row['priority']:02d} `{row['probe_id']}` — integration coordinate")
        lines.append(f"  - {row['reason']}")
    if plan.get("gremlin_hints"):
        lines.extend(["", "## GREMLIN recurrence hints", ""])
        for row in plan["gremlin_hints"]:
            lines.append(
                f"- `{row['hint_id']}` — exact={row['exact_structural_match']} "
                f"Jaccard={row.get('feature_jaccard')} — CANDIDATE_ONLY"
            )
    lines.extend(
        [
            "",
            "Probe order is deterministic diagnostic ordering, not a causal probability ranking.",
            "Historical recurrence never overrides current evidence coordinates.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("seams", type=Path)
    parser.add_argument("micro", type=Path)
    parser.add_argument("--matches", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        plan = build_plan(
            load_json(args.seams),
            load_json(args.micro),
            load_json(args.matches) if args.matches else None,
        )
        BUILD_DIR.mkdir(exist_ok=True)
        (BUILD_DIR / "DIAGNOSTIC_PROBE_PLAN.json").write_text(
            json.dumps(plan, indent=2) + "\n", encoding="utf-8"
        )
        (BUILD_DIR / "DIAGNOSTIC_PROBE_PLAN.md").write_text(
            render_markdown(plan), encoding="utf-8"
        )
        if args.json:
            print(json.dumps(plan, indent=2))
        else:
            print(
                f"{plan['status']}: zones={len(plan['zones'])} "
                f"integration={len(plan['integration_probes'])} "
                f"gremlin_hints={len(plan['gremlin_hints'])}"
            )
        return 0 if plan["status"] == "READY" else 2
    except (OSError, json.JSONDecodeError, ProbePlanError, KeyError, TypeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
