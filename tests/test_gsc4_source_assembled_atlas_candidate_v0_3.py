import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "interfaces" / "GSC4_SOURCE_ASSEMBLED_ATLAS_CANDIDATE_V0_3.json"


def load_candidate():
    return json.loads(CANDIDATE.read_text(encoding="utf-8"))


def test_candidate_remains_noncanonical():
    data = load_candidate()
    assert data["promotion_authority"] is False
    assert data["canonical_graph_mutation"] is False
    assert data["canon_mutations"] == []


def test_vertex_star_coverage_is_derived_from_gsc1_facets_and_a5():
    data = load_candidate()
    route = data["coverage_route"]
    assert set(route["requirements"]) == {
        "FPDG.GSC4.GSC1_TETRAHEDRAL_FACET_INPUT",
        "TIR.SPACE.GLOBAL_3MANIFOLD_A5",
    }
    assert route["independent_overlap_coverage_packet_required"] is False
    assert set(route["derived_outputs"]) == {
        "patch_ids",
        "pair_overlap_incidence",
        "triple_overlap_incidence",
    }


def test_general_route_uses_derived_coverage_not_an_open_coverage_packet():
    data = load_candidate()
    route = data["general_shared_clock_patch_route"]
    assert "FPDG.GSC4.VERTEX_STAR_COVERAGE" in route["requirements"]
    assert "FPDG.GSC4.OVERLAP_COVERAGE" not in route["requirements"]
    assert route["product_trivialization_required"] is False


def test_tir_bound_general_shift_requires_gsc3e_only_on_that_subroute():
    data = load_candidate()
    route = data["general_shared_clock_patch_route"]
    assert "FPDG.GSC4.GSC3E_W0_SOURCE_BINDING" not in route["requirements"]
    optional = route["optional_source_binding_subroute"]
    assert optional["additional_requirement"] == "FPDG.GSC4.GSC3E_W0_SOURCE_BINDING"


def test_flow_route_also_reuses_derived_vertex_star_coverage():
    data = load_candidate()
    route = data["flow_adapted_product_route"]
    assert "FPDG.GSC4.VERTEX_STAR_COVERAGE" in route["requirements"]
    assert "FPDG.GSC3.PRODUCT_TRIVIALIZATION" in route["requirements"]
    assert route["derived_coordinate_specialization"] == {
        "matching_shift": "b=0",
        "temporal_spatial_drift": "v=0",
    }


def test_coverage_theorem_does_not_generate_numeric_geometry():
    data = load_candidate()
    assert data["firewalls"]["vertex_star_coverage_generates_numeric_geometry"] is False
    nodes = {node["id"]: node for node in data["candidate_nodes"]}
    assert nodes["FPDG.GSC4.TIR_SPATIAL_COFRAME_PACKET"]["status"] == "OPEN_PRODUCTION_INPUT"
    assert nodes["FPDG.GSC4.IDT_SHARED_CLOCK_LAPSE_PACKET"]["status"] == "OPEN_PRODUCTION_INPUT"


def test_hosted_gsc4c_and_live_36d_audit_are_recorded_without_promotion():
    data = load_candidate()
    src = data["source_validations"]["gsc4c_vertex_star_coverage"]
    assert src["conclusion"] == "success"
    audit = data["live_36d_coverage_audit"]
    assert audit["authority"] == "CANDIDATE_ONLY"
    assert audit["promotion_evidence"] is False
    assert audit["shape"] == [14, 36]
