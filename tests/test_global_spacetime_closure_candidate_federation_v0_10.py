import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFINEMENT = ROOT / "interfaces" / "GLOBAL_SPACETIME_CLOSURE_CANDIDATE_FEDERATION_V0_10.json"


def load_refinement():
    return json.loads(REFINEMENT.read_text(encoding="utf-8"))


def test_refinement_remains_noncanonical():
    data = load_refinement()
    assert data["promotion_authority"] is False
    assert data["canonical_graph_mutation"] is False
    assert data["canon_mutations"] == []


def test_gsc4h_hosted_pass_is_recorded():
    data = load_refinement()
    src = data["source_validation"]
    assert src["rfc_pr"] == 113
    assert src["reference_suite_run"] == 469
    assert src["conclusion"] == "success"
    assert src["pytest"].startswith("1420 passed")


def test_same_incidence_distinct_numeric_geometry_is_explicit():
    data = load_refinement()
    refinement = data["refinement"]
    assert refinement["exact_result"] == (
        "ONE_FIXED_INCIDENCE_SURFACE_ADMITS_MULTIPLE_INEQUIVALENT_NUMERIC_SE3_COCYCLES"
    )
    witness = refinement["constructive_witness"]
    assert witness["incidence"] == "p->q"
    assert witness["inequivalent_mod_global_se3"] is True


def test_topology_numeric_geometry_and_scale_have_distinct_owners():
    data = load_refinement()
    typed = data["refinement"]["typing_consequence"]
    assert typed["TIR_A5_GSC4C"] == "DISCRETE_INDEXING_AND_COVER_CARRIER"
    assert typed["RFC_GSC4G_NUMERIC_SE3_COCYCLE"] == "SEPARATELY_SOURCE_BOUND_NUMERIC_GEOMETRY"
    assert typed["RFC_GSC4E_PHASE_MAGNITUDE"] == "SEPARATELY_SOURCE_BOUND_POINTWISE_SCALE_FIELD"


def test_numeric_se3_cocycle_remains_confirmed_source_input():
    data = load_refinement()
    frontier = data["frontier_update"]
    assert frontier["confirmed_open_source_input"] == (
        "PRODUCTION_CONNECTED_NUMERIC_SE3_OVERLAP_COCYCLE_ON_GSC4C_COVER"
    )
    assert "INCIDENCE_ONLY" in frontier["search_boundary"]


def test_runtime_audit_is_candidate_only():
    data = load_refinement()
    audit = data["live_36d_audit"]
    assert audit["authority"] == "CANDIDATE_ONLY"
    assert audit["promotion_evidence"] is False
    assert audit["shape"] == [12, 36]
    assert len(audit["terminal_receipt_sha256"]) == 64
    assert len(audit["phasenav_trace_sha256"]) == 64
