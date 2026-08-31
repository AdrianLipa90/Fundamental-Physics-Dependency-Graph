from tools.certify_global_spacetime_production_witness import (
    CANONICAL_ATLAS_ROUTE,
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


def canonical_manifest():
    patch_ids = ["star:0", "star:1", "star:2", "star:3"]
    return {
        "schema": "FPDG_GLOBAL_SPACETIME_PRODUCTION_WITNESS_V0_1",
        "target": TARGET_GR,
        "route": CANONICAL_ATLAS_ROUTE,
        "witnesses": {
            "W1_GSC1_SPATIAL_TOPOLOGY": certified(
                spatial_carrier_id="sigma-prod-1",
                cover_id="cover-1",
            ),
            "W2_GSC3A_GLOBAL_PRODUCT_CLOCK": certified(
                spatial_carrier_id="sigma-prod-1",
                clock_id="clock-prod-1",
                realization_id="spacetime-prod-1",
                cover_id="cover-1",
                product_provenance="FLOW_COVERAGE",
                canonical_atlas_coverage_certified=True,
                atlas_patch_ids=patch_ids,
                atlas_domain_id="domain-prod-1",
            ),
            "W3_GSC4_NUMERIC_SPATIAL_GEOMETRY": certified(
                spatial_carrier_id="sigma-prod-1",
                cover_id="cover-1",
            ),
            "W4_GSC4_PHASE_MAGNITUDE_SCALE_FIELD": certified(
                spatial_carrier_id="sigma-prod-1",
                clock_id="clock-prod-1",
            ),
            "W5_IDT_GLOBAL_LAPSE": certified(clock_id="clock-prod-1"),
            "W6_RF_E24_PATCHWISE_LOCAL_SOLUTIONS": certified(
                domain_id="domain-prod-1",
                source_lineage_id="source-prod-1",
                solution_patch_ids=patch_ids,
            ),
        },
    }


def test_canonical_atlas_route_uses_six_independent_groups_and_derives_w7():
    result = certify_manifest(canonical_manifest())
    assert result["status"] == "READY_FOR_SOURCE_RESOLUTION"
    assert len(result["required_groups"]) == 6
    assert "W7_TARGET_DOMAIN_COVERAGE" not in result["required_groups"]
    assert result["derived_witnesses"] == ["W7_TARGET_DOMAIN_COVERAGE"]
    assert result["all_required_slots_certified"] is True
    assert result["production_promoted"] is False


def test_missing_one_solution_patch_fails_canonical_coverage_derivation():
    manifest = canonical_manifest()
    manifest["witnesses"]["W6_RF_E24_PATCHWISE_LOCAL_SOLUTIONS"]["lineage"]["solution_patch_ids"].pop()
    result = certify_manifest(manifest)
    assert result["status"] == "LINEAGE_CONFLICTS"
    assert any(item.startswith("GSC5B_PATCH_COMPLETENESS_MISMATCH:") for item in result["lineage_conflicts"])
    assert "W7_TARGET_DOMAIN_COVERAGE" not in result["derived_witnesses"]


def test_foreign_solution_patch_fails_canonical_lineage():
    manifest = canonical_manifest()
    manifest["witnesses"]["W6_RF_E24_PATCHWISE_LOCAL_SOLUTIONS"]["lineage"]["solution_patch_ids"].append("foreign:9")
    result = certify_manifest(manifest)
    assert result["status"] == "LINEAGE_CONFLICTS"
    assert any("foreign:9" in item for item in result["lineage_conflicts"])


def test_target_domain_must_equal_atlas_domain():
    manifest = canonical_manifest()
    manifest["witnesses"]["W6_RF_E24_PATCHWISE_LOCAL_SOLUTIONS"]["lineage"]["domain_id"] = "larger-domain"
    result = certify_manifest(manifest)
    assert result["status"] == "LINEAGE_CONFLICTS"
    assert any(item.startswith("GSC5B_TARGET_ATLAS_DOMAIN_CONFLICT:") for item in result["lineage_conflicts"])


def test_canonical_atlas_parent_flag_is_required():
    manifest = canonical_manifest()
    manifest["witnesses"]["W2_GSC3A_GLOBAL_PRODUCT_CLOCK"]["lineage"]["canonical_atlas_coverage_certified"] = False
    result = certify_manifest(manifest)
    assert result["status"] == "LINEAGE_CONFLICTS"
    assert "W2_GSC3A_GLOBAL_PRODUCT_CLOCK:CANONICAL_ATLAS_COVERAGE_NOT_CERTIFIED" in result["lineage_conflicts"]


def test_cover_id_must_match_gsc1_gsc3_and_gsc4_geometry():
    manifest = canonical_manifest()
    manifest["witnesses"]["W2_GSC3A_GLOBAL_PRODUCT_CLOCK"]["lineage"]["cover_id"] = "cover-other"
    result = certify_manifest(manifest)
    assert result["status"] == "LINEAGE_CONFLICTS"
    assert any(item.startswith("COVER_ID_CONFLICT:") for item in result["lineage_conflicts"])


def test_clock_properness_product_ancestry_remains_blocked_on_six_group_route():
    manifest = canonical_manifest()
    manifest["witnesses"]["W2_GSC3A_GLOBAL_PRODUCT_CLOCK"]["lineage"]["product_provenance"] = "CLOCK_PROPERNESS"
    result = certify_manifest(manifest)
    assert result["status"] == "LINEAGE_CONFLICTS"
    assert "W2_GSC3A_GLOBAL_PRODUCT_CLOCK:PROPER_CLOCK_ANCESTRY_CYCLE" in result["lineage_conflicts"]
