import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "interfaces" / "GLOBAL_SPACETIME_CLOSURE_CANDIDATE_FEDERATION_V0_14.json"


def load_doc():
    return json.loads(DOC.read_text(encoding="utf-8"))


def test_candidate_is_noncanonical_and_runtime_cannot_promote():
    d = load_doc()
    assert d["promotion_authority"] is False
    assert d["canonical_graph_mutation"] is False
    assert d["canon_mutations"] == []
    assert d["firewalls"]["runtime_audit_can_promote"] is False
    assert d["firewalls"]["candidate_edge_enters_canonical_graph"] is False


def test_gsc5b_is_hosted_validated_source_refinement():
    d = load_doc()
    src = d["source_validation"]
    assert src["rfc_pr"] == 118
    assert src["conclusion"] == "success"
    assert src["theorem_reference_suite_run"] == 483
    assert src["receipt_head_reference_suite_run"] == 484


def test_w7_is_derived_only_on_canonical_atlas_domain_route():
    d = load_doc()
    update = d["frontier_update"]
    assert update["independent_witness_groups_before"] == 7
    assert update["independent_witness_groups_after_on_current_route"] == 6
    assert update["removed_independent_group_on_current_route"] == "W7_TARGET_DOMAIN_COVERAGE"
    assert update["broader_or_different_target_domain_coverage"] == "OPEN_SEPARATE_EXTENSION_INPUT"

    route = d["gsc5_routes"]["canonical_atlas_domain_route"]
    req = set(route["requirements"])
    assert "W6_RF_E24_LOCAL_SOLUTION_RECEIPTS_ON_EXACT_ATLAS_PATCH_SET" in req
    assert "TARGET_DOMAIN_ID_EQUALS_ATLAS_DOMAIN_ID" in req
    assert "W7_TARGET_DOMAIN_COVERAGE" in route["derived"]


def test_broader_target_domain_retains_explicit_coverage():
    d = load_doc()
    route = d["gsc5_routes"]["broader_target_domain_route"]
    assert "EXPLICIT_BROADER_TARGET_DOMAIN_COVERAGE_RECEIPT" in route["requirements"]
    assert d["firewalls"]["gsc5b_removes_W7_for_broader_target_domains"] is False


def test_patch_count_equality_is_not_promoted_to_patch_identity():
    d = load_doc()
    assert d["firewalls"]["patch_count_equality_is_sufficient_without_patch_id_equality"] is False
    controls = set(d["falsification_controls"])
    assert "MISSING_ONE_ATLAS_PATCH_RF_E24_RECEIPT_KEEPS_W7_OPEN" in controls
    assert "FOREIGN_OR_EXTRA_SOLUTION_PATCH_ID_KEEPS_CANONICAL_LINEAGE_ROUTE_OPEN" in controls
    assert "TARGET_DOMAIN_ID_DIFFERENT_FROM_ATLAS_DOMAIN_ID_KEEPS_W7_OPEN" in controls


def test_live_audit_stays_candidate_only():
    d = load_doc()
    audit = d["live_36d_audit"]
    assert audit["authority"] == "CANDIDATE_ONLY"
    assert audit["promotion_evidence"] is False
    assert audit["shape"] == [7, 36]
