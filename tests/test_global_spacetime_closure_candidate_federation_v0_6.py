import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FEDERATION = ROOT / "interfaces" / "GLOBAL_SPACETIME_CLOSURE_CANDIDATE_FEDERATION_V0_6.json"


def load_federation():
    return json.loads(FEDERATION.read_text(encoding="utf-8"))


def test_candidate_remains_noncanonical_and_fail_closed():
    data = load_federation()
    assert data["promotion_authority"] is False
    assert data["canonical_graph_mutation"] is False
    assert data["canon_mutations"] == []
    assert data["firewalls"]["gremlin_can_promote"] is False
    assert data["firewalls"]["terminal36d_can_promote"] is False
    assert data["firewalls"]["phasenav36d_can_promote"] is False


def test_spatial_geometry_packet_is_or_between_raw_and_rigid_routes():
    data = load_federation()
    route = data["gsc4_spatial_geometry_packet"]
    assert route["operator"] == "OR"
    assert route["target"] == "FPDG.GSC4.SPATIAL_GEOMETRY_PACKET"
    names = {item["route"] for item in route["alternatives"]}
    assert names == {"GENERAL_SOURCE_PACKET", "ANCHORED_PHASE_SCALED_RIGID_PACKET"}


def test_rigid_route_reduces_e_a_r_but_keeps_source_packet_open():
    data = load_federation()
    rigid = next(
        item
        for item in data["gsc4_spatial_geometry_packet"]["alternatives"]
        if item["route"] == "ANCHORED_PHASE_SCALED_RIGID_PACKET"
    )
    assert set(rigid["requirements"]) == {
        "FPDG.GSC4D.HOSTED_THEOREM",
        "FPDG.GSC4D.PRODUCTION_ANCHOR_VECTORS",
        "FPDG.GSC4D.PRODUCTION_SO3_FRAME_MATRICES",
        "FPDG.GSC4D.PRODUCTION_FINITE_NONZERO_PHASE_RATE_FIELD",
        "FPDG.GSC4D.PRODUCTION_SHARED_PHASE_SCALE_BINDING",
    }
    assert "INDEPENDENT_E_A_R_MATRICES_ON_GSC4D_RIGID_ROUTE" in data["derived_or_eliminated_from_frontier"]
    assert "GENERAL_RAW_SPATIAL_PACKET_OR_GSC4D_ANCHOR_FRAME_PHASE_PACKET" in data["open_frontier"]["GSC4"]


def test_rigid_route_does_not_leak_into_general_atlas_semantics():
    data = load_federation()
    fw = data["gsc4d_firewalls"]
    assert fw["a_equals_r_is_general_smooth_atlas_identity"] is False
    assert fw["a5_incidence_determines_numeric_anchor_frame_phase_packet"] is False
    assert fw["hosted_pass_closes_production_anchor_frame_phase_packet"] is False


def test_phase_rate_remains_distinct_from_idt_lapse():
    data = load_federation()
    assert data["gsc4d_firewalls"]["phase_rate_determines_idt_lapse"] is False
    assert "IDT_SHARED_CLOCK_LAPSE_AND_CALIBRATION" in data["open_frontier"]["GSC4"]


def test_general_and_flow_routes_consume_the_same_spatial_packet_abstraction():
    data = load_federation()
    general = data["global_routes"]["general_gsc4a_atlas"]["requirements"]
    flow = data["global_routes"]["flow_adapted_gsc4b_atlas"]["requirements"]
    assert "FPDG.GSC4.SPATIAL_GEOMETRY_PACKET" in general
    assert "FPDG.GSC4.SPATIAL_GEOMETRY_PACKET" in flow
    assert "FPDG.GSC3.PRODUCT_TRIVIALIZATION" not in general
    assert "FPDG.GSC3.PRODUCT_TRIVIALIZATION" in flow


def test_gsc4_union_still_targets_rfe25():
    data = load_federation()
    route = data["global_routes"]["gsc4_atlas"]
    assert route["operator"] == "OR"
    assert route["target"] == "RFC.E25.SHARED_SPACETIME_ATLAS"
    assert set(route["alternatives"]) == {
        "FPDG.GSC4.GENERAL_SOURCE_ASSEMBLED_RF_E25_PACKET",
        "FPDG.GSC4.FLOW_ADAPTED_SOURCE_ASSEMBLED_RF_E25_PACKET",
    }


def test_fresh_triad_receipt_is_36d_and_candidate_only():
    data = load_federation()
    audits = data["live_36d_audits"]
    assert audits["authority"] == "CANDIDATE_ONLY"
    assert audits["promotion_evidence"] is False
    audit = audits["gsc4d_fresh_post_test_fix"]
    assert audit["shape"] == [11, 36]
    assert len(audit["terminal_receipt_sha256"]) == 64
    assert len(audit["phasenav_trace_sha256"]) == 64
