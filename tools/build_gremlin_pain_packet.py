#!/usr/bin/env python3
"""Convert an exact FPDG diagnosis into a GREMLIN candidate-mining request.

This adapter deliberately stops before KAKU/RADICAL/PNV compilation. FPDG claim IDs are
not silently reinterpreted as PNCS KAKU atoms and no 36D vectors are fabricated. The
new GREMLIN may use the packet to search for recurring relational failure patterns, but
explicit cross-domain alignment and canonical KAKU resolution remain mandatory gates.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build"


class PacketError(RuntimeError):
    pass


def load_diagnosis(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise PacketError("diagnosis must be a JSON object")
    if value.get("schema") != "FPDG_INCONSISTENCY_DIAGNOSIS_V0_1":
        raise PacketError(f"unsupported diagnosis schema {value.get('schema')!r}")
    return value


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)


def required_gates() -> dict[str, bool]:
    return {
        "explicit_cross_domain_alignment": True,
        "canonical_kaku_resolution": True,
        "single_exact_36d_basis": True,
        "unknown_relation_binding_fail_closed": True,
    }


def build_packet(diagnosis: dict[str, Any]) -> dict[str, Any]:
    zones = []
    integration_zones = []
    observations_by_id = {
        row["observation_id"]: row for row in diagnosis.get("observations", [])
    }

    for index, zone in enumerate(diagnosis.get("pain_zones", []), 1):
        frontier = zone["frontier_claim"]
        witness_paths = zone.get("witness_paths", [])
        domains = sorted(
            {
                row.get("repository")
                for row in diagnosis.get("observations", [])
                if row.get("observation_id") in zone.get("observation_ids", [])
                and isinstance(row.get("repository"), str)
            }
            | ({zone.get("repository")} if isinstance(zone.get("repository"), str) else set())
        )

        raw_chains = []
        for path_index, path in enumerate(witness_paths, 1):
            raw_chains.append(
                {
                    "chain_id": f"FPDG.PAIN.{index:03d}.PATH.{path_index:03d}",
                    "source": "FPDG_PROMOTED_DEPENDENCY_WITNESS",
                    "status": "OBSERVED_DIAGNOSTIC_WITNESS",
                    "claims": path,
                }
            )
        if not raw_chains:
            raw_chains.append(
                {
                    "chain_id": f"FPDG.PAIN.{index:03d}.FRONTIER",
                    "source": "FPDG_PROMOTED_DEPENDENCY_WITNESS",
                    "status": "OBSERVED_DIAGNOSTIC_WITNESS",
                    "claims": [frontier],
                }
            )

        evidence_refs = []
        for obs_id in zone.get("observation_ids", []):
            obs = observations_by_id.get(obs_id, {})
            evidence_refs.extend(obs.get("evidence_refs", []))
            evidence_refs.append(f"observation:{obs_id}")

        zones.append(
            {
                "finding_request_id": f"FPDG.GREMLIN.PAIN.{safe_id(frontier)}",
                "invariant_id": "MINIMAL_PROMOTED_DEPENDENCY_FAILURE_FRONTIER",
                "invariant_description": (
                    "Search for recurring relational structures that place observed failures "
                    "behind the same minimal promoted dependency frontier or interface seam."
                ),
                "frontier_claim": frontier,
                "domains": domains,
                "raw_chains": raw_chains,
                "incoming_boundary_edges": zone.get("incoming_boundary_edges", []),
                "outgoing_boundary_edges": zone.get("outgoing_boundary_edges", []),
                "evidence_refs": sorted(set(evidence_refs)),
                "required_gates": required_gates(),
                "compiler_state": "BLOCKED_PENDING_GREMLIN_ALIGNMENT_AND_KAKU_RESOLUTION",
            }
        )

    for index, point in enumerate(diagnosis.get("integration_pain_points", []), 1):
        location = point["location"]
        integration_zones.append(
            {
                "finding_request_id": f"FPDG.GREMLIN.INTEGRATION.{safe_id(location)}",
                "invariant_id": "EXACT_INTEGRATION_CONSISTENCY_LOCATION",
                "invariant_description": (
                    "Search prior incidents for the same integration-layer mismatch shape "
                    "without projecting it onto scientific claims unless evidence establishes that link."
                ),
                "frontier_location": location,
                "repository": point.get("repository"),
                "kind": point.get("kind"),
                "details": point,
                "raw_chains": [
                    {
                        "chain_id": f"FPDG.INTEGRATION.PAIN.{index:03d}",
                        "source": "FPDG_INTEGRATION_DIAGNOSTIC_WITNESS",
                        "status": "OBSERVED_DIAGNOSTIC_WITNESS",
                        "locations": point.get("witness_locations", [location]),
                    }
                ],
                "required_gates": required_gates(),
                "compiler_state": "BLOCKED_PENDING_GREMLIN_ALIGNMENT_AND_KAKU_RESOLUTION",
            }
        )

    return {
        "schema": "FPDG_GREMLIN_PAIN_PACKET_V0_1",
        "source_diagnosis_schema": diagnosis.get("schema"),
        "epistemic": "CHYBA",
        "promotion_state": "CANDIDATE_ONLY",
        "runtime_execution_authority": False,
        "canon_write_authority": False,
        "vector_guessing_allowed": False,
        "candidate_edges_enter_canon": False,
        "gremlin_contract": {
            "relation_mining_adapter": "PNCS_GREMLIN_RELATION_MINING_ADAPTER_V0_1",
            "relational_compiler": "PNCS_GREMLIN_RELATIONAL_ISOMORPHISM_COMPILER_V0_1",
            "lowering_path": [
                "GREMLIN explicit finding/alignment",
                "canonical KAKU resolver",
                "RelationalIsomorphism",
                "RADICAL",
                "native PNV OPERATORS",
                "PNV candidate program",
            ],
        },
        "diagnosis_status": diagnosis.get("status"),
        "localization_mode": diagnosis.get("localization_mode"),
        "zones": zones,
        "integration_zones": integration_zones,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("diagnosis", type=Path, help="FPDG_INCONSISTENCY_DIAGNOSIS_V0_1 JSON")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        diagnosis = load_diagnosis(args.diagnosis)
        packet = build_packet(diagnosis)
        BUILD_DIR.mkdir(exist_ok=True)
        output = BUILD_DIR / "GREMLIN_PAIN_PACKET.json"
        output.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(packet, indent=2))
        else:
            print(
                f"PASS: GREMLIN candidate packet claim_zones={len(packet['zones'])} "
                f"integration_zones={len(packet['integration_zones'])}; "
                "KAKU/36D compilation remains gated"
            )
        return 0
    except (OSError, json.JSONDecodeError, PacketError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
