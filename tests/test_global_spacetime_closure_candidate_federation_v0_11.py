import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFINEMENT = ROOT / "interfaces" / "GLOBAL_SPACETIME_CLOSURE_CANDIDATE_FEDERATION_V0_11.json"


def load_refinement():
    return json.loads(REFINEMENT.read_text(encoding="utf-8"))


def test_refinement_remains_noncanonical():
    data = load_refinement()
    assert data["promotion_authority"] is False
    assert data["canonical_graph_mutation"] is False
    assert data["canon_mutations"] == []


def test_gsc5a_hosted_pass_is_recorded():
    data = load_refinement()
    src = data["source_validation"]
    assert src["rfc_pr"] == 111
    assert src["reference_suite_run"] == 466
    assert src["conclusion"] == "success"
    assert src["pytest"] == "1356 passed in 13.70s"


def test_einstein_stress_and_residual_overlap_checks_are_derived():
    data = load_refinement()
    derived = set(data["refinement"]["exact_derivations"])
    assert "G_p=J^T G_q J_FROM_NATURALITY_OF_G[g]" in derived
    assert "T_p=J^T T_q J_FROM_PULLED_BACK_PATCHWISE_RF_E24_EQUATIONS" in derived
    assert "EINSTEIN_RESIDUAL_OVERLAP_COVARIANCE" in derived
    assert "ZERO_GLOBAL_RESIDUAL_ON_COVERED_DOMAIN" in derived


def test_derived_tensor_overlap_matrices_leave_production_frontier():
    data = load_refinement()
    removed = set(data["refinement"]["derived_coordinates_removed_from_production_frontier"])
    assert "INDEPENDENT_G_OVERLAP_MATRICES" in removed
    assert "INDEPENDENT_T_OVERLAP_MATRICES" in removed
    assert "INDEPENDENT_EINSTEIN_RESIDUAL_OVERLAP_MATRICES" in removed


def test_source_lineage_and_domain_coverage_remain_explicit_inputs():
    data = load_refinement()
    open_inputs = set(data["frontier_update"]["GSC5_open_inputs"])
    assert "COMMON_PHYSICAL_SOURCE_FIELD_LINEAGE_ID" in open_inputs
    assert "TARGET_DOMAIN_COVERAGE" in open_inputs
    assert data["firewalls"]["metric_atlas_alone_supplies_physical_source_lineage"] is False
    assert data["firewalls"]["patchwise_local_solutions_alone_supply_target_domain_coverage"] is False


def test_gsc5a_does_not_promote_gsc6():
    data = load_refinement()
    assert data["firewalls"]["gsc5a_promotes_gsc6_global_hyperbolicity"] is False


def test_live_triad_is_candidate_only():
    data = load_refinement()
    audit = data["live_36d_audit"]
    assert audit["authority"] == "CANDIDATE_ONLY"
    assert audit["promotion_evidence"] is False
    assert audit["shape"] == [9, 36]
    assert len(audit["terminal_receipt_sha256"]) == 64
    assert len(audit["phasenav_trace_sha256"]) == 64
