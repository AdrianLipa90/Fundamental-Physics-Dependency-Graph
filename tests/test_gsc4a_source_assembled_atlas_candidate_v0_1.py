import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "interfaces" / "GSC4A_SOURCE_ASSEMBLED_ATLAS_CANDIDATE_V0_1.json"


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
    assert data["firewalls"]["hosted_reference_pass_closes_production_source_packet"] is False


def test_source_theorem_has_hosted_success():
    data = load_candidate()
    source = data["source_validation"]
    assert source["rfc_pr"] == 105
    assert source["reference_suite_run"] == 433
    assert source["conclusion"] == "success"


def test_full_rfe25_transition_fields_are_derived_on_source_assembled_class():
    data = load_candidate()
    derived = set(data["derived_rf_e25_coordinates"])
    assert derived == {
        "FULL_4D_COORDINATE_JACOBIAN_J",
        "LORENTZ_TRANSITION_LAMBDA",
        "ADM_COFRAME_E",
        "LORENTZ_METRIC_G",
        "METRIC_PULLBACK_WITNESS",
    }
    reduction = data["input_reduction"]
    assert reduction["independent_full_j_required"] is False
    assert reduction["independent_lorentz_transition_required"] is False
    assert reduction["independent_metric_tensor_required"] is False
    assert reduction["independent_metric_pullback_witness_required"] is False


def test_source_inputs_remain_explicitly_open():
    data = load_candidate()
    nodes = {node["id"]: node for node in data["candidate_nodes"]}
    for key in (
        "FPDG.GSC4A.TIR_SPATIAL_COFRAME_PACKET",
        "FPDG.GSC4A.TIR_SPATIAL_OVERLAP_COCYCLE_PACKET",
        "FPDG.GSC4A.IDT_SHARED_CLOCK_LAPSE_PACKET",
        "FPDG.GSC4A.MATCHING_SHIFT_DRIFT_PACKET",
        "FPDG.GSC4A.OVERLAP_COVERAGE",
    ):
        assert nodes[key]["status"] == "OPEN_PRODUCTION_INPUT"
    assert nodes["FPDG.GSC4A.PATCH_CLOCK_IDENTITY"]["status"] == "OPEN_PROVENANCE_INPUT"


def test_assembly_route_requires_product_and_source_packets():
    data = load_candidate()
    route = data["assembly_route"]
    assert route["operator"] == "AND"
    assert "FPDG.GSC3CD.PRODUCT_TRIVIALIZATION" in route["requirements"]
    assert "FPDG.GSC4A.SOURCE_ASSEMBLY_THEOREM" in route["requirements"]
    assert route["target"] == "FPDG.GSC4A.SOURCE_ASSEMBLED_RF_E25_PACKET"


def test_rfe25_handoff_reuses_existing_certifier():
    data = load_candidate()
    handoff = data["rf_e25_handoff"]
    assert handoff["from"] == "FPDG.GSC4A.SOURCE_ASSEMBLED_RF_E25_PACKET"
    assert handoff["to"] == "RFC.E25.SHARED_SPACETIME_ATLAS"
    assert handoff["authority"] == "CANDIDATE_ONLY"


def test_event_placement_stays_independent_of_atlas_assembly():
    data = load_candidate()
    assert data["firewalls"]["event_placement_is_required_for_rfe25_atlas_construction"] is False
    assert all("EVENT" not in item for item in data["assembly_route"]["requirements"])


def test_live_36d_evidence_is_audit_only():
    data = load_candidate()
    audit = data["live_36d_audit"]
    assert audit["authority"] == "CANDIDATE_ONLY"
    assert audit["promotion_evidence"] is False
    assert audit["shape"] == [7, 36]
    assert len(audit["terminal_receipt_sha256"]) == 64
    assert len(audit["phasenav_trace_sha256"]) == 64
