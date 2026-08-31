import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FEDERATION = ROOT / "interfaces" / "GLOBAL_SPACETIME_CLOSURE_CANDIDATE_FEDERATION_V0_5.json"


def load_federation():
    return json.loads(FEDERATION.read_text(encoding="utf-8"))


def test_noncanonical_authority_firewall():
    data = load_federation()
    assert data["promotion_authority"] is False
    assert data["canonical_graph_mutation"] is False
    assert data["canon_mutations"] == []
    assert data["firewalls"]["gremlin_can_promote"] is False


def test_gsc4_coverage_is_removed_from_independent_open_frontier():
    data = load_federation()
    gsc4 = data["open_frontier"]["GSC4"]
    assert not any("COVERAGE" in item for item in gsc4)
    eliminated = data["derived_or_eliminated_from_frontier"]
    assert "GSC4_OVERLAP_COVERAGE_AS_INDEPENDENT_INPUT_ON_VERTEX_STAR_ROUTE" in eliminated
    assert "GSC4_PAIR_TRIPLE_OVERLAP_INCIDENCE_AS_INDEPENDENT_INPUT_ON_VERTEX_STAR_ROUTE" in eliminated


def test_spatial_topology_generates_vertex_star_cover_but_not_numeric_geometry():
    data = load_federation()
    route = data["global_routes"]["spatial_topology_to_atlas_cover"]
    assert set(route["requirements"]) == {
        "GSC1_PRODUCTION_TETRAHEDRAL_FACET_LIST",
        "TIR.SPACE.GLOBAL_3MANIFOLD_A5",
    }
    assert route["target"] == "FPDG.GSC4.VERTEX_STAR_COVERAGE"
    assert data["firewalls"]["a5_facet_incidence_determines_numeric_coframe_geometry"] is False


def test_event_clock_exactness_does_not_silently_supply_lapse():
    data = load_federation()
    assert data["firewalls"]["event_clock_exactness_determines_lapse_ratio"] is False
    assert "IDT_SHARED_CLOCK_LAPSE_AND_CALIBRATION" in data["open_frontier"]["GSC4"]


def test_gsc4_route_union_still_targets_rfe25():
    data = load_federation()
    route = data["global_routes"]["gsc4_atlas"]
    assert route["operator"] == "OR"
    assert route["target"] == "RFC.E25.SHARED_SPACETIME_ATLAS"
    assert set(route["alternatives"]) == {
        "FPDG.GSC4.GENERAL_SOURCE_ASSEMBLED_RF_E25_PACKET",
        "FPDG.GSC4.FLOW_ADAPTED_SOURCE_ASSEMBLED_RF_E25_PACKET",
    }


def test_physical_event_composition_remains_separate():
    data = load_federation()
    route = data["global_routes"]["physical_event_on_atlas"]
    assert set(route["requirements"]) == {
        "RFC.E25.SHARED_SPACETIME_ATLAS",
        "FPDG.GSC3.EVENT_PLACEMENT",
    }


def test_live_audits_have_36d_shape_and_no_promotion_authority():
    data = load_federation()
    audits = data["live_36d_audits"]
    assert audits["authority"] == "CANDIDATE_ONLY"
    assert audits["promotion_evidence"] is False
    assert audits["two_route_gsc4"]["shape"] == [13, 36]
    assert audits["gsc4c_coverage"]["shape"] == [14, 36]
