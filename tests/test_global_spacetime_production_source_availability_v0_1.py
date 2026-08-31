import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "interfaces" / "GLOBAL_SPACETIME_PRODUCTION_SOURCE_AVAILABILITY_V0_1.json"


def load_audit():
    return json.loads(AUDIT.read_text(encoding="utf-8"))


def test_all_current_production_slots_remain_open():
    data = load_audit()
    assert data["status"] == "AUDITED_NO_CERTIFIED_PRODUCTION_WITNESS_RESOLVED"
    assert set(data["availability"]) == {
        "W1_GSC1_SPATIAL_TOPOLOGY",
        "W2_GSC3A_GLOBAL_PRODUCT_CLOCK",
        "W3_GSC4_NUMERIC_SPATIAL_GEOMETRY",
        "W4_GSC4_PHASE_MAGNITUDE_SCALE_FIELD",
        "W5_IDT_GLOBAL_LAPSE",
        "W6_RF_E24_PATCHWISE_LOCAL_SOLUTIONS",
        "W7_TARGET_DOMAIN_COVERAGE",
        "E1_GSC2_TEMPORAL_EVENT_COMPLEX",
        "E2_EVENT_SPATIAL_ANCHOR_BINDING",
    }
    assert all(item["status"] == "OPEN" for item in data["availability"].values())


def test_reference_and_runtime_substitutions_are_blocked():
    fw = load_audit()["firewalls"]
    assert fw["candidate_or_reference_artifact_fills_production_slot"] is False
    assert fw["live_tooling_event_bus_is_IDT_production_event_complex"] is False
    assert fw["availability_audit_can_promote"] is False


def test_acquisition_priority_separates_gr_and_event_targets():
    priority = load_audit()["acquisition_priority"]
    assert priority["for_global_GR_Cauchy_carrier"]["first"] == "W1_GSC1_SPATIAL_TOPOLOGY"
    assert priority["for_event_realization_extension"]["first"] == "E1_GSC2_TEMPORAL_EVENT_COMPLEX"


def test_live_audit_is_candidate_only_and_hash_complete():
    audit = load_audit()["live_36d_audit"]
    assert audit["authority"] == "CANDIDATE_ONLY"
    assert audit["promotion_evidence"] is False
    assert len(audit["terminal_receipt_sha256"]) == 64
    assert len(audit["phasenav_trace_sha256"]) == 64
    assert audit["shape"] == [8, 36]
