import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FEDERATION = ROOT / "interfaces" / "GLOBAL_SPACETIME_CLOSURE_CANDIDATE_FEDERATION_V0_4.json"


def load_federation():
    return json.loads(FEDERATION.read_text(encoding="utf-8"))


def test_federation_remains_noncanonical():
    data = load_federation()
    assert data["promotion_authority"] is False
    assert data["canonical_graph_mutation"] is False
    assert data["canon_mutations"] == []
    assert data["firewalls"]["candidate_edge_enters_canonical_graph"] is False


def test_all_new_rfc_source_heads_are_hosted_success():
    data = load_federation()
    src = data["validated_source_heads"]
    for key in (
        "RFC_GSC3C_STATE_VERTEX",
        "RFC_GSC3D_MATCHING_ALIAS",
        "RFC_GSC3E_W0_FIREWALL",
        "RFC_GSC4A_GENERAL",
        "RFC_GSC4B_FLOW_ADAPTED",
    ):
        assert src[key]["conclusion"] == "success"


def test_gsc3_general_source_route_preserves_w0_firewall():
    data = load_federation()
    route = data["closure_routes"]["gsc3_general_kinematic_source"]
    assert route["operator"] == "AND"
    assert "FPDG.GSC3.SHARED_MATCHING_ONE_FORM_W0_BINDING" in route["requirements"]
    assert "FPDG.GSC3.BETA_SHIFT_INTERFACE_ALIAS" in route["requirements"]
    assert data["firewalls"]["same_patch_clock_ids_imply_shared_matching_one_form"] is False


def test_gsc4_general_route_does_not_require_product():
    data = load_federation()
    route = data["closure_routes"]["gsc4_general_patch_route"]
    assert route["product_trivialization_required"] is False
    assert "FPDG.GSC3.PRODUCT_TRIVIALIZATION" not in route["requirements"]
    assert "FPDG.GSC4.GSC3E_W0_SOURCE_BINDING" in route["requirements"]


def test_gsc4_flow_route_uses_product_and_derives_zero_shift_drift():
    data = load_federation()
    route = data["closure_routes"]["gsc4_flow_adapted_route"]
    assert "FPDG.GSC3.PRODUCT_TRIVIALIZATION" in route["requirements"]
    assert route["matching_shift_and_drift"] == "DERIVED_ZERO_IN_FLOW_ADAPTED_GAUGE"
    assert "FPDG.GSC4.GENERAL_MATCHING_SHIFT_DRIFT_PACKET" not in route["requirements"]
    assert data["firewalls"]["flow_adapted_zero_shift_implies_zero_extrinsic_curvature"] is False


def test_two_gsc4_routes_join_by_or_before_rfe25():
    data = load_federation()
    union = data["closure_routes"]["gsc4_union"]
    assert union["operator"] == "OR"
    assert set(union["alternatives"]) == {
        "FPDG.GSC4.GENERAL_SOURCE_ASSEMBLED_RF_E25_PACKET",
        "FPDG.GSC4.FLOW_ADAPTED_SOURCE_ASSEMBLED_RF_E25_PACKET",
    }
    assert data["closure_routes"]["gsc4_to_rfe25"]["from"] == union["target"]
    assert data["closure_routes"]["gsc4_to_rfe25"]["to"] == "RFC.E25.SHARED_SPACETIME_ATLAS"


def test_event_placement_remains_separate_from_atlas_construction():
    data = load_federation()
    comp = data["closure_routes"]["physical_event_composition"]
    assert set(comp["requirements"]) == {
        "RFC.E25.SHARED_SPACETIME_ATLAS",
        "FPDG.GSC3.EVENT_PLACEMENT",
    }
    assert data["firewalls"]["event_placement_is_required_for_rfe25_atlas_construction"] is False


def test_live_36d_latest_audit_is_candidate_only():
    data = load_federation()
    audit = data["live_36d_latest_dependency_audit"]
    assert audit["authority"] == "CANDIDATE_ONLY"
    assert audit["promotion_evidence"] is False
    assert audit["shape"] == [13, 36]
    assert len(audit["terminal_receipt_sha256"]) == 64
    assert len(audit["phasenav_trace_sha256"]) == 64
