from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

SCHEMA = "FPDG_IDT_TIR_TERMINAL_STATE_SPATIAL_VERTEX_BINDING_V0_1"
IDT_REPOSITORY = "AdrianLipa90/Informational-Dynamics-of-Time"
TIR_REPOSITORY = "AdrianLipa90/The-Fundamental-Theory-of-Informational-Relations"


class StateVertexBindingError(ValueError):
    """Raised when a supplied cross-repository state/vertex binding fails closed."""


@dataclass(frozen=True)
class StateVertexBindingCertificate:
    input_valid: bool
    provenance_valid: bool
    total_on_terminal_state_domain: bool
    targets_in_tir_vertex_domain: bool
    injective: bool
    surjective_onto_tir_vertex_domain: bool
    production_input: bool
    promotion_review_eligible: bool
    canon_allowed: bool
    dataset_id: str
    binding_sha256: str
    terminal_state_count: int
    tir_vertex_count: int
    used_tir_vertex_count: int
    state_to_vertex: dict[str, str]


def _id(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StateVertexBindingError(f"{name} must be a non-empty string")
    return value.strip()


def _domain(values: Iterable[str], name: str) -> tuple[str, ...]:
    items = tuple(_id(value, name) for value in values)
    if not items or len(set(items)) != len(items):
        raise StateVertexBindingError(f"{name} must be non-empty and unique")
    return tuple(sorted(items))


def domain_sha256(values: Iterable[str]) -> str:
    items = _domain(values, "domain identifier")
    raw = json.dumps(items, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _normalized_bindings(
    bindings: Sequence[Mapping[str, Any]],
) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for index, row in enumerate(bindings):
        if not isinstance(row, Mapping):
            raise StateVertexBindingError(f"binding {index} must be an object")
        out.append(
            {
                "terminal_state_id": _id(
                    row.get("terminal_state_id"),
                    f"binding {index} terminal_state_id",
                ),
                "spatial_vertex_id": _id(
                    row.get("spatial_vertex_id"),
                    f"binding {index} spatial_vertex_id",
                ),
                "binding_evidence_id": _id(
                    row.get("binding_evidence_id"),
                    f"binding {index} binding_evidence_id",
                ),
            }
        )
    if not out:
        raise StateVertexBindingError("bindings must be non-empty")
    return out


def binding_sha256(
    *, bindings: Sequence[Mapping[str, Any]], provenance: Mapping[str, Any]
) -> str:
    normalized = sorted(
        _normalized_bindings(bindings),
        key=lambda row: (
            row["terminal_state_id"],
            row["spatial_vertex_id"],
            row["binding_evidence_id"],
        ),
    )
    source = {
        "idt_source_commit_or_digest": _id(
            provenance.get("idt_source_commit_or_digest"),
            "idt_source_commit_or_digest",
        ),
        "idt_occurrence_state_table_sha256": _id(
            provenance.get("idt_occurrence_state_table_sha256"),
            "idt_occurrence_state_table_sha256",
        ),
        "tir_source_commit_or_digest": _id(
            provenance.get("tir_source_commit_or_digest"),
            "tir_source_commit_or_digest",
        ),
        "tir_spatial_complex_incidence_sha256": _id(
            provenance.get("tir_spatial_complex_incidence_sha256"),
            "tir_spatial_complex_incidence_sha256",
        ),
    }
    raw = json.dumps(
        {"provenance": source, "bindings": normalized},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_binding_dataset(
    *,
    dataset_id: str,
    bindings: Sequence[Mapping[str, Any]],
    idt_source_commit_or_digest: str,
    idt_occurrence_state_table_sha256: str,
    tir_source_commit_or_digest: str,
    tir_spatial_complex_incidence_sha256: str,
    production: bool,
) -> dict[str, Any]:
    provenance = {
        "idt_repository": IDT_REPOSITORY,
        "idt_source_commit_or_digest": _id(
            idt_source_commit_or_digest, "idt_source_commit_or_digest"
        ),
        "idt_occurrence_state_table_sha256": _id(
            idt_occurrence_state_table_sha256,
            "idt_occurrence_state_table_sha256",
        ),
        "tir_repository": TIR_REPOSITORY,
        "tir_source_commit_or_digest": _id(
            tir_source_commit_or_digest, "tir_source_commit_or_digest"
        ),
        "tir_spatial_complex_incidence_sha256": _id(
            tir_spatial_complex_incidence_sha256,
            "tir_spatial_complex_incidence_sha256",
        ),
    }
    normalized = _normalized_bindings(bindings)
    return {
        "schema": SCHEMA,
        "dataset_id": _id(dataset_id, "dataset_id"),
        "production": bool(production),
        "provenance": provenance,
        "bindings": normalized,
        "binding_sha256": binding_sha256(
            bindings=normalized,
            provenance=provenance,
        ),
    }


def certify_binding_dataset(
    data: Mapping[str, Any],
    *,
    expected_terminal_state_ids: Iterable[str],
    expected_tir_vertex_ids: Iterable[str],
    expected_idt_source_commit_or_digest: str,
    expected_idt_occurrence_state_table_sha256: str,
    expected_tir_source_commit_or_digest: str,
    expected_tir_spatial_complex_incidence_sha256: str,
) -> StateVertexBindingCertificate:
    if not isinstance(data, Mapping):
        raise StateVertexBindingError("dataset must be an object")
    if data.get("schema") != SCHEMA:
        raise StateVertexBindingError(f"schema must equal {SCHEMA}")
    dataset_id = _id(data.get("dataset_id"), "dataset_id")
    if type(data.get("production")) is not bool:
        raise StateVertexBindingError("production must be a boolean")

    provenance = data.get("provenance")
    if not isinstance(provenance, Mapping):
        raise StateVertexBindingError("provenance must be an object")
    if _id(provenance.get("idt_repository"), "idt_repository") != IDT_REPOSITORY:
        raise StateVertexBindingError("IDT repository coordinate mismatch")
    if _id(provenance.get("tir_repository"), "tir_repository") != TIR_REPOSITORY:
        raise StateVertexBindingError("TIR repository coordinate mismatch")

    expected = {
        "idt_source_commit_or_digest": _id(
            expected_idt_source_commit_or_digest,
            "expected_idt_source_commit_or_digest",
        ),
        "idt_occurrence_state_table_sha256": _id(
            expected_idt_occurrence_state_table_sha256,
            "expected_idt_occurrence_state_table_sha256",
        ),
        "tir_source_commit_or_digest": _id(
            expected_tir_source_commit_or_digest,
            "expected_tir_source_commit_or_digest",
        ),
        "tir_spatial_complex_incidence_sha256": _id(
            expected_tir_spatial_complex_incidence_sha256,
            "expected_tir_spatial_complex_incidence_sha256",
        ),
    }
    for key, value in expected.items():
        if _id(provenance.get(key), key) != value:
            raise StateVertexBindingError(f"provenance mismatch: {key}")

    states = _domain(expected_terminal_state_ids, "terminal-state domain")
    vertices = _domain(expected_tir_vertex_ids, "TIR vertex domain")
    vertex_set = set(vertices)

    raw_bindings = data.get("bindings")
    if not isinstance(raw_bindings, list):
        raise StateVertexBindingError("bindings must be a list")
    bindings = _normalized_bindings(raw_bindings)
    state_map: dict[str, str] = {}
    evidence_ids: set[str] = set()
    for row in bindings:
        state_id = row["terminal_state_id"]
        vertex_id = row["spatial_vertex_id"]
        evidence_id = row["binding_evidence_id"]
        if state_id in state_map:
            raise StateVertexBindingError(
                f"duplicate or conflicting binding for terminal state {state_id}"
            )
        if evidence_id in evidence_ids:
            raise StateVertexBindingError(
                f"binding_evidence_id must be unique: {evidence_id}"
            )
        if vertex_id not in vertex_set:
            raise StateVertexBindingError(
                f"binding target {vertex_id!r} is outside supplied TIR vertex domain"
            )
        state_map[state_id] = vertex_id
        evidence_ids.add(evidence_id)

    if set(state_map) != set(states):
        missing = sorted(set(states) - set(state_map))
        extra = sorted(set(state_map) - set(states))
        raise StateVertexBindingError(
            f"terminal-state domain mismatch: missing={missing}, extra={extra}"
        )

    supplied_digest = _id(data.get("binding_sha256"), "binding_sha256")
    computed_digest = binding_sha256(bindings=bindings, provenance=provenance)
    if supplied_digest != computed_digest:
        raise StateVertexBindingError("binding_sha256 mismatch")

    values = list(state_map.values())
    injective = len(set(values)) == len(values)
    surjective = set(values) == vertex_set
    production = bool(data["production"])
    return StateVertexBindingCertificate(
        input_valid=True,
        provenance_valid=True,
        total_on_terminal_state_domain=True,
        targets_in_tir_vertex_domain=True,
        injective=injective,
        surjective_onto_tir_vertex_domain=surjective,
        production_input=production,
        promotion_review_eligible=production,
        canon_allowed=False,
        dataset_id=dataset_id,
        binding_sha256=computed_digest,
        terminal_state_count=len(states),
        tir_vertex_count=len(vertices),
        used_tir_vertex_count=len(set(values)),
        state_to_vertex=dict(sorted(state_map.items())),
    )


def reference_binding(*, production: bool = False) -> dict[str, Any]:
    return build_binding_dataset(
        dataset_id="reference-state-vertex-control",
        bindings=[
            {
                "terminal_state_id": "A",
                "spatial_vertex_id": "v0",
                "binding_evidence_id": "ref-A-v0",
            },
            {
                "terminal_state_id": "B",
                "spatial_vertex_id": "v0",
                "binding_evidence_id": "ref-B-v0",
            },
        ],
        idt_source_commit_or_digest="IDT_REFERENCE",
        idt_occurrence_state_table_sha256="IDT_TABLE_REFERENCE",
        tir_source_commit_or_digest="TIR_REFERENCE",
        tir_spatial_complex_incidence_sha256="TIR_COMPLEX_REFERENCE",
        production=production,
    )
