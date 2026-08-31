import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "interfaces" / "GSC3CDE_GSC4AB_SHARED_ATLAS_OR_ROUTE_CANDIDATE_V0_4.json"


def load_doc():
    return json.loads(DOC.read_text(encoding="utf-8"))


def test_candidate_is_noncanonical_and_fail_closed():
    d = load_doc()
    assert d["promotion_authority"] is False
    assert d["canonical_graph_mutation"] is False
    assert d["canon_mutations"] == []
    assert d["authority"]["candidate_edge_enters_canonical_graph"] is False


def test_rfe25_is_explicit_or_route():
    d = load_doc()
    route = d["rfe25_or_route"]
    assert route["operator"] == "OR"
    assert set(route["alternatives"]) == {"GENERAL_GSC4A_ROUTE", "FLOW_ADAPTED_GSC4B_ROUTE"}


def test_gsc3e_w0_is_required_only_on_tir_derived_general_shift_subroute():
    d = load_doc()
    fw = d["route_specific_firewalls"]
    assert fw["gsc3e_w0_required_on_rfc_independent_shift_route"] is False
    assert fw["gsc3e_w0_required_on_tir_beta_match_bound_route"] is True
    assert fw["gsc3e_w0_required_on_flow_adapted_zero_shift_route"] is False

    alternatives = {a["route"]: a for a in d["general_shift_source_route"]["alternatives"]}
    tir = set(alternatives["TIR_BETA_MATCH_BOUND"]["requirements"])
    assert "FPDG.GSC4AB.GSC3D_SHARED_ONE_FORM_ALIAS" in tir
    assert "FPDG.GSC4AB.GSC3E_W0_FIREWALL" in tir
    assert "FPDG.GSC4AB.SHARED_MATCHING_ONE_FORM_W0_SOURCE_RECEIPT" in tir
    rfc = set(alternatives["RFC_INDEPENDENT_SHIFT"]["requirements"])
    assert "FPDG.GSC4AB.GSC3E_W0_FIREWALL" not in rfc


def test_flow_adapted_route_constructs_zero_shift_without_shift_source_input():
    d = load_doc()
    route = d["flow_adapted_gsc4b_route"]
    assert route["constructed_fields"] == {"shift_b": "0", "temporal_spatial_drift_v": "0"}
    assert d["route_specific_firewalls"]["flow_adapted_route_consumes_independent_shift_source"] is False
    assert "FPDG.GSC4AB.PRODUCT_TRIVIALIZATION" in route["requirements"]
    assert "FPDG.GSC4AB.GSC3E_W0_FIREWALL" not in route["requirements"]


def test_zero_shift_route_does_not_collapse_extrinsic_curvature():
    d = load_doc()
    assert d["route_specific_firewalls"]["flow_adapted_b_zero_implies_k_zero"] is False


def test_source_validation_heads_are_hosted_pass():
    d = load_doc()
    src = d["source_validations"]
    assert src["gsc4a_provenance_aware_general_atlas"]["rfc_pr"] == 105
    assert src["gsc4a_provenance_aware_general_atlas"]["conclusion"] == "success"
    assert src["gsc4b_flow_adapted_zero_shift_atlas"]["rfc_pr"] == 106
    assert src["gsc4b_flow_adapted_zero_shift_atlas"]["theorem_head"] == "bb427244d28c62e624557cf1b8cf532b49e490cf"
    assert src["gsc4b_flow_adapted_zero_shift_atlas"]["conclusion"] == "success"


def test_production_inputs_remain_open():
    d = load_doc()
    assert "PRODUCTION_LAPSE_COFRAME_SPATIAL_OVERLAP_PACKET" in d["open_inputs"]
    assert "PRODUCTION_OVERLAP_COVERAGE" in d["open_inputs"]
    assert d["authority"]["hosted_pass_closes_production_inputs"] is False
