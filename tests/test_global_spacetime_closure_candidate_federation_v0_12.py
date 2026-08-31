import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "interfaces" / "GLOBAL_SPACETIME_CLOSURE_CANDIDATE_FEDERATION_V0_12.json"


def load_candidate():
    return json.loads(CANDIDATE.read_text(encoding="utf-8"))


def test_candidate_remains_noncanonical_and_runtime_cannot_promote():
    data = load_candidate()
    assert data["promotion_authority"] is False
    assert data["canonical_graph_mutation"] is False
    assert data["canon_mutations"] == []
    assert data["live_36d_audit"]["authority"] == "CANDIDATE_ONLY"
    assert data["live_36d_audit"]["promotion_evidence"] is False
    assert data["firewalls"]["runtime_audit_can_promote"] is False


def test_source_theorem_has_hosted_success():
    src = load_candidate()["source_validation"]
    assert src["rfc_pr"] == 116
    assert src["conclusion"] == "success"
    assert src["theorem_head"] == "f1e557fce5f541ec1de6bb496213ad76d0e9d306"
    assert "1392 passed" in src["pytest"]


def test_gsc6c_derives_properness_from_upstream_product_parents():
    data = load_candidate()
    exact = set(data["refinement"]["exact_derivations"])
    assert "REGULAR_ONTO_PRODUCT_CLOCK_IMAGE_IS_OPEN_INTERVAL" in exact
    assert "ORIENTATION_PRESERVING_SMOOTH_DIFFEO_I_TO_R_EXISTS" in exact
    assert "COMPACT_FIBER_MAKES_TAU_PROPER" in exact
    assert "GSC6B_PROPER_CLOCK_INPUT_DERIVED" in exact


def test_gsc6_routes_preserve_or_semantics():
    data = load_candidate()
    routes = data["gsc6_routes"]
    assert routes["operator"] == "OR"
    ids = {route["id"] for route in routes["alternatives"]}
    assert ids == {
        "RF_L8_CONSTANT_SCALE",
        "RFC_GSC6A_ADAPTIVE_WICK",
        "RFC_GSC6B_DIRECT_PROPER_CLOCK",
        "RFC_GSC6C_COMPACT_FIBER_PRODUCT",
    }


def test_gsc6c_route_removes_only_its_separate_global_witnesses():
    data = load_candidate()
    removed = set(data["refinement"]["derived_coordinates_removed_from_production_frontier_on_this_route"])
    assert "SEPARATELY_SUPPLIED_PROPER_REAL_CLOCK" in removed
    assert "SEPARATELY_SUPPLIED_GLOBAL_FINITE_LAPSE_BOUND_NMAX" in removed
    assert "SEPARATELY_SUPPLIED_COMPLETE_UNSCALED_WICK_METRIC_W" in removed
    assert "SEPARATELY_SUPPLIED_COMPLETE_ADAPTIVE_WICK_METRIC_HN" in removed
    assert data["frontier_update"]["GSC5_requirement_for_full_GR_Cauchy"] == "PRESERVED"


def test_gsc6c_production_parents_remain_open():
    data = load_candidate()
    open_parents = set(data["frontier_update"]["GSC6C_open_parents"])
    assert open_parents == {
        "PRODUCTION_GSC1_COMPACT_SPATIAL_REALIZATION",
        "PRODUCTION_GSC3A_INTERVAL_COMPLETE_PRODUCT_REALIZATION_AND_COMMON_CLOCK",
        "PRODUCTION_RF_E25_GLOBAL_LORENTZIAN_ADM_CARRIER",
    }
    assert data["firewalls"]["gsc6c_closes_production_GSC1_parent"] is False
    assert data["firewalls"]["gsc6c_closes_production_GSC3A_parent"] is False
    assert data["firewalls"]["gsc6c_closes_production_RF_E25_parent"] is False


def test_global_gr_cauchy_still_requires_gsc5_and_gsc6():
    comp = load_candidate()["global_gr_cauchy_composition"]
    assert comp["operator"] == "AND"
    assert set(comp["requirements"]) == {
        "RFC_E26_GSC5_PRODUCTION_GLOBAL_EINSTEIN_CARRIER",
        "GSC6_GLOBAL_HYPERBOLICITY_CAUCHY_FOLIATION",
    }
    assert comp["target"] == "GLOBAL_GR_CAUCHY_CARRIER"


def test_live_36d_receipts_have_hash_shape():
    audit = load_candidate()["live_36d_audit"]
    assert len(audit["terminal_receipt_sha256"]) == 64
    assert len(audit["phasenav_trace_sha256"]) == 64
    assert audit["shape"] == [10, 36]
