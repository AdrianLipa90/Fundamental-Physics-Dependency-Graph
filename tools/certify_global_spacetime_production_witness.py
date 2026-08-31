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
CANONICAL_ATLAS_ROUTE = "FLOW_ADAPTED_CANONICAL_ATLAS_DOMAIN"
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
GR_GROUPS_CANONICAL_ATLAS = GR_GROUPS[:-1]
EVENT_GROUPS = (
    "E1_GSC2_TEMPORAL_EVENT_COMPLEX",
    "E2_EVENT_SPATIAL_ANCHOR_BINDING",
)
GENERAL_ROUTE_GROUPS = ("M1_SHARED_MATCHING_ONE_FORM_W0",)

PRODUCT_PROVENANCE_FLOW = "FLOW_COVERAGE"
PRODUCT_PROVENANCE_INDEPENDENT = "INDEPENDENT_SOURCE_RECEIPT"
PRODUCT_PROVENANCE_CLOCK = "CLOCK_PROPERNESS"

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


def _validate_product_provenance(witness: Any, conflicts: list[str]) -> None:
    group_id = "W2_GSC3A_GLOBAL_PRODUCT_CLOCK"
    if not _certified(witness):
        return

    provenance = _lineage(witness, "product_provenance")
    if not isinstance(provenance, str) or not provenance.strip():
        conflicts.append(f"{group_id}:MISSING_PRODUCT_PROVENANCE")
        return

    tag = provenance.strip().upper()
    if tag == PRODUCT_PROVENANCE_CLOCK:
        conflicts.append(f"{group_id}:PROPER_CLOCK_ANCESTRY_CYCLE")
        return
    if tag == PRODUCT_PROVENANCE_INDEPENDENT:
        if _lineage(witness, "no_proper_clock_ancestry") is not True:
            conflicts.append(f"{group_id}:INDEPENDENT_PRODUCT_ANCESTRY_NOT_CERTIFIED")
        return
    if tag == PRODUCT_PROVENANCE_FLOW:
        return

    conflicts.append(f"{group_id}:UNSUPPORTED_PRODUCT_PROVENANCE:{tag}")


def _id_set(value: Any, label: str, conflicts: list[str]) -> set[str] | None:
    if not isinstance(value, list) or not value:
        conflicts.append(f"{label}:MISSING_OR_INVALID_PATCH_ID_LIST")
        return None
    out: list[str] = []
    for raw in value:
        if not isinstance(raw, str) or not raw.strip():
            conflicts.append(f"{label}:INVALID_PATCH_ID")
            return None
        out.append(raw.strip())
    if len(set(out)) != len(out):
        conflicts.append(f"{label}:DUPLICATE_PATCH_ID")
        return None
    return set(out)


def _validate_canonical_atlas_domain_coverage(
    witnesses: dict[str, Any], conflicts: list[str]
) -> bool:
    """Derive W7 from W2 canonical-atlas lineage and W6 patch completeness."""

    w2 = witnesses.get("W2_GSC3A_GLOBAL_PRODUCT_CLOCK")
    w6 = witnesses.get("W6_RF_E24_PATCHWISE_LOCAL_SOLUTIONS")
    if not (_certified(w2) and _certified(w6)):
        return False

    if _lineage(w2, "canonical_atlas_coverage_certified") is not True:
        conflicts.append("W2_GSC3A_GLOBAL_PRODUCT_CLOCK:CANONICAL_ATLAS_COVERAGE_NOT_CERTIFIED")
        return False

    atlas_ids = _id_set(
        _lineage(w2, "atlas_patch_ids"),
        "W2_GSC3A_GLOBAL_PRODUCT_CLOCK",
        conflicts,
    )
    solution_ids = _id_set(
        _lineage(w6, "solution_patch_ids"),
        "W6_RF_E24_PATCHWISE_LOCAL_SOLUTIONS",
        conflicts,
    )
    if atlas_ids is None or solution_ids is None:
        return False

    if atlas_ids != solution_ids:
        missing = sorted(atlas_ids - solution_ids)
        extra = sorted(solution_ids - atlas_ids)
        conflicts.append(
            "GSC5B_PATCH_COMPLETENESS_MISMATCH:"
            f"missing={missing},extra={extra}"
        )
        return False

    atlas_domain = _lineage(w2, "atlas_domain_id")
    target_domain = _lineage(w6, "domain_id")
    if not isinstance(atlas_domain, str) or not atlas_domain.strip():
        conflicts.append("W2_GSC3A_GLOBAL_PRODUCT_CLOCK:MISSING_ATLAS_DOMAIN_ID")
        return False
    if target_domain != atlas_domain:
        conflicts.append(
            "GSC5B_TARGET_ATLAS_DOMAIN_CONFLICT:"
            f"target={target_domain},atlas={atlas_domain}"
        )
        return False

    return True


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
    derived_witnesses: list[str] = []

    if manifest.get("schema") != SCHEMA:
        conflicts.append("INVALID_SCHEMA")

    target = manifest.get("target")
    if target not in {TARGET_GR, TARGET_EVENT}:
        conflicts.append("INVALID_TARGET")

    route = manifest.get("route")
    if route not in {FLOW_ROUTE, CANONICAL_ATLAS_ROUTE, GENERAL_ROUTE}:
        conflicts.append("INVALID_ROUTE")

    witnesses = manifest.get("witnesses")
    if not isinstance(witnesses, dict):
        witnesses = {}
        conflicts.append("WITNESSES_NOT_OBJECT")

    required = list(
        GR_GROUPS_CANONICAL_ATLAS if route == CANONICAL_ATLAS_ROUTE else GR_GROUPS
    )
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

    _validate_product_provenance(witnesses.get("W2_GSC3A_GLOBAL_PRODUCT_CLOCK"), conflicts)

    if route == CANONICAL_ATLAS_ROUTE:
        if _validate_canonical_atlas_domain_coverage(witnesses, conflicts):
            derived_witnesses.append("W7_TARGET_DOMAIN_COVERAGE")

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

    cover_refs = [
        ("W1_GSC1_SPATIAL_TOPOLOGY", "cover_id"),
        ("W3_GSC4_NUMERIC_SPATIAL_GEOMETRY", "cover_id"),
    ]
    if route == CANONICAL_ATLAS_ROUTE:
        cover_refs.append(("W2_GSC3A_GLOBAL_PRODUCT_CLOCK", "cover_id"))
    _require_equal(witnesses, cover_refs, "COVER_ID_CONFLICT", conflicts)

    if route != CANONICAL_ATLAS_ROUTE:
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
        "derived_witnesses": sorted(derived_witnesses),
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
