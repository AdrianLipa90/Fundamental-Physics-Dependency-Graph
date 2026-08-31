from copy import deepcopy

from tools.certify_global_spacetime_production_witness import (
    FLOW_ROUTE,
    GENERAL_ROUTE,
    TARGET_EVENT,
    TARGET_GR,
    certify_manifest,
)


COMMIT = "a" * 40
DIGEST = "b" * 64


def certified(**lineage):
    return {
        "status": "CERTIFIED_PRODUCTION",
        "receipt": {
            "repository": "AdrianLipa90/example",
            "commit": COMMIT,
            "path": "validation/example.json",
            "sha256": DIGEST,
        },
        "lineage": lineage,
    }


def base_manifest(target=TARGET_GR, route=FLOW_ROUTE):
    witnesses = {
        "W1_GSC1_SPATIAL_TOPOLOGY": certified(
            spatial_carrier_id="sigma-prod-1", cover_id="cover-1"
        ),
        "W2_GSC3A_GLOBAL_PRODUCT_CLOCK": certified(
            spatial_carrier_id="sigma-prod-1",
            clock_id="clock-prod-1",
            realization_id="spacetime-prod-1",
            product_provenance="FLOW_COVERAGE",
        ),
        "W3_GSC4_NUMERIC_SPATIAL_GEOMETRY": certified(
            spatial_carrier_id="sigma-prod-1", cover_id="cover-1"
        ),
        "W4_GSC4_PHASE_MAGNITUDE_SCALE_FIELD": certified(
            spatial_carrier_id="sigma-prod-1", clock_id="clock-prod-1"
        ),
        "W5_IDT_GLOBAL_LAPSE": certified(clock_id="clock-prod-1"),
        "W6_RF_E24_PATCHWISE_LOCAL_SOLUTIONS": certified(
            domain_id="domain-prod-1", source_lineage_id="source-prod-1"
        ),
        "W7_TARGET_DOMAIN_COVERAGE": certified(domain_id="domain-prod-1"),
    }
    if target == TARGET_EVENT:
        witnesses["E1_GSC2_TEMPORAL_EVENT_COMPLEX"] = certified(
            clock_id="clock-prod-1", event_complex_id="events-prod-1"
        )
        witnesses["E2_EVENT_SPATIAL_ANCHOR_BINDING"] = certified(
            spatial_carrier_id="sigma-prod-1", event_complex_id="events-prod-1"
        )
    if route == GENERAL_ROUTE:
        witnesses["M1_SHARED_MATCHING_ONE_FORM_W0"] = certified(
            clock_id="clock-prod-1", realization_id="spacetime-prod-1"
        )
    return {
        "schema": "FPDG_GLOBAL_SPACETIME_PRODUCTION_WITNESS_V0_1",
        "target": target,
        "route": route,
        "witnesses": witnesses,
    }


def test_complete_flow_route_is_ready_for_source_resolution_only():
    result = certify_manifest(base_manifest())
    assert result["status"] == "READY_FOR_SOURCE_RESOLUTION"
    assert result["all_required_slots_certified"] is True
    assert result["source_receipt_resolution_required"] is True
    assert result["production_promoted"] is False
    assert result["promotion_authority"] is False


def test_flow_coverage_product_provenance_is_admitted():
    manifest = base_manifest()
    assert manifest["witnesses"]["W2_GSC3A_GLOBAL_PRODUCT_CLOCK"]["lineage"]["product_provenance"] == "FLOW_COVERAGE"
    result = certify_manifest(manifest)
    assert result["status"] == "READY_FOR_SOURCE_RESOLUTION"


def test_clock_properness_product_provenance_is_rejected_as_dependency_cycle():
    manifest = base_manifest()
    lineage = manifest["witnesses"]["W2_GSC3A_GLOBAL_PRODUCT_CLOCK"]["lineage"]
    lineage["product_provenance"] = "CLOCK_PROPERNESS"
    result = certify_manifest(manifest)
    assert result["status"] == "LINEAGE_CONFLICTS"
    assert "W2_GSC3A_GLOBAL_PRODUCT_CLOCK:PROPER_CLOCK_ANCESTRY_CYCLE" in result["lineage_conflicts"]


def test_missing_product_provenance_is_fail_closed():
    manifest = base_manifest()
    manifest["witnesses"]["W2_GSC3A_GLOBAL_PRODUCT_CLOCK"]["lineage"].pop("product_provenance")
    result = certify_manifest(manifest)
    assert result["status"] == "LINEAGE_CONFLICTS"
    assert "W2_GSC3A_GLOBAL_PRODUCT_CLOCK:MISSING_PRODUCT_PROVENANCE" in result["lineage_conflicts"]


def test_independent_source_product_requires_explicit_no_proper_clock_ancestry():
    manifest = base_manifest()
    lineage = manifest["witnesses"]["W2_GSC3A_GLOBAL_PRODUCT_CLOCK"]["lineage"]
    lineage["product_provenance"] = "INDEPENDENT_SOURCE_RECEIPT"
    result_blocked = certify_manifest(manifest)
    assert result_blocked["status"] == "LINEAGE_CONFLICTS"
    assert "W2_GSC3A_GLOBAL_PRODUCT_CLOCK:INDEPENDENT_PRODUCT_ANCESTRY_NOT_CERTIFIED" in result_blocked["lineage_conflicts"]

    lineage["no_proper_clock_ancestry"] = True
    result_admitted = certify_manifest(manifest)
    assert result_admitted["status"] == "READY_FOR_SOURCE_RESOLUTION"


def test_unsupported_product_provenance_is_fail_closed():
    manifest = base_manifest()
    manifest["witnesses"]["W2_GSC3A_GLOBAL_PRODUCT_CLOCK"]["lineage"]["product_provenance"] = "UNDECLARED"
    result = certify_manifest(manifest)
    assert result["status"] == "LINEAGE_CONFLICTS"
    assert "W2_GSC3A_GLOBAL_PRODUCT_CLOCK:UNSUPPORTED_PRODUCT_PROVENANCE:UNDECLARED" in result["lineage_conflicts"]


def test_missing_required_group_is_reported():
    manifest = base_manifest()
    manifest["witnesses"].pop("W3_GSC4_NUMERIC_SPATIAL_GEOMETRY")
    result = certify_manifest(manifest)
    assert result["status"] == "MISSING_WITNESSES"
    assert "W3_GSC4_NUMERIC_SPATIAL_GEOMETRY" in result["missing_witnesses"]


def test_open_required_group_is_reported_without_fake_receipt():
    manifest = base_manifest()
    manifest["witnesses"]["W5_IDT_GLOBAL_LAPSE"] = {
        "status": "OPEN",
        "lineage": {"clock_id": "clock-prod-1"},
    }
    result = certify_manifest(manifest)
    assert result["status"] == "MISSING_WITNESSES"
    assert "W5_IDT_GLOBAL_LAPSE" in result["missing_witnesses"]


def test_clock_lineage_conflict_is_fail_closed():
    manifest = base_manifest()
    manifest["witnesses"]["W5_IDT_GLOBAL_LAPSE"]["lineage"]["clock_id"] = "clock-other"
    result = certify_manifest(manifest)
    assert result["status"] == "LINEAGE_CONFLICTS"
    assert any(item.startswith("CLOCK_ID_CONFLICT:") for item in result["lineage_conflicts"])


def test_spatial_and_domain_conflicts_are_separate():
    manifest = base_manifest()
    manifest["witnesses"]["W3_GSC4_NUMERIC_SPATIAL_GEOMETRY"]["lineage"]["spatial_carrier_id"] = "sigma-other"
    manifest["witnesses"]["W7_TARGET_DOMAIN_COVERAGE"]["lineage"]["domain_id"] = "domain-other"
    result = certify_manifest(manifest)
    assert result["status"] == "LINEAGE_CONFLICTS"
    assert any(item.startswith("SPATIAL_CARRIER_ID_CONFLICT:") for item in result["lineage_conflicts"])
    assert any(item.startswith("DOMAIN_ID_CONFLICT:") for item in result["lineage_conflicts"])


def test_event_target_requires_event_complex_and_spatial_binding():
    manifest = base_manifest(target=TARGET_EVENT)
    result = certify_manifest(manifest)
    assert result["status"] == "READY_FOR_SOURCE_RESOLUTION"
    assert "E1_GSC2_TEMPORAL_EVENT_COMPLEX" in result["required_groups"]
    assert "E2_EVENT_SPATIAL_ANCHOR_BINDING" in result["required_groups"]


def test_event_complex_lineage_conflict_is_detected():
    manifest = base_manifest(target=TARGET_EVENT)
    manifest["witnesses"]["E2_EVENT_SPATIAL_ANCHOR_BINDING"]["lineage"]["event_complex_id"] = "events-other"
    result = certify_manifest(manifest)
    assert result["status"] == "LINEAGE_CONFLICTS"
    assert any(item.startswith("EVENT_COMPLEX_ID_CONFLICT:") for item in result["lineage_conflicts"])


def test_general_matching_route_requires_w0_binding():
    manifest = base_manifest(route=GENERAL_ROUTE)
    result = certify_manifest(manifest)
    assert result["status"] == "READY_FOR_SOURCE_RESOLUTION"
    assert "M1_SHARED_MATCHING_ONE_FORM_W0" in result["required_groups"]

    missing = deepcopy(manifest)
    missing["witnesses"].pop("M1_SHARED_MATCHING_ONE_FORM_W0")
    result_missing = certify_manifest(missing)
    assert result_missing["status"] == "MISSING_WITNESSES"
    assert "M1_SHARED_MATCHING_ONE_FORM_W0" in result_missing["missing_witnesses"]


def test_flow_route_does_not_require_w0_binding():
    result = certify_manifest(base_manifest(route=FLOW_ROUTE))
    assert "M1_SHARED_MATCHING_ONE_FORM_W0" not in result["required_groups"]
    assert result["status"] == "READY_FOR_SOURCE_RESOLUTION"


def test_invalid_receipt_digest_is_conflict():
    manifest = base_manifest()
    manifest["witnesses"]["W1_GSC1_SPATIAL_TOPOLOGY"]["receipt"]["sha256"] = "bad"
    result = certify_manifest(manifest)
    assert result["status"] == "LINEAGE_CONFLICTS"
    assert "W1_GSC1_SPATIAL_TOPOLOGY:INVALID_RECEIPT_SHA256" in result["lineage_conflicts"]


def test_quarantined_witness_is_reported_separately():
    manifest = base_manifest()
    manifest["witnesses"]["W6_RF_E24_PATCHWISE_LOCAL_SOLUTIONS"]["status"] = "QUARANTINED"
    result = certify_manifest(manifest)
    assert result["status"] == "QUARANTINED_WITNESSES"
    assert "W6_RF_E24_PATCHWISE_LOCAL_SOLUTIONS" in result["quarantined_witnesses"]
