#!/usr/bin/env python3
"""Build a repository-agnostic relational signature for a localized FPDG incident.

The signature intentionally separates exact coordinates from structural features. Exact
claim IDs, seam IDs and source locations remain available for repair/provenance, while
the hashed structural signature lets GREMLIN compare failure shapes across repositories
without pretending that name similarity is an isomorphism.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build"


class SignatureError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise SignatureError(f"{path}: expected JSON object")
    return value


def classify_status(value: Any) -> str:
    if not isinstance(value, str):
        return "UNKNOWN"
    status = value.upper()
    if "FIREWALL" in status or "REJECTED" in status:
        return "FIREWALL"
    if "OPEN" in status or "FRONTIER" in status or "ACTIVE_RECONCILIATION" in status:
        return "FRONTIER_OR_OPEN"
    if "CANDIDATE" in status or "CHYBA" in status:
        return "CANDIDATE"
    if "PASS" in status or "CLOSED" in status or "CANONICAL" in status or "ADMITTED" in status:
        return "PROMOTED_OR_PASS"
    return "OTHER"


def counter_dict(values: list[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def structural_zone(zone: dict[str, Any], seam_zone: dict[str, Any]) -> dict[str, Any]:
    witness_lengths = sorted(len(path) for path in zone.get("witness_paths", []) if isinstance(path, list))
    seams = seam_zone.get("seams", []) if isinstance(seam_zone, dict) else []
    seam_roles = [row.get("role", "UNKNOWN") for row in seams if isinstance(row, dict)]
    seam_scopes = [row.get("scope", "UNKNOWN") for row in seams if isinstance(row, dict)]
    seam_authorities = [row.get("authority", "UNKNOWN") for row in seams if isinstance(row, dict)]
    registration_states = [
        row.get("registration_status", "UNKNOWN") for row in seams if isinstance(row, dict)
    ]

    contract_features: list[str] = []
    for seam in seams:
        if not isinstance(seam, dict):
            continue
        contract = seam.get("contract")
        if not isinstance(contract, dict):
            continue
        for key in sorted(contract):
            if key in {
                "status",
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
            }:
                contract_features.append(key)

    return {
        "frontier_status_class": classify_status(zone.get("status") or seam_zone.get("claim_status")),
        "symptom_anchor_count": len(zone.get("symptom_anchors", [])),
        "witness_path_lengths": witness_lengths,
        "downstream_revalidation_count": int(zone.get("downstream_revalidation_count", 0)),
        "seam_roles": counter_dict(seam_roles),
        "seam_scopes": counter_dict(seam_scopes),
        "seam_authorities": counter_dict(seam_authorities),
        "seam_registration_states": counter_dict(registration_states),
        "contract_feature_keys": counter_dict(contract_features),
    }


def feature_tokens(structure: dict[str, Any]) -> list[str]:
    tokens: list[str] = []
    tokens.append(f"localization_mode={structure.get('localization_mode')}")
    tokens.append(f"zone_count={len(structure.get('zones', []))}")
    tokens.append(f"integration_kind_count={len(structure.get('integration_kinds', []))}")
    for kind in structure.get("integration_kinds", []):
        tokens.append(f"integration.kind={kind}")

    for zone in structure.get("zones", []):
        tokens.append(f"zone.status={zone['frontier_status_class']}")
        tokens.append(f"zone.symptoms={zone['symptom_anchor_count']}")
        tokens.append(f"zone.downstream={zone['downstream_revalidation_count']}")
        for length in zone.get("witness_path_lengths", []):
            tokens.append(f"zone.witness_length={length}")
        for field in (
            "seam_roles",
            "seam_scopes",
            "seam_authorities",
            "seam_registration_states",
            "contract_feature_keys",
        ):
            for key, count in zone.get(field, {}).items():
                tokens.append(f"zone.{field}.{key}={count}")
    return sorted(tokens)


def build_signature(
    diagnosis: dict[str, Any], seam_report: dict[str, Any]
) -> dict[str, Any]:
    if diagnosis.get("schema") != "FPDG_INCONSISTENCY_DIAGNOSIS_V0_1":
        raise SignatureError("unsupported diagnosis schema")
    if seam_report.get("schema") != "FPDG_PAIN_SEAM_REPORT_V0_1":
        raise SignatureError("unsupported seam report schema")

    seam_by_frontier = {
        row["frontier_claim"]: row
        for row in seam_report.get("zones", [])
        if isinstance(row, dict) and isinstance(row.get("frontier_claim"), str)
    }
    zones = []
    exact_frontiers = []
    exact_seams = []
    for zone in diagnosis.get("pain_zones", []):
        frontier = zone.get("frontier_claim")
        if not isinstance(frontier, str):
            continue
        exact_frontiers.append(frontier)
        seam_zone = seam_by_frontier.get(frontier, {})
        zones.append(structural_zone(zone, seam_zone))
        exact_seams.extend(
            row.get("seam_id")
            for row in seam_zone.get("seams", [])
            if isinstance(row, dict) and isinstance(row.get("seam_id"), str)
        )

    integration_kinds = sorted(
        {
            point.get("kind", "UNKNOWN")
            for point in diagnosis.get("integration_pain_points", [])
            if isinstance(point, dict)
        }
    )
    structure = {
        "localization_mode": diagnosis.get("localization_mode"),
        "candidate_edges_included": False,
        "zones": zones,
        "integration_kinds": integration_kinds,
    }
    canonical = json.dumps(structure, sort_keys=True, separators=(",", ":"))
    signature_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    tokens = feature_tokens(structure)

    return {
        "schema": "FPDG_PAIN_SIGNATURE_V0_1",
        "signature_hash": signature_hash,
        "hash_basis": "repository_agnostic_structural_signature",
        "candidate_edges_included": False,
        "structural_signature": structure,
        "feature_tokens": tokens,
        "exact_coordinates": {
            "frontier_claims": sorted(set(exact_frontiers)),
            "seam_ids": sorted(set(exact_seams)),
            "integration_locations": sorted(
                {
                    point.get("location")
                    for point in diagnosis.get("integration_pain_points", [])
                    if isinstance(point, dict) and isinstance(point.get("location"), str)
                }
            ),
        },
        "gremlin_use": "INCIDENT_SHAPE_RETRIEVAL_ONLY",
        "promotion_state": "CANDIDATE_ONLY",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("diagnosis", type=Path)
    parser.add_argument("seams", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        signature = build_signature(load_json(args.diagnosis), load_json(args.seams))
        BUILD_DIR.mkdir(exist_ok=True)
        output = BUILD_DIR / "PAIN_SIGNATURE.json"
        output.write_text(json.dumps(signature, indent=2) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(signature, indent=2))
        else:
            print(
                f"PASS: pain signature {signature['signature_hash']} "
                f"features={len(signature['feature_tokens'])}"
            )
        return 0
    except (OSError, json.JSONDecodeError, SignatureError, KeyError, TypeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
