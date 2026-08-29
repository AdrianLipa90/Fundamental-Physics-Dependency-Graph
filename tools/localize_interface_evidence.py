#!/usr/bin/env python3
"""Promote explicit interface evidence to exact integration pain coordinates.

An interface failure is not silently projected onto either endpoint claim. The source
receipt may name a registered `interface_id`; this layer verifies that identifier against
the FPDG interface registry, preserves the observation for micro-localization, and adds
an exact integration pain point while leaving claim frontier localization independent.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
INTERFACES_PATH = ROOT / "interfaces" / "cross_repo_interfaces.yaml"


class InterfaceEvidenceError(RuntimeError):
    pass


def load_interfaces(path: Path = INTERFACES_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    if not isinstance(value, dict) or not isinstance(value.get("interfaces"), list):
        raise InterfaceEvidenceError("cross-repository interface registry is invalid")
    return value


def interface_index(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in payload.get("interfaces", []):
        if not isinstance(row, dict):
            raise InterfaceEvidenceError("interface row must be an object")
        interface_id = row.get("interface_id")
        if not isinstance(interface_id, str) or not interface_id:
            raise InterfaceEvidenceError("interface row requires interface_id")
        if interface_id in out:
            raise InterfaceEvidenceError(f"duplicate interface_id {interface_id}")
        out[interface_id] = row
    return out


def explicit_interface_id(observation: dict[str, Any]) -> str | None:
    locator = observation.get("source_locator")
    if locator is None:
        return None
    if not isinstance(locator, dict):
        raise InterfaceEvidenceError("source_locator must be an object")
    value = locator.get("interface_id")
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise InterfaceEvidenceError("source_locator.interface_id must be non-empty string")
    return value


def interface_only_observation(observation: dict[str, Any]) -> bool:
    """True when interface_id is the sole scientific graph anchor in this observation."""
    interface_id = explicit_interface_id(observation)
    if interface_id is None:
        return False
    return not isinstance(observation.get("claim_id"), str) and not isinstance(
        observation.get("edge"), dict
    )


def claim_projection_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    """Remove interface-only observations before claim-frontier localization.

    Their test/source paths must not trigger repository-wide fallback and manufacture a
    claim frontier. They are reattached by `enrich_interface_diagnosis` as exact
    interface observations.
    """
    if evidence.get("schema") != "FPDG_INCONSISTENCY_EVIDENCE_V0_1":
        raise InterfaceEvidenceError("unsupported evidence schema")
    rows = evidence.get("observations")
    if not isinstance(rows, list):
        raise InterfaceEvidenceError("evidence observations must be a list")
    result = copy.deepcopy(evidence)
    result["observations"] = [
        copy.deepcopy(row)
        for row in rows
        if isinstance(row, dict) and not interface_only_observation(row)
    ]
    return result


def _diagnostic_observation(observation: dict[str, Any], interface_id: str) -> dict[str, Any]:
    return {
        "observation_id": observation["observation_id"],
        "kind": observation.get("kind", "CROSS_REPO_CONTRACT_FAILURE"),
        "repository": observation.get("repository"),
        "claim_id": observation.get("claim_id"),
        "edge": observation.get("edge"),
        "source_path": observation.get("source_path"),
        "expected": observation.get("expected"),
        "observed": observation.get("observed"),
        "evidence_refs": observation.get("evidence_refs", []),
        "anchors": [],
        "anchor_method": "EXACT_INTERFACE_CONTRACT",
        "precision": "EXACT_INTERFACE",
        "external_subject": interface_id,
    }


def enrich_interface_diagnosis(
    diagnosis: dict[str, Any],
    evidence: dict[str, Any],
    interfaces_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if diagnosis.get("schema") != "FPDG_INCONSISTENCY_DIAGNOSIS_V0_1":
        raise InterfaceEvidenceError("unsupported diagnosis schema")
    if evidence.get("schema") != "FPDG_INCONSISTENCY_EVIDENCE_V0_1":
        raise InterfaceEvidenceError("unsupported evidence schema")
    interfaces = interface_index(interfaces_payload or load_interfaces())
    result = copy.deepcopy(diagnosis)
    points = list(result.get("integration_pain_points", []))
    diagnostic_rows = list(result.get("observations", []))
    diagnostic_ids = {
        row.get("observation_id")
        for row in diagnostic_rows
        if isinstance(row, dict) and isinstance(row.get("observation_id"), str)
    }
    interface_obs_ids: list[str] = []

    for observation in evidence.get("observations", []):
        if not isinstance(observation, dict):
            raise InterfaceEvidenceError("evidence observation must be an object")
        interface_id = explicit_interface_id(observation)
        if interface_id is None:
            continue
        interface = interfaces.get(interface_id)
        if interface is None:
            raise InterfaceEvidenceError(
                f"explicit interface evidence references unregistered interface {interface_id}"
            )
        obs_id = observation.get("observation_id")
        if not isinstance(obs_id, str) or not obs_id:
            raise InterfaceEvidenceError("interface observation requires observation_id")
        contract = interface.get("contract", {})
        if not isinstance(contract, dict):
            raise InterfaceEvidenceError(f"{interface_id}: contract must be an object")
        candidate_only = contract.get("status") == "CANDIDATE_ONLY"
        point = {
            "location": f"FPDG.INTERFACE.{interface_id}",
            "kind": observation.get("kind", "CROSS_REPO_CONTRACT_FAILURE"),
            "interface_id": interface_id,
            "observation_id": obs_id,
            "repository": observation.get("repository"),
            "upstream_repository": interface.get("upstream_repository"),
            "downstream_repository": interface.get("downstream_repository"),
            "upstream_claim": interface.get("upstream_claim"),
            "downstream_claim": interface.get("downstream_claim"),
            "contract": contract,
            "candidate_interface": candidate_only,
            "canonical_invalidation_allowed": not candidate_only,
            "witness_locations": [
                f"interfaces/cross_repo_interfaces.yaml:{interface_id}",
                f"observation:{obs_id}",
            ],
            "evidence_refs": observation.get("evidence_refs", []),
            "causal_endpoint_projection_performed": False,
        }
        if point not in points:
            points.append(point)
        if obs_id not in diagnostic_ids:
            diagnostic_rows.append(_diagnostic_observation(observation, interface_id))
            diagnostic_ids.add(obs_id)
        interface_obs_ids.append(obs_id)

    result["observations"] = diagnostic_rows
    result["integration_pain_points"] = points
    result["interface_anchored_observation_ids"] = sorted(set(interface_obs_ids))
    if interface_obs_ids:
        unanchored = result.get("unanchored_observation_ids", [])
        if isinstance(unanchored, list):
            result["unanchored_observation_ids"] = sorted(
                value for value in unanchored if value not in set(interface_obs_ids)
            )
        has_claim_frontier = bool(result.get("minimal_failing_frontier"))
        if has_claim_frontier:
            result["localization_mode"] = "EXACT_MIXED_CLAIM_AND_INTERFACE"
        else:
            result["status"] = "LOCALIZED"
            result["localization_mode"] = "EXACT_INTERFACE_CONTRACT"
    return result


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: localize_interface_evidence.py DIAGNOSIS.json EVIDENCE.json", file=sys.stderr)
        return 1
    try:
        diagnosis = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        evidence = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
        report = enrich_interface_diagnosis(diagnosis, evidence)
        print(json.dumps(report, indent=2))
        return 0 if report.get("status") == "LOCALIZED" else 2
    except (OSError, json.JSONDecodeError, InterfaceEvidenceError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
