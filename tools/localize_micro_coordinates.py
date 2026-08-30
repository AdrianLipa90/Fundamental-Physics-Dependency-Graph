#!/usr/bin/env python3
"""Resolve FPDG pain zones to sub-claim source coordinates.

This layer consumes the original structured evidence plus the deterministic diagnosis.
It preserves exact line/equation/symbol/validator/receipt/interface coordinates when
available and never invents a finer location than the evidence supports. Integration-
only diagnoses may carry the exact source/test locator that observed the integration
failure without projecting the failure onto scientific endpoint claims.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build"


class MicroLocalizationError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise MicroLocalizationError(f"{path}: expected JSON object")
    return value


def normalize_locator(observation: dict[str, Any]) -> dict[str, Any]:
    raw = observation.get("source_locator")
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise MicroLocalizationError("source_locator must be an object")

    allowed = {
        "path",
        "symbol",
        "equation_id",
        "line_start",
        "line_end",
        "validator_id",
        "test_id",
        "receipt_ref",
        "interface_id",
    }
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise MicroLocalizationError(f"source_locator has unknown fields: {unknown}")

    locator = {key: raw[key] for key in allowed if key in raw}
    source_path = observation.get("source_path")
    locator_path = locator.get("path")
    if source_path is not None and not isinstance(source_path, str):
        raise MicroLocalizationError("source_path must be a string")
    if locator_path is not None and not isinstance(locator_path, str):
        raise MicroLocalizationError("source_locator.path must be a string")
    if source_path and locator_path and source_path != locator_path:
        raise MicroLocalizationError(
            f"source_path and source_locator.path disagree: {source_path!r} != {locator_path!r}"
        )
    if source_path and not locator_path:
        locator["path"] = source_path

    for key in ("symbol", "equation_id", "validator_id", "test_id", "receipt_ref", "interface_id"):
        value = locator.get(key)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise MicroLocalizationError(f"source_locator.{key} must be a non-empty string")

    line_start = locator.get("line_start")
    line_end = locator.get("line_end")
    for key, value in (("line_start", line_start), ("line_end", line_end)):
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 1):
            raise MicroLocalizationError(f"source_locator.{key} must be a positive integer")
    if line_end is not None and line_start is None:
        raise MicroLocalizationError("source_locator.line_end requires line_start")
    if line_start is not None and line_end is not None and line_end < line_start:
        raise MicroLocalizationError("source_locator line_end precedes line_start")

    return locator


def precision_level(locator: dict[str, Any], claim_id: str | None) -> str:
    if "line_start" in locator:
        return "SOURCE_RANGE"
    if "equation_id" in locator:
        return "EQUATION"
    if "symbol" in locator:
        return "SYMBOL"
    if "validator_id" in locator or "test_id" in locator:
        return "VALIDATOR_OR_TEST"
    if "receipt_ref" in locator:
        return "RECEIPT"
    if "interface_id" in locator:
        return "INTERFACE_CONTRACT"
    if "path" in locator:
        return "SOURCE_PATH"
    if claim_id:
        return "CLAIM"
    return "UNSPECIFIED"


def _diagnosis_observation_index(diagnosis: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = diagnosis.get("observations", [])
    if not isinstance(rows, list):
        raise MicroLocalizationError("diagnosis observations must be a list")
    out = {}
    for row in rows:
        if not isinstance(row, dict):
            raise MicroLocalizationError("diagnosis observation must be an object")
        obs_id = row.get("observation_id")
        if not isinstance(obs_id, str) or not obs_id:
            raise MicroLocalizationError("diagnosis observation_id missing")
        if obs_id in out:
            raise MicroLocalizationError(f"duplicate diagnosis observation_id: {obs_id}")
        out[obs_id] = row
    return out


def _evidence_observation_index(evidence: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if evidence.get("schema") != "FPDG_INCONSISTENCY_EVIDENCE_V0_1":
        raise MicroLocalizationError(f"unsupported evidence schema {evidence.get('schema')!r}")
    rows = evidence.get("observations")
    if not isinstance(rows, list) or not rows:
        raise MicroLocalizationError("evidence observations must be a non-empty list")
    out = {}
    for row in rows:
        if not isinstance(row, dict):
            raise MicroLocalizationError("evidence observation must be an object")
        obs_id = row.get("observation_id")
        if not isinstance(obs_id, str) or not obs_id:
            raise MicroLocalizationError("evidence observation_id missing")
        if obs_id in out:
            raise MicroLocalizationError(f"duplicate evidence observation_id: {obs_id}")
        out[obs_id] = row
    return out


def integration_coordinates(
    diagnosis: dict[str, Any],
    evidence_by_id: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    rows = []
    evidence_by_id = evidence_by_id or {}
    for index, point in enumerate(diagnosis.get("integration_pain_points", []), 1):
        if not isinstance(point, dict):
            raise MicroLocalizationError("integration pain point must be an object")
        location = point.get("location")
        if not isinstance(location, str) or not location:
            raise MicroLocalizationError("integration pain point requires location")
        obs_id = point.get("observation_id")
        source_locator: dict[str, Any] = {}
        evidence_refs = list(point.get("evidence_refs", []))
        if isinstance(obs_id, str) and obs_id in evidence_by_id:
            source_locator = normalize_locator(evidence_by_id[obs_id])
            evidence_refs = sorted(
                set(evidence_refs)
                | {
                    ref
                    for ref in evidence_by_id[obs_id].get("evidence_refs", [])
                    if isinstance(ref, str)
                }
            )
        precision = (
            precision_level(source_locator, None)
            if source_locator
            else "INTEGRATION_METADATA_LOCATION"
        )
        rows.append(
            {
                "coordinate_id": f"MICRO.INTEGRATION.{index:03d}",
                "observation_id": obs_id,
                "location": location,
                "kind": point.get("kind"),
                "repository": point.get("repository"),
                "interface_id": point.get("interface_id"),
                "precision": precision,
                "source_locator": source_locator,
                "witness_locations": point.get("witness_locations", []),
                "evidence_refs": evidence_refs,
                "causal_endpoint_projection_performed": point.get(
                    "causal_endpoint_projection_performed", False
                ),
            }
        )
    return rows


def localize(
    diagnosis: dict[str, Any], evidence: dict[str, Any] | None = None
) -> dict[str, Any]:
    if diagnosis.get("schema") != "FPDG_INCONSISTENCY_DIAGNOSIS_V0_1":
        raise MicroLocalizationError(f"unsupported diagnosis schema {diagnosis.get('schema')!r}")

    diagnosed = _diagnosis_observation_index(diagnosis)
    if diagnosed and evidence is None:
        raise MicroLocalizationError("claim/interface diagnosis requires original inconsistency evidence")
    if evidence is None:
        observed: dict[str, dict[str, Any]] = {}
        source_evidence_schema = None
    else:
        observed = _evidence_observation_index(evidence)
        source_evidence_schema = evidence.get("schema")

    missing = sorted(set(diagnosed) - set(observed))
    if missing:
        raise MicroLocalizationError(f"diagnosis references observations absent from evidence: {missing}")

    coordinates = []
    coordinate_by_obs: dict[str, dict[str, Any]] = {}
    for obs_id in sorted(diagnosed):
        drow = diagnosed[obs_id]
        erow = observed[obs_id]
        locator = normalize_locator(erow)
        anchors = drow.get("anchors", [])
        if not isinstance(anchors, list):
            raise MicroLocalizationError(f"diagnosis observation {obs_id} anchors must be a list")
        claim_id = erow.get("claim_id") if isinstance(erow.get("claim_id"), str) else None
        coordinate = {
            "coordinate_id": f"MICRO.{obs_id}",
            "observation_id": obs_id,
            "kind": erow.get("kind"),
            "repository": erow.get("repository"),
            "claim_id": claim_id,
            "anchored_claims": anchors,
            "source_locator": locator,
            "precision": precision_level(locator, claim_id or (anchors[0] if len(anchors) == 1 else None)),
            "expected": erow.get("expected"),
            "observed": erow.get("observed"),
            "evidence_refs": erow.get("evidence_refs", []),
        }
        coordinates.append(coordinate)
        coordinate_by_obs[obs_id] = coordinate

    zones = []
    used_coordinate_ids: set[str] = set()
    for zone in diagnosis.get("pain_zones", []):
        if not isinstance(zone, dict):
            raise MicroLocalizationError("pain zone must be an object")
        frontier = zone.get("frontier_claim")
        obs_ids = zone.get("observation_ids", [])
        if not isinstance(obs_ids, list):
            raise MicroLocalizationError("pain zone observation_ids must be a list")
        zone_coordinates = []
        for obs_id in obs_ids:
            if obs_id not in coordinate_by_obs:
                raise MicroLocalizationError(f"pain zone references unknown observation: {obs_id}")
            coord = coordinate_by_obs[obs_id]
            zone_coordinates.append(coord["coordinate_id"])
            used_coordinate_ids.add(coord["coordinate_id"])
        zones.append(
            {
                "frontier_claim": frontier,
                "coordinate_ids": sorted(set(zone_coordinates)),
                "finest_precision": finest_precision(
                    [coordinate_by_obs[obs_id]["precision"] for obs_id in obs_ids]
                ),
            }
        )

    integration_rows = integration_coordinates(diagnosis, observed)
    integration_observation_ids = {
        row.get("observation_id")
        for row in integration_rows
        if isinstance(row.get("observation_id"), str)
    }
    unassigned = sorted(
        coord["coordinate_id"]
        for coord in coordinates
        if coord["coordinate_id"] not in used_coordinate_ids
        and coord.get("observation_id") not in integration_observation_ids
    )
    precisions = [coord["precision"] for coord in coordinates]
    precisions.extend(point["precision"] for point in integration_rows)

    return {
        "schema": "FPDG_PAIN_MICRO_COORDINATES_V0_1",
        "status": "LOCALIZED" if coordinates or integration_rows else "NO_COORDINATES",
        "source_diagnosis_schema": diagnosis.get("schema"),
        "source_evidence_schema": source_evidence_schema,
        "finest_precision": finest_precision(precisions),
        "coordinates": coordinates,
        "zones": zones,
        "integration_coordinates": integration_rows,
        "unassigned_coordinate_ids": unassigned,
        "causal_inference_performed": False,
        "candidate_edges_included": False,
    }


_PRECISION_ORDER = {
    "UNSPECIFIED": 0,
    "CLAIM": 1,
    "SOURCE_PATH": 2,
    "RECEIPT": 3,
    "INTERFACE_CONTRACT": 4,
    "INTEGRATION_METADATA_LOCATION": 4,
    "VALIDATOR_OR_TEST": 5,
    "SYMBOL": 6,
    "EQUATION": 7,
    "SOURCE_RANGE": 8,
}


def finest_precision(values: list[str]) -> str:
    if not values:
        return "UNSPECIFIED"
    return max(values, key=lambda value: _PRECISION_ORDER.get(value, -1))


def render_markdown(report: dict[str, Any]) -> str:
    lines = ["# FPDG Pain Micro-Coordinates", "", f"Status: **{report['status']}**", ""]
    lines.append(f"Finest observed coordinate: **{report['finest_precision']}**")
    lines.append("")
    for coordinate in report.get("coordinates", []):
        locator = coordinate.get("source_locator", {})
        target = locator.get("path") or coordinate.get("claim_id") or coordinate.get("anchored_claims")
        lines.append(
            f"- `{coordinate['coordinate_id']}` — `{coordinate['precision']}` — `{target}`"
        )
        details = []
        for key in ("line_start", "line_end", "equation_id", "symbol", "validator_id", "test_id", "receipt_ref", "interface_id"):
            if key in locator:
                details.append(f"{key}={locator[key]}")
        if details:
            lines.append("  - " + "; ".join(details))
    for coordinate in report.get("integration_coordinates", []):
        lines.append(
            f"- `{coordinate['coordinate_id']}` — `{coordinate['precision']}` — `{coordinate.get('location')}`"
        )
        locator = coordinate.get("source_locator", {})
        if locator:
            details = [f"{key}={locator[key]}" for key in sorted(locator)]
            lines.append("  - " + "; ".join(details))
    lines.extend(
        [
            "",
            "These are evidence coordinates, not automatically inferred causal roots.",
            "No finer location is emitted than the supplied evidence supports.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("diagnosis", type=Path)
    parser.add_argument(
        "evidence",
        type=Path,
        nargs="?",
        help="FPDG_INCONSISTENCY_EVIDENCE_V0_1 JSON; omit only for integration-only diagnosis",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        report = localize(
            load_json(args.diagnosis),
            load_json(args.evidence) if args.evidence is not None else None,
        )
        BUILD_DIR.mkdir(exist_ok=True)
        (BUILD_DIR / "PAIN_MICRO_COORDINATES.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        (BUILD_DIR / "PAIN_MICRO_COORDINATES.md").write_text(
            render_markdown(report), encoding="utf-8"
        )
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(
                f"{report['status']}: coordinates={len(report['coordinates'])} "
                f"integration={len(report['integration_coordinates'])} "
                f"finest={report['finest_precision']}"
            )
        return 0 if report["status"] == "LOCALIZED" else 2
    except (OSError, json.JSONDecodeError, MicroLocalizationError, KeyError, TypeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
