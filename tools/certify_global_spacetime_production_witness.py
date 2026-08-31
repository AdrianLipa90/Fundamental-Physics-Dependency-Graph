from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


SCHEMA = "FPDG_GLOBAL_SPACETIME_PRODUCTION_WITNESS_V0_1"
TARGET_GR = "GLOBAL_GR_CAUCHY_CARRIER"
TARGET_EVENT = "PHYSICAL_EVENT_REALIZATION_ON_GLOBAL_GR_CAUCHY_CARRIER"
FLOW_ROUTE = "FLOW_ADAPTED_COMPACT_FIBER"
GENERAL_ROUTE = "GENERAL_MATCHING_COMPACT_FIBER"

GR_GROUPS = (
    "W1_GSC1_SPATIAL_TOPOLOGY",
    "W2_GSC3A_GLOBAL_PRODUCT_CLOCK",
    "W3_GSC4_NUMERIC_SPATIAL_GEOMETRY",
    "W4_GSC4_PHASE_MAGNITUDE_SCALE_FIELD",
    "W5_IDT_GLOBAL_LAPSE",
    "W6_RF_E24_PATCHWISE_LOCAL_SOLUTIONS",
    "W7_TARGET_DOMAIN_COVERAGE",
)
EVENT_GROUPS = (
    "E1_GSC2_TEMPORAL_EVENT_COMPLEX",
    "E2_EVENT_SPATIAL_ANCHOR_BINDING",
)
GENERAL_ROUTE_GROUPS = ("M1_SHARED_MATCHING_ONE_FORM_W0",)

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def _lineage(witness: dict[str, Any], key: str) -> Any:
    lineage = witness.get("lineage")
    if not isinstance(lineage, dict):
        return None
    return lineage.get(key)


def _certified(witness: Any) -> bool:
    return isinstance(witness, dict) and witness.get("status") == "CERTIFIED_PRODUCTION"


def _validate_receipt(group_id: str, witness: dict[str, Any], conflicts: list[str]) -> None:
    receipt = witness.get("receipt")
    if not isinstance(receipt, dict):
        conflicts.append(f"{group_id}:CERTIFIED_PRODUCTION_WITHOUT_RECEIPT")
        return

    repository = receipt.get("repository")
    commit = receipt.get("commit")
    path = receipt.get("path")
    digest = receipt.get("sha256")

    if not isinstance(repository, str) or "/" not in repository:
        conflicts.append(f"{group_id}:INVALID_RECEIPT_REPOSITORY")
    if not isinstance(commit, str) or HEX40.fullmatch(commit) is None:
        conflicts.append(f"{group_id}:INVALID_RECEIPT_COMMIT")
    if not isinstance(path, str) or not path.strip():
        conflicts.append(f"{group_id}:INVALID_RECEIPT_PATH")
    if not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
        conflicts.append(f"{group_id}:INVALID_RECEIPT_SHA256")


def _require_equal(
    witnesses: dict[str, Any],
    refs: list[tuple[str, str]],
    label: str,
    conflicts: list[str],
) -> None:
    values: list[tuple[str, Any]] = []
    for group_id, key in refs:
        witness = witnesses.get(group_id)
        if not _certified(witness):
            continue
        value = _lineage(witness, key)
        if value is not None:
            values.append((group_id, value))

    if len(values) < 2:
        return

    unique = {json.dumps(v, sort_keys=True) for _, v in values}
    if len(unique) > 1:
        detail = ",".join(f"{group}={value}" for group, value in values)
        conflicts.append(f"{label}:{detail}")


def certify_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    missing: list[str] = []
    conflicts: list[str] = []
    quarantined: list[str] = []

    if manifest.get("schema") != SCHEMA:
        conflicts.append("INVALID_SCHEMA")

    target = manifest.get("target")
    if target not in {TARGET_GR, TARGET_EVENT}:
        conflicts.append("INVALID_TARGET")

    route = manifest.get("route")
    if route not in {FLOW_ROUTE, GENERAL_ROUTE}:
        conflicts.append("INVALID_ROUTE")

    witnesses = manifest.get("witnesses")
    if not isinstance(witnesses, dict):
        witnesses = {}
        conflicts.append("WITNESSES_NOT_OBJECT")

    required = list(GR_GROUPS)
    if target == TARGET_EVENT:
        required.extend(EVENT_GROUPS)
    if route == GENERAL_ROUTE:
        required.extend(GENERAL_ROUTE_GROUPS)

    for group_id in required:
        witness = witnesses.get(group_id)
        if not isinstance(witness, dict):
            missing.append(group_id)
            continue
        status = witness.get("status")
        if status == "OPEN":
            missing.append(group_id)
            continue
        if status == "QUARANTINED":
            quarantined.append(group_id)
            continue
        if status != "CERTIFIED_PRODUCTION":
            conflicts.append(f"{group_id}:INVALID_STATUS")
            continue
        _validate_receipt(group_id, witness, conflicts)

    # Shared clock lineage across product clock, scale field and lapse.
    _require_equal(
        witnesses,
        [
            ("W2_GSC3A_GLOBAL_PRODUCT_CLOCK", "clock_id"),
            ("W4_GSC4_PHASE_MAGNITUDE_SCALE_FIELD", "clock_id"),
            ("W5_IDT_GLOBAL_LAPSE", "clock_id"),
        ],
        "CLOCK_ID_CONFLICT",
        conflicts,
    )

    # Shared spatial carrier across topology, product, numeric geometry and scale field.
    _require_equal(
        witnesses,
        [
            ("W1_GSC1_SPATIAL_TOPOLOGY", "spatial_carrier_id"),
            ("W2_GSC3A_GLOBAL_PRODUCT_CLOCK", "spatial_carrier_id"),
            ("W3_GSC4_NUMERIC_SPATIAL_GEOMETRY", "spatial_carrier_id"),
            ("W4_GSC4_PHASE_MAGNITUDE_SCALE_FIELD", "spatial_carrier_id"),
        ],
        "SPATIAL_CARRIER_ID_CONFLICT",
        conflicts,
    )

    # Cover identity is shared between topology and numeric overlap geometry.
    _require_equal(
        witnesses,
        [
            ("W1_GSC1_SPATIAL_TOPOLOGY", "cover_id"),
            ("W3_GSC4_NUMERIC_SPATIAL_GEOMETRY", "cover_id"),
        ],
        "COVER_ID_CONFLICT",
        conflicts,
    )

    # Domain identity is shared by patchwise RF-E24 receipts and the coverage receipt.
    _require_equal(
        witnesses,
        [
            ("W6_RF_E24_PATCHWISE_LOCAL_SOLUTIONS", "domain_id"),
            ("W7_TARGET_DOMAIN_COVERAGE", "domain_id"),
        ],
        "DOMAIN_ID_CONFLICT",
        conflicts,
    )

    if target == TARGET_EVENT:
        _require_equal(
            witnesses,
            [
                ("W2_GSC3A_GLOBAL_PRODUCT_CLOCK", "clock_id"),
                ("E1_GSC2_TEMPORAL_EVENT_COMPLEX", "clock_id"),
            ],
            "EVENT_CLOCK_ID_CONFLICT",
            conflicts,
        )
        _require_equal(
            witnesses,
            [
                ("W1_GSC1_SPATIAL_TOPOLOGY", "spatial_carrier_id"),
                ("E2_EVENT_SPATIAL_ANCHOR_BINDING", "spatial_carrier_id"),
            ],
            "EVENT_SPATIAL_CARRIER_ID_CONFLICT",
            conflicts,
        )
        _require_equal(
            witnesses,
            [
                ("E1_GSC2_TEMPORAL_EVENT_COMPLEX", "event_complex_id"),
                ("E2_EVENT_SPATIAL_ANCHOR_BINDING", "event_complex_id"),
            ],
            "EVENT_COMPLEX_ID_CONFLICT",
            conflicts,
        )

    if route == GENERAL_ROUTE:
        _require_equal(
            witnesses,
            [
                ("W2_GSC3A_GLOBAL_PRODUCT_CLOCK", "clock_id"),
                ("M1_SHARED_MATCHING_ONE_FORM_W0", "clock_id"),
            ],
            "MATCHING_CLOCK_ID_CONFLICT",
            conflicts,
        )
        _require_equal(
            witnesses,
            [
                ("W2_GSC3A_GLOBAL_PRODUCT_CLOCK", "realization_id"),
                ("M1_SHARED_MATCHING_ONE_FORM_W0", "realization_id"),
            ],
            "MATCHING_REALIZATION_ID_CONFLICT",
            conflicts,
        )

    ready = not missing and not conflicts and not quarantined

    if conflicts:
        status = "LINEAGE_CONFLICTS"
    elif quarantined:
        status = "QUARANTINED_WITNESSES"
    elif missing:
        status = "MISSING_WITNESSES"
    else:
        status = "READY_FOR_SOURCE_RESOLUTION"

    return {
        "schema": "FPDG_GLOBAL_SPACETIME_PRODUCTION_WITNESS_CERTIFICATE_V0_1",
        "status": status,
        "target": target,
        "route": route,
        "required_groups": required,
        "missing_witnesses": sorted(set(missing)),
        "quarantined_witnesses": sorted(set(quarantined)),
        "lineage_conflicts": sorted(set(conflicts)),
        "all_required_slots_certified": ready,
        "source_receipt_resolution_required": True,
        "production_promoted": False,
        "promotion_authority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    result = certify_manifest(manifest)
    raw = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(raw, encoding="utf-8")
    else:
        print(raw, end="")
    return 0 if result["status"] == "READY_FOR_SOURCE_RESOLUTION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
