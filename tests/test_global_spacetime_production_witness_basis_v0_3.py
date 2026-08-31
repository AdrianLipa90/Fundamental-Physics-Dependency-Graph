import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "interfaces" / "GLOBAL_SPACETIME_PRODUCTION_WITNESS_BASIS_V0_3.json"


def load_doc():
    return json.loads(DOC.read_text(encoding="utf-8"))


def test_current_route_has_six_independent_groups():
    d = load_doc()
    assert d["independent_witness_group_count"] == 6
    assert d["independent_groups"] == [
        "W1_GSC1_SPATIAL_TOPOLOGY",
        "W2_GSC3A_GLOBAL_PRODUCT_CLOCK",
        "W3_GSC4_NUMERIC_SPATIAL_GEOMETRY",
        "W4_GSC4_PHASE_MAGNITUDE_SCALE_FIELD",
        "W5_IDT_GLOBAL_LAPSE",
        "W6_RF_E24_PATCHWISE_LOCAL_SOLUTIONS",
    ]
    assert "W7_TARGET_DOMAIN_COVERAGE" not in d["independent_groups"]


def test_w7_reduction_has_exact_route_requirements():
    d = load_doc()
    w7 = d["derived_group"]
    assert w7["id"] == "W7_TARGET_DOMAIN_COVERAGE"
    assert w7["status"] == "DERIVED_ON_CANONICAL_ATLAS_DOMAIN_ROUTE"
    req = set(w7["requirements"])
    assert "exact equality of W6 local-solution patch ids and production atlas patch ids" in req
    assert "target_domain_id=atlas_domain_id" in req
    assert w7["broader_target_domain_status"] == "OPEN_SEPARATE_EXTENSION_INPUT"


def test_nonreductions_preserve_independent_geometry_and_lapse():
    d = load_doc()
    nr = d["nonreductions_preserved"]
    assert nr["W1_plus_W4_implies_W3"] is False
    assert nr["W2_implies_W5"] is False
    assert nr["W6_count_equality_implies_W7"] is False


def test_event_and_matching_extensions_remain_separate():
    d = load_doc()
    assert set(d["event_extensions"]) == {
        "E1_GSC2_TEMPORAL_EVENT_COMPLEX",
        "E2_EVENT_SPATIAL_ANCHOR_BINDING",
    }
    assert d["conditional_general_matching_extension"] == "M1_SHARED_MATCHING_ONE_FORM_W0"


def test_minimality_claim_is_route_scoped():
    d = load_doc()
    mb = d["minimality_boundary"]
    assert mb["claim"] == "CURRENT_ROUTE_MINIMALITY_ONLY"
    assert mb["absolute_information_theoretic_minimality_claimed"] is False
    assert d["firewalls"]["broader_target_domain_coverage_removed"] is False
    assert d["firewalls"]["canonical_graph_mutated"] is False
