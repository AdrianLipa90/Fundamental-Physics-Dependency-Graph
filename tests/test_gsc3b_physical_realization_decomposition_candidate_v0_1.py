import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "interfaces" / "GSC3B_PHYSICAL_REALIZATION_DECOMPOSITION_CANDIDATE_V0_1.json"


def load_candidate():
    return json.loads(CANDIDATE.read_text(encoding="utf-8"))


def test_candidate_is_noncanonical_and_fail_closed():
    data = load_candidate()
    assert data["promotion_authority"] is False
    assert data["canonical_graph_mutation"] is False
    assert data["canon_mutations"] == []
    assert data["firewalls"]["gremlin_can_promote"] is False
    assert data["firewalls"]["terminal36d_can_promote"] is False
    assert data["firewalls"]["phasenav36d_can_promote"] is False
    assert data["firewalls"]["hosted_reference_pass_closes_production_inputs"] is False


def test_geometry_route_keeps_or_semantics_for_global_coverage():
    data = load_candidate()
    route = data["geometry_route"]
    assert route["operator"] == "AND"
    nested = next(item for item in route["requirements"] if isinstance(item, dict))
    assert nested["operator"] == "OR"
    assert set(nested["alternatives"]) == {
        "FPDG.GSC3B.FLOW_COVERAGE",
        "FPDG.GSC3B.CLOCK_PROPERNESS",
    }
    assert data["important_separation"]["flow_coverage_and_clock_properness_are_or"] is True
    assert data["important_separation"]["flow_coverage_and_clock_properness_are_and"] is False


def test_beta_match_shift_binding_remains_independent_open_input():
    data = load_candidate()
    nodes = {node["id"]: node for node in data["candidate_nodes"]}
    node = nodes["FPDG.GSC3B.BETA_MATCH_SHIFT_SOURCE_BINDING"]
    assert node["status"] == "OPEN_SOURCE_BINDING"
    assert "FPDG.GSC3B.BETA_MATCH_SHIFT_SOURCE_BINDING" in data["geometry_route"]["requirements"]
    assert data["important_separation"]["beta_match_shift_binding_is_required_for_matching_flow_to_rfe9_physical_crosslink"] is True


def test_event_route_is_independent_of_rfe25_atlas_certification():
    data = load_candidate()
    event_requirements = set(data["event_route"]["requirements"])
    assert "RFC.E25.SHARED_SPACETIME_ATLAS" not in event_requirements
    assert data["important_separation"]["event_placement_is_premise_of_rfe25_algebraic_atlas_certifier"] is False
    assert data["important_separation"]["event_placement_is_required_for_full_physical_event_spacetime_realization"] is True


def test_event_route_keeps_source_and_production_inputs_open():
    data = load_candidate()
    nodes = {node["id"]: node for node in data["candidate_nodes"]}
    assert nodes["FPDG.GSC3B.PRODUCTION_EVENT_COMPLEX"]["status"] == "OPEN_PRODUCTION_INPUT"
    assert nodes["FPDG.GSC3B.PRODUCTION_OCCURRENCE_STATE_TABLE"]["status"] == "OPEN_PRODUCTION_INPUT"
    assert nodes["FPDG.GSC3B.STATE_TO_TIR_SPATIAL_ANCHOR_BINDING"]["status"] == "OPEN_SOURCE_BINDING"
    assert nodes["FPDG.GSC3B.QUOTIENT_FIBRE_CONSTANCY"]["status"] == "EXACT_EXECUTABLE_GATE"


def test_full_physical_event_spacetime_is_composition_not_atlas_premise():
    data = load_candidate()
    composition = data["composition"]
    assert composition["operator"] == "AND"
    assert set(composition["requirements"]) == {
        "RFC.E25.SHARED_SPACETIME_ATLAS",
        "FPDG.GSC3B.EVENT_PLACEMENT",
    }
    assert composition["target"] == "FPDG.GSC3B.PHYSICAL_EVENT_ON_SHARED_SPACETIME"


def test_all_three_source_surfaces_are_hosted_validated():
    data = load_candidate()
    src = data["source_validations"]
    assert src["gsc3a_matching_flow"]["conclusion"] == "success"
    assert src["relational_event_placement"]["dedicated_conclusion"] == "success"
    assert src["relational_event_placement"]["reference_suite_conclusion"] == "success"
    assert src["matching_flow_rfe9_crosslink"]["conclusion"] == "success"


def test_live_36d_trace_is_audit_only():
    data = load_candidate()
    audit = data["live_36d_audit"]
    assert audit["authority"] == "CANDIDATE_ONLY"
    assert audit["promotion_evidence"] is False
    assert audit["shape"] == [13, 36]
    assert len(audit["terminal_receipt_sha256"]) == 64
    assert len(audit["phasenav_trace_sha256"]) == 64
