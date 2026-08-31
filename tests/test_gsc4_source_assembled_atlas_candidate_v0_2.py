import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "interfaces" / "GSC4_SOURCE_ASSEMBLED_ATLAS_CANDIDATE_V0_2.json"


def load_candidate():
    return json.loads(CANDIDATE.read_text(encoding="utf-8"))


def test_candidate_is_noncanonical_and_fail_closed():
    data = load_candidate()
    assert data["promotion_authority"] is False
    assert data["canonical_graph_mutation"] is False
    assert data["canon_mutations"] == []
    fw = data["firewalls"]
    assert fw["gremlin_can_promote"] is False
    assert fw["terminal36d_can_promote"] is False
    assert fw["phasenav36d_can_promote"] is False
    assert fw["hosted_reference_pass_closes_production_inputs"] is False


def test_general_route_does_not_require_product_trivialization():
    data = load_candidate()
    route = data["general_shared_clock_patch_route"]
    assert route["operator"] == "AND"
    assert route["product_trivialization_required"] is False
    assert "FPDG.GSC3.PRODUCT_TRIVIALIZATION" not in route["requirements"]
    assert "FPDG.GSC4.GENERAL_MATCHING_SHIFT_DRIFT_PACKET" in route["requirements"]
    assert "FPDG.GSC4.GSC3E_W0_SOURCE_BINDING" in route["requirements"]


def test_flow_route_requires_product_but_not_independent_shift_drift():
    data = load_candidate()
    route = data["flow_adapted_product_route"]
    assert route["operator"] == "AND"
    assert "FPDG.GSC3.PRODUCT_TRIVIALIZATION" in route["requirements"]
    assert "FPDG.GSC4.GENERAL_MATCHING_SHIFT_DRIFT_PACKET" not in route["requirements"]
    assert "FPDG.GSC4.GSC3E_W0_SOURCE_BINDING" not in route["requirements"]
    assert route["independent_matching_shift_drift_packet_required"] is False
    assert route["derived_coordinate_specialization"] == {
        "matching_shift": "b=0",
        "temporal_spatial_drift": "v=0",
        "status": "EXACT_FLOW_ADAPTED_GAUGE",
    }


def test_both_routes_join_at_one_rfe25_packet():
    data = load_candidate()
    union = data["route_union"]
    assert union["operator"] == "OR"
    assert set(union["alternatives"]) == {
        "FPDG.GSC4.GENERAL_SOURCE_ASSEMBLED_RF_E25_PACKET",
        "FPDG.GSC4.FLOW_ADAPTED_SOURCE_ASSEMBLED_RF_E25_PACKET",
    }
    assert union["target"] == "FPDG.GSC4.SOURCE_ASSEMBLED_RF_E25_PACKET"
    assert data["rf_e25_handoff"]["from"] == union["target"]
    assert data["rf_e25_handoff"]["to"] == "RFC.E25.SHARED_SPACETIME_ATLAS"


def test_gsc3e_firewall_is_preserved_on_general_route():
    data = load_candidate()
    nodes = {node["id"]: node for node in data["candidate_nodes"]}
    assert nodes["FPDG.GSC4.GSC3E_W0_SOURCE_BINDING"]["status"] == "OPEN_SOURCE_BINDING"
    assert data["firewalls"]["affine_overlap_class_implies_gsc3e_w0_binding"] is False


def test_flow_zero_shift_does_not_zero_extrinsic_curvature():
    data = load_candidate()
    assert data["firewalls"]["flow_adapted_zero_shift_implies_zero_extrinsic_curvature"] is False


def test_source_theorems_have_hosted_success():
    data = load_candidate()
    src = data["source_validations"]
    assert src["gsc4a_general_source_assembly"]["conclusion"] == "success"
    assert src["gsc4b_flow_adapted_route"]["conclusion"] == "success"
    assert src["gsc3e_matching_source_firewall"]["conclusion"] == "success"


def test_live_two_route_audit_is_candidate_only():
    data = load_candidate()
    audit = data["live_36d_two_route_audit"]
    assert audit["authority"] == "CANDIDATE_ONLY"
    assert audit["promotion_evidence"] is False
    assert audit["shape"] == [13, 36]
    assert len(audit["terminal_receipt_sha256"]) == 64
    assert len(audit["phasenav_trace_sha256"]) == 64


def test_independent_rfe25_fields_are_reduced_on_both_source_routes():
    data = load_candidate()
    reduction = data["input_reduction"]
    assert reduction["independent_full_4d_jacobian_required"] is False
    assert reduction["independent_lorentz_transition_required"] is False
    assert reduction["independent_metric_tensor_required"] is False
    assert reduction["independent_metric_pullback_witness_required"] is False
