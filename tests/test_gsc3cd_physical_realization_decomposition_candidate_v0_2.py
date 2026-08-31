import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "interfaces" / "GSC3CD_PHYSICAL_REALIZATION_DECOMPOSITION_CANDIDATE_V0_2.json"


def load_candidate():
    return json.loads(CANDIDATE.read_text(encoding="utf-8"))


def test_candidate_remains_noncanonical_and_fail_closed():
    data = load_candidate()
    assert data["promotion_authority"] is False
    assert data["canonical_graph_mutation"] is False
    assert data["canon_mutations"] == []
    assert data["firewalls"]["gremlin_can_promote"] is False
    assert data["firewalls"]["terminal36d_can_promote"] is False
    assert data["firewalls"]["phasenav36d_can_promote"] is False
    assert data["firewalls"]["hosted_reference_pass_closes_production_inputs"] is False


def test_product_route_preserves_or_semantics():
    data = load_candidate()
    route = data["product_route"]
    assert route["operator"] == "AND"
    nested = next(item for item in route["requirements"] if isinstance(item, dict))
    assert nested["operator"] == "OR"
    assert set(nested["alternatives"]) == {
        "FPDG.GSC3CD.FLOW_COVERAGE",
        "FPDG.GSC3CD.CLOCK_PROPERNESS",
    }
    assert data["refinements_from_v0_1"]["flow_coverage_and_clock_properness_semantics"] == "OR"


def test_beta_shift_binding_is_reduced_to_provenance_identity():
    data = load_candidate()
    nodes = {node["id"]: node for node in data["candidate_nodes"]}
    assert nodes["FPDG.GSC3CD.BETA_SHIFT_INTERFACE_ALIAS"]["status"] == "HOSTED_PASS"
    assert nodes["FPDG.GSC3CD.SAME_PATCH_CLOCK_IDENTITY"]["status"] == "OPEN_PROVENANCE_INPUT"
    route = data["tir_rfc_kinematic_alias_route"]
    assert set(route["requirements"]) == {
        "FPDG.GSC3CD.BETA_SHIFT_INTERFACE_ALIAS",
        "FPDG.GSC3CD.SAME_PATCH_CLOCK_IDENTITY",
    }
    assert data["refinements_from_v0_1"]["broad_beta_match_shift_source_binding_replaced_by"] == "SAME_PATCH_CLOCK_IDENTITY"


def test_product_route_is_independent_of_kinematic_alias_provenance():
    data = load_candidate()
    product_requirements = data["product_route"]["requirements"]
    assert "FPDG.GSC3CD.SAME_PATCH_CLOCK_IDENTITY" not in product_requirements
    assert data["refinements_from_v0_1"]["product_route_separated_from_tir_rfc_kinematic_alias_route"] is True


def test_state_vertex_binding_is_supported_by_obstruction_theorem_but_remains_open():
    data = load_candidate()
    nodes = {node["id"]: node for node in data["candidate_nodes"]}
    assert nodes["FPDG.GSC3CD.STATE_VERTEX_RELABELING_OBSTRUCTION"]["status"] == "HOSTED_PASS"
    assert nodes["FPDG.GSC3CD.STATE_TO_TIR_SPATIAL_ANCHOR_BINDING"]["status"] == "OPEN_SOURCE_BINDING"
    assert data["event_route"]["theorem_parent"] == "FPDG.GSC3CD.STATE_VERTEX_RELABELING_OBSTRUCTION"
    assert data["refinements_from_v0_1"]["state_vertex_binding_open_input_explained_by"] == "EXACT_RELABELING_OBSTRUCTION_THEOREM"


def test_event_route_stays_separate_from_rfe25_atlas_route():
    data = load_candidate()
    event_requirements = set(data["event_route"]["requirements"])
    assert "RFC.E25.SHARED_SPACETIME_ATLAS" not in event_requirements
    assert data["firewalls"]["event_placement_is_rfe25_atlas_premise"] is False
    assert data["refinements_from_v0_1"]["event_route_separated_from_rfe25_atlas_route"] is True


def test_shared_atlas_requires_product_and_production_atlas_input():
    data = load_candidate()
    route = data["shared_atlas_route"]
    assert route["operator"] == "AND"
    assert set(route["requirements"]) == {
        "FPDG.GSC3CD.PRODUCT_TRIVIALIZATION",
        "FPDG.GSC3CD.RFE25_PRODUCTION_SHARED_ATLAS",
    }
    assert route["target"] == "RFC.E25.SHARED_SPACETIME_ATLAS"


def test_physical_event_spacetime_is_final_composition():
    data = load_candidate()
    composition = data["physical_event_spacetime_composition"]
    assert composition["operator"] == "AND"
    assert set(composition["requirements"]) == {
        "RFC.E25.SHARED_SPACETIME_ATLAS",
        "FPDG.GSC3CD.EVENT_PLACEMENT",
    }
    assert composition["target"] == "FPDG.GSC3CD.PHYSICAL_EVENT_ON_SHARED_SPACETIME"


def test_same_string_type_is_not_namespace_evidence():
    data = load_candidate()
    assert data["firewalls"]["same_string_type_implies_shared_namespace"] is False


def test_all_new_source_theorems_have_hosted_success():
    data = load_candidate()
    src = data["source_validations"]
    assert src["gsc3c_relabeling_obstruction"]["conclusion"] == "success"
    assert src["gsc3d_beta_shift_alias"]["conclusion"] == "success"
    assert src["gsc3b_event_placement"]["conclusion"] == "success"
    assert src["gsc3b_rfe9_crosslink"]["conclusion"] == "success"


def test_live_36d_audits_are_candidate_only():
    data = load_candidate()
    for audit in data["live_36d_audits"].values():
        assert audit["authority"] == "CANDIDATE_ONLY"
        assert audit["promotion_evidence"] is False
        assert len(audit["terminal_receipt_sha256"]) == 64
        assert len(audit["phasenav_trace_sha256"]) == 64
