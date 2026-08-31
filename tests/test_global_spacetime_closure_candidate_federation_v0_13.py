import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "interfaces" / "GLOBAL_SPACETIME_CLOSURE_CANDIDATE_FEDERATION_V0_13.json"


def load_candidate():
    return json.loads(CANDIDATE.read_text(encoding="utf-8"))


def test_candidate_stays_noncanonical_and_runtime_cannot_promote():
    data = load_candidate()
    assert data["promotion_authority"] is False
    assert data["canonical_graph_mutation"] is False
    assert data["canon_mutations"] == []
    assert data["live_36d_audit"]["authority"] == "CANDIDATE_ONLY"
    assert data["live_36d_audit"]["promotion_evidence"] is False
    assert data["firewalls"]["runtime_audit_can_promote"] is False


def test_source_validation_uses_refined_gsc6c_pr117_and_two_green_heads():
    data = load_candidate()["source_validation"]
    assert data["rfc_pr"] == 117
    assert data["supersedes_rfc_pr"] == 116
    assert data["theorem_reference_suite_run"] == 481
    assert data["receipt_reference_suite_run"] == 482
    assert data["conclusion"] == "success"


def test_gsc6c_route_requires_product_provenance_independent_of_proper_clock():
    data = load_candidate()
    route = next(
        item
        for item in data["gsc6_routes"]["alternatives"]
        if item["id"] == "RFC_GSC6C_ACYCLIC_COMPACT_FIBER_PRODUCT"
    )
    nested = next(item for item in route["requirements"] if isinstance(item, dict))
    assert nested["operator"] == "OR"
    assert set(nested["alternatives"]) == {
        "GSC3A_FLOW_COVERAGE_PRODUCT_PROVENANCE",
        "INDEPENDENT_PRODUCT_SOURCE_RECEIPT_NO_PROPER_CLOCK_ANCESTRY",
    }
    assert "SMOOTH_FINITE_POSITIVE_LAPSE" in route["requirements"]


def test_clock_properness_product_ancestry_is_explicitly_blocked_from_elimination_route():
    data = load_candidate()
    firewall = data["product_provenance_firewall"]
    assert firewall["forbidden_dependency_cycle"] == "PROPER_CLOCK -> PRODUCT_TRIVIALIZATION -> PROPER_CLOCK"
    assert "GSC3_CLOCK_PROPERNESS_ROUTE" in firewall["not_admitted_for_GSC6C_proper_clock_elimination"]
    assert data["firewalls"]["gsc6c_reuses_clock_properness_to_construct_its_product_parent"] is False
    assert data["firewalls"]["unknown_product_provenance_can_remove_proper_clock_input"] is False


def test_adm_time_transport_is_derived_not_an_independent_witness():
    data = load_candidate()
    exact = set(data["refinement"]["exact_derivations"])
    assert "ADM_TIME_TRANSPORT_N_TAU_EQUALS_N_T_OVER_PSI_PRIME" in exact
    assert "ADM_TIME_TRANSPORT_B_TAU_EQUALS_B_T_OVER_PSI_PRIME" in exact
    removed = set(data["refinement"]["derived_coordinates_removed_from_production_frontier_on_this_route"])
    assert "SEPARATELY_SUPPLIED_REPARAMETRIZED_LAPSE_FIELD" in removed
    assert "SEPARATELY_SUPPLIED_REPARAMETRIZED_SHIFT_FIELD" in removed


def test_gsc5_remains_required_for_full_gr_cauchy_composition():
    data = load_candidate()["global_gr_cauchy_composition"]
    assert data["operator"] == "AND"
    assert set(data["requirements"]) == {
        "RFC_E26_GSC5_PRODUCTION_GLOBAL_EINSTEIN_CARRIER",
        "GSC6_GLOBAL_HYPERBOLICITY_CAUCHY_FOLIATION",
    }


def test_live_36d_hashes_are_well_formed():
    audit = load_candidate()["live_36d_audit"]
    assert len(audit["terminal_receipt_sha256"]) == 64
    assert len(audit["phasenav_trace_sha256"]) == 64
    assert audit["shape"] == [10, 36]
