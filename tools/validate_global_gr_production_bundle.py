"""Fail-closed validator for a proof-carrying global-GR production bundle.

This integration contract does not execute TIR/IDT/RFC source certifiers and does
not create source-owned scientific receipts.  It verifies that already-produced
GSC-1..GSC-6 receipts and the explicit global witnesses belong to one lineage,
one target domain, and the exact dependency chain required by the FPDG global
spacetime closure ledger.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Mapping
import re


SCHEMA = "FPDG_GLOBAL_GR_PRODUCTION_WITNESS_BUNDLE_V0_1"

REQUIRED_GATES = {
    "GSC-1": {
        "source_repository": "AdrianLipa90/The-Fundamental-Theory-of-Informational-Relations",
        "required_verdict": "PASS_PRODUCTION_3_MANIFOLD",
    },
    "GSC-2": {
        "source_repository": "AdrianLipa90/Informational-Dynamics-of-Time",
        "required_verdict": "PASS_PRODUCTION_EXACT_EVENT_CLOCK",
    },
    "GSC-3": {
        "source_repository": "AdrianLipa90/Informational-Dynamics-of-Time",
        "required_verdict": "PASS_REGULAR_CLOCK_EXTENSION",
    },
    "GSC-4": {
        "source_repository": "AdrianLipa90/Relational-Field-Closure",
        "required_verdict": "PASS_SHARED_SPACETIME_REALIZATION",
    },
    "GSC-5": {
        "source_repository": "AdrianLipa90/Relational-Field-Closure",
        "required_verdict": "PASS_GLOBAL_EINSTEIN_REALIZATION",
    },
    "GSC-6": {
        "source_repository": "AdrianLipa90/Relational-Field-Closure",
        "required_verdict": "PASS_GLOBAL_CAUCHY_HYPERBOLICITY",
    },
}

REQUIRED_DEPENDENCIES = {
    "GSC-5": ("GSC-1", "GSC-2", "GSC-3", "GSC-4"),
    "GSC-6": ("GSC-3", "GSC-4", "GSC-5"),
}

REQUIRED_GLOBAL_WITNESSES = (
    "target_domain_coverage",
    "global_lapse_upper_bound",
    "adm_wick_completeness",
)

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class ProductionBundleError(ValueError):
    """Raised when a declared global-GR witness bundle violates the contract."""


@dataclass(frozen=True)
class ProductionBundleCertificate:
    structural_pass: bool
    production_promotable: bool
    global_gr_cauchy_carrier_eligible: bool
    bundle_id: str
    lineage_id: str
    target_domain_id: str
    gate_count: int
    witness_count: int
    production_status: str


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ProductionBundleError(f"{label} must be a mapping")
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProductionBundleError(f"{label} must be a non-empty string")
    return value


def _bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise ProductionBundleError(f"{label} must be boolean")
    return value


def _sha40(value: Any, label: str) -> str:
    text = _text(value, label)
    if HEX40.fullmatch(text) is None:
        raise ProductionBundleError(f"{label} must be a lowercase 40-hex commit SHA")
    return text


def _sha256(value: Any, label: str) -> str:
    text = _text(value, label)
    if HEX64.fullmatch(text) is None:
        raise ProductionBundleError(f"{label} must be a lowercase 64-hex SHA-256")
    return text


def _evidence_class(value: Any, production: bool, label: str) -> str:
    text = _text(value, label)
    allowed = {"PRODUCTION", "REFERENCE_CONTROL"}
    if text not in allowed:
        raise ProductionBundleError(
            f"{label} must be PRODUCTION or REFERENCE_CONTROL; synthetic/fixture classes are inadmissible"
        )
    expected = "PRODUCTION" if production else "REFERENCE_CONTROL"
    if text != expected:
        raise ProductionBundleError(
            f"{label}={text!r} is incompatible with production={production}"
        )
    return text


def _same(value: Any, expected: str, label: str) -> str:
    text = _text(value, label)
    if text != expected:
        raise ProductionBundleError(f"{label} must equal {expected!r}, got {text!r}")
    return text


def validate_global_gr_production_bundle(payload: Mapping[str, Any]) -> ProductionBundleCertificate:
    """Validate one GSC-1..GSC-6 proof bundle and return its promotion state.

    A reference-control bundle can be structurally valid but is never production
    promotable.  A production bundle is promotable only when every source-owned
    gate receipt carries the gate-specific required verdict, every dependency is
    digest-bound to those receipts, and all global witnesses are production-class.
    """

    data = _mapping(payload, "bundle")
    _same(data.get("schema"), SCHEMA, "schema")

    bundle_id = _text(data.get("bundle_id"), "bundle_id")
    lineage_id = _text(data.get("lineage_id"), "lineage_id")
    target_domain_id = _text(data.get("target_domain_id"), "target_domain_id")
    production = _bool(data.get("production"), "production")
    evidence = _evidence_class(data.get("evidence_class"), production, "evidence_class")

    gates = _mapping(data.get("gates"), "gates")
    if set(gates) != set(REQUIRED_GATES):
        missing = sorted(set(REQUIRED_GATES) - set(gates))
        extra = sorted(set(gates) - set(REQUIRED_GATES))
        raise ProductionBundleError(f"gates must be exactly GSC-1..GSC-6; missing={missing}, extra={extra}")

    gate_digests: dict[str, str] = {}
    all_digests: set[str] = set()

    for gate_id, expected in REQUIRED_GATES.items():
        gate = _mapping(gates[gate_id], gate_id)
        _same(gate.get("source_repository"), expected["source_repository"], f"{gate_id}.source_repository")
        _sha40(gate.get("source_commit"), f"{gate_id}.source_commit")
        digest = _sha256(gate.get("receipt_sha256"), f"{gate_id}.receipt_sha256")
        if digest in all_digests:
            raise ProductionBundleError(f"receipt digest collision at {gate_id}")
        all_digests.add(digest)
        gate_digests[gate_id] = digest

        _same(gate.get("lineage_id"), lineage_id, f"{gate_id}.lineage_id")
        _same(gate.get("target_domain_id"), target_domain_id, f"{gate_id}.target_domain_id")
        gate_production = _bool(gate.get("production"), f"{gate_id}.production")
        if gate_production != production:
            raise ProductionBundleError(f"{gate_id}.production must match bundle production")
        _evidence_class(gate.get("evidence_class"), production, f"{gate_id}.evidence_class")

        _same(gate.get("required_verdict"), expected["required_verdict"], f"{gate_id}.required_verdict")
        observed = _text(gate.get("observed_verdict"), f"{gate_id}.observed_verdict")
        if production:
            if observed != expected["required_verdict"]:
                raise ProductionBundleError(
                    f"{gate_id} production receipt must observe {expected['required_verdict']!r}"
                )
        elif observed != "REFERENCE_CONTROL_PASS":
            raise ProductionBundleError(
                f"{gate_id} reference-control receipt must observe 'REFERENCE_CONTROL_PASS'"
            )

    dependencies = _mapping(data.get("dependencies"), "dependencies")
    if set(dependencies) != set(REQUIRED_DEPENDENCIES):
        raise ProductionBundleError("dependencies must contain exactly GSC-5 and GSC-6 parent bindings")
    for child, parents in REQUIRED_DEPENDENCIES.items():
        binding = _mapping(dependencies[child], f"dependencies.{child}")
        if set(binding) != set(parents):
            raise ProductionBundleError(f"dependencies.{child} must bind exactly {list(parents)}")
        for parent in parents:
            digest = _sha256(binding[parent], f"dependencies.{child}.{parent}")
            if digest != gate_digests[parent]:
                raise ProductionBundleError(
                    f"dependencies.{child}.{parent} does not bind the supplied {parent} receipt"
                )

    witnesses = _mapping(data.get("global_witnesses"), "global_witnesses")
    if set(witnesses) != set(REQUIRED_GLOBAL_WITNESSES):
        raise ProductionBundleError(
            f"global_witnesses must be exactly {list(REQUIRED_GLOBAL_WITNESSES)}"
        )

    for witness_name in REQUIRED_GLOBAL_WITNESSES:
        witness = _mapping(witnesses[witness_name], f"global_witnesses.{witness_name}")
        digest = _sha256(witness.get("receipt_sha256"), f"{witness_name}.receipt_sha256")
        if digest in all_digests:
            raise ProductionBundleError(f"receipt digest collision at global witness {witness_name}")
        all_digests.add(digest)
        _same(witness.get("lineage_id"), lineage_id, f"{witness_name}.lineage_id")
        _same(witness.get("target_domain_id"), target_domain_id, f"{witness_name}.target_domain_id")
        witness_production = _bool(witness.get("production"), f"{witness_name}.production")
        if witness_production != production:
            raise ProductionBundleError(f"{witness_name}.production must match bundle production")
        _evidence_class(witness.get("evidence_class"), production, f"{witness_name}.evidence_class")

    coverage = _mapping(witnesses["target_domain_coverage"], "target_domain_coverage")
    if not _bool(coverage.get("covers_target_domain"), "target_domain_coverage.covers_target_domain"):
        raise ProductionBundleError("target-domain coverage witness must certify full target-domain coverage")

    lapse = _mapping(witnesses["global_lapse_upper_bound"], "global_lapse_upper_bound")
    n_max_raw = lapse.get("n_max")
    if isinstance(n_max_raw, bool):
        raise ProductionBundleError("global_lapse_upper_bound.n_max must be numeric")
    try:
        n_max = float(n_max_raw)
    except (TypeError, ValueError) as exc:
        raise ProductionBundleError("global_lapse_upper_bound.n_max must be numeric") from exc
    if not isfinite(n_max) or n_max <= 0.0:
        raise ProductionBundleError("global_lapse_upper_bound.n_max must be finite and positive")
    if not _bool(lapse.get("globally_certified"), "global_lapse_upper_bound.globally_certified"):
        raise ProductionBundleError("global lapse bound must be globally certified")

    wick = _mapping(witnesses["adm_wick_completeness"], "adm_wick_completeness")
    if not _bool(wick.get("complete"), "adm_wick_completeness.complete"):
        raise ProductionBundleError("ADM Wick-metric witness must certify completeness")

    production_promotable = production and evidence == "PRODUCTION"
    return ProductionBundleCertificate(
        structural_pass=True,
        production_promotable=production_promotable,
        global_gr_cauchy_carrier_eligible=production_promotable,
        bundle_id=bundle_id,
        lineage_id=lineage_id,
        target_domain_id=target_domain_id,
        gate_count=len(gates),
        witness_count=len(witnesses),
        production_status=(
            "ELIGIBLE_FOR_SOURCE_OWNED_PRODUCTION_PROMOTION"
            if production_promotable
            else "REFERENCE_CONTROL_ONLY_NO_PRODUCTION_PROMOTION"
        ),
    )
