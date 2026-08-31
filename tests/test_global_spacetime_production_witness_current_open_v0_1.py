import json
from pathlib import Path

from tools.certify_global_spacetime_production_witness import certify_manifest


ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "interfaces" / "GLOBAL_SPACETIME_PRODUCTION_WITNESS_CURRENT_OPEN_V0_1.json"


def test_current_open_manifest_reports_all_nine_missing_event_spacetime_groups():
    manifest = json.loads(CURRENT.read_text(encoding="utf-8"))
    result = certify_manifest(manifest)
    assert result["status"] == "MISSING_WITNESSES"
    assert result["lineage_conflicts"] == []
    assert result["quarantined_witnesses"] == []
    assert set(result["missing_witnesses"]) == {
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
    assert result["production_promoted"] is False
    assert result["promotion_authority"] is False
