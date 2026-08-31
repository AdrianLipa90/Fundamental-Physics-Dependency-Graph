import pytest

from tools.certify_idt_tir_state_vertex_binding import (
    StateVertexBindingError,
    binding_sha256,
    certify_binding_dataset,
    reference_binding,
)

KW = dict(
    expected_terminal_state_ids=["A", "B"],
    expected_tir_vertex_ids=["v0", "v1"],
    expected_idt_source_commit_or_digest="IDT_REFERENCE",
    expected_idt_occurrence_state_table_sha256="IDT_TABLE_REFERENCE",
    expected_tir_source_commit_or_digest="TIR_REFERENCE",
    expected_tir_spatial_complex_incidence_sha256="TIR_COMPLEX_REFERENCE",
)


def test_total_function_allows_noninjective_spatial_anchor():
    cert = certify_binding_dataset(reference_binding(), **KW)
    assert cert.total_on_terminal_state_domain
    assert cert.targets_in_tir_vertex_domain
    assert cert.injective is False
    assert cert.surjective_onto_tir_vertex_domain is False
    assert cert.canon_allowed is False


def test_missing_state_binding_fails_closed():
    data = reference_binding()
    data["bindings"] = data["bindings"][:1]
    data["binding_sha256"] = binding_sha256(
        bindings=data["bindings"],
        provenance=data["provenance"],
    )
    with pytest.raises(StateVertexBindingError, match="domain mismatch"):
        certify_binding_dataset(data, **KW)


def test_unknown_tir_vertex_fails_closed():
    data = reference_binding()
    data["bindings"][1]["spatial_vertex_id"] = "vx"
    data["binding_sha256"] = binding_sha256(
        bindings=data["bindings"],
        provenance=data["provenance"],
    )
    with pytest.raises(StateVertexBindingError, match="outside supplied TIR vertex domain"):
        certify_binding_dataset(data, **KW)


def test_source_coordinate_drift_fails_closed():
    data = reference_binding()
    with pytest.raises(StateVertexBindingError, match="provenance mismatch"):
        certify_binding_dataset(
            data,
            **{**KW, "expected_idt_occurrence_state_table_sha256": "other"},
        )


def test_binding_tampering_fails_digest():
    data = reference_binding()
    data["bindings"][0]["binding_evidence_id"] = "tampered"
    with pytest.raises(StateVertexBindingError, match="binding_sha256 mismatch"):
        certify_binding_dataset(data, **KW)


def test_production_flag_gives_review_eligibility_only():
    cert = certify_binding_dataset(reference_binding(production=True), **KW)
    assert cert.promotion_review_eligible is True
    assert cert.canon_allowed is False
