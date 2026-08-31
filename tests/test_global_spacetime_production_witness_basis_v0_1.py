import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASIS = ROOT / "interfaces" / "GLOBAL_SPACETIME_PRODUCTION_WITNESS_BASIS_V0_1.json"


def load_basis():
    return json.loads(BASIS.read_text(encoding="utf-8"))


def test_basis_remains_noncanonical_and_candidate_only():
    data = load_basis()
    assert data["promotion_authority"] is False
    assert data["canonical_graph_mutation"] is False
    assert data["canon_mutations"] == []
    assert data["live_36d_audit"]["authority"] == "CANDIDATE_ONLY"
    assert data["live_36d_audit"]["promotion_evidence"] is False
    assert data["firewalls"]["runtime_audit_can_promote"] is False


def test_global_gr_cauchy_basis_has_seven_independent_groups():
    data = load_basis()
    groups = data["global_gr_cauchy_carrier_basis"]["witness_groups"]
    ids = [g["id"] for g in groups]
    assert ids == [
        "W1_GSC1_SPATIAL_TOPOLOGY",
        "W2_GSC3A_GLOBAL_PRODUCT_CLOCK",
        "W3_GSC4_NUMERIC_SPATIAL_GEOMETRY",
        "W4_GSC4_PHASE_MAGNITUDE_SCALE_FIELD",
        "W5_IDT_GLOBAL_LAPSE",
        "W6_RF_E24_PATCHWISE_LOCAL_SOLUTIONS",
        "W7_TARGET_DOMAIN_COVERAGE",
    ]


def test_event_realization_is_separate_extension():
    data = load_basis()
    ext = data["event_realization_extension_basis"]
    ids = {g["id"] for g in ext["additional_witness_groups"]}
    assert ids == {
        "E1_GSC2_TEMPORAL_EVENT_COMPLEX",
        "E2_EVENT_SPATIAL_ANCHOR_BINDING",
    }
    assert data["firewalls"]["event_realization_is_required_for_pure_tensor_global_GR_Cauchy_carrier"] is False


def test_flow_adapted_route_avoids_general_matching_w0_input():
    data = load_basis()
    assert data["conditional_general_matching_route_extension"]["additional_witness"]["id"] == "M1_SHARED_MATCHING_ONE_FORM_W0"
    assert data["firewalls"]["general_matching_W0_witness_is_required_on_flow_adapted_route"] is False


def test_known_derived_coordinates_are_excluded():
    data = load_basis()
    excluded = set(data["derived_coordinates_excluded_from_independent_basis"])
    assert "vertex-star pair/triple overlap incidence beyond GSC1 facets" in excluded
    assert "independent G/T/Einstein-residual overlap matrices on the GSC5A route" in excluded
    assert "separate proper R-clock witness on the GSC6C route" in excluded
    assert "separate global finite lapse bound N_max on the GSC6C route" in excluded
    assert "separate complete W witness on the GSC6C route" in excluded
    assert "separate complete H_N witness on the GSC6C route" in excluded


def test_basis_does_not_claim_absolute_minimality():
    data = load_basis()
    boundary = data["minimality_boundary"]
    assert boundary["claim"] == "CURRENT_ROUTE_MINIMALITY_ONLY"
    assert boundary["absolute_information_theoretic_minimality_claimed"] is False


def test_live_audit_hashes_have_expected_shape():
    audit = load_basis()["live_36d_audit"]
    assert len(audit["terminal_receipt_sha256"]) == 64
    assert len(audit["phasenav_trace_sha256"]) == 64
    assert audit["shape"] == [19, 36]
