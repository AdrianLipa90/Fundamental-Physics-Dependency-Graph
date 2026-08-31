import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FEDERATION = ROOT / "interfaces" / "GLOBAL_SPACETIME_CLOSURE_CANDIDATE_FEDERATION_V0_8.json"


def load_federation():
    return json.loads(FEDERATION.read_text(encoding="utf-8"))


def rigid_route(data):
    return next(
        route
        for route in data["gsc4_spatial_geometry_packet"]["alternatives"]
        if route["route"] == "ANCHORED_PHASE_SCALED_RIGID_PACKET_MOD_GLOBAL_SE3"
    )


def test_candidate_remains_noncanonical_and_runtime_has_no_promotion_authority():
    data = load_federation()
    assert data["promotion_authority"] is False
    assert data["canonical_graph_mutation"] is False
    assert data["canon_mutations"] == []
    assert data["authority"]["runtime_audit_role"] == "CANDIDATE_GENERATION_AND_AUDIT_ONLY"


def test_gsc4f_hosted_source_validation_is_recorded():
    data = load_federation()
    g = data["source_validations"]["gsc4f_global_se3_quotient"]
    assert g["rfc_pr"] == 110
    assert g["conclusion"] == "success"
    assert g["reference_suite_run"] == 463
    assert g["pytest"].startswith("1402 passed")


def test_rigid_route_consumes_relative_geometry_mod_global_se3():
    data = load_federation()
    rigid = rigid_route(data)
    requirements = set(rigid["requirements"])
    assert "FPDG.GSC4F.GLOBAL_SE3_QUOTIENT_THEOREM" in requirements
    assert "FPDG.GSC4F.PRODUCTION_RELATIVE_RIGID_CONFIGURATION_MOD_GLOBAL_SE3" in requirements
    assert "FPDG.GSC4D.PRODUCTION_ANCHOR_VECTORS" not in requirements
    assert "FPDG.GSC4D.PRODUCTION_SO3_FRAME_MATRICES" not in requirements


def test_global_se3_quotient_removes_six_only_and_retains_relative_geometry():
    data = load_federation()
    quotient = rigid_route(data)["gauge_quotient"]
    assert quotient["group"] == "SE(3)"
    assert quotient["canonical_reference_patch"] == "r_p0=0, Q_p0=I3"
    assert quotient["global_gauge_dof_removed"] == 6
    assert quotient["retained_source_geometry"] == "RELATIVE_RIGID_CONFIGURATION"
    assert data["preserved_structure"]["RELATIVE_RIGID_CONFIGURATION"] == "SOURCE_REPRESENTABLE_AND_RETAINED"


def test_absolute_anchor_origin_and_frame_orientation_leave_frontier():
    data = load_federation()
    eliminated = set(data["derived_or_eliminated_from_frontier"])
    assert "ABSOLUTE_RIGID_ANCHOR_ORIGIN_AS_PRODUCTION_INPUT" in eliminated
    assert "ABSOLUTE_RIGID_FRAME_ORIENTATION_AS_PRODUCTION_INPUT" in eliminated
    assert "GLOBAL_SE3_GAUGE_COORDINATES_6" in eliminated
    assert "PRODUCTION_RELATIVE_RIGID_CONFIGURATION_MOD_GLOBAL_SE3_ON_RIGID_ROUTE" in data["open_frontier"]["GSC4"]


def test_a5_scope_preserves_numeric_relative_geometry_as_source_bound():
    data = load_federation()
    assert data["preserved_structure"]["A5_TOPOLOGY_SCOPE"] == (
        "TOPOLOGY_AND_COVERAGE_WITH_RELATIVE_NUMERIC_GEOMETRY_SEPARATELY_SOURCE_BOUND"
    )


def test_phase_magnitude_and_temporal_carriers_remain_separately_typed():
    data = load_federation()
    ownership = data["typed_carrier_ownership"]
    assert ownership["RIGID_SPATIAL_SCALE"]["carrier"] == "nu(x)=abs(omega_t(x))"
    assert ownership["TEMPORAL_LAPSE"]["carrier"] == "N_R"
    assert ownership["EVENT_CLOCK"]["owner"] == "IDT_05H_LINEAGE"
    assert "FPDG.GSC4E.PRODUCTION_OVERLAP_LOCAL_PHASE_MAGNITUDE_SAMPLES" in rigid_route(data)["requirements"]


def test_general_route_remains_parallel_and_gsc4_union_still_targets_rfe25():
    data = load_federation()
    assert data["preserved_structure"]["GENERAL_SMOOTH_GSC4A_ROUTE"] == "PARALLEL_SUFFICIENT_ROUTE"
    route = data["global_routes"]["gsc4_atlas"]
    assert route["operator"] == "OR"
    assert route["target"] == "RFC.E25.SHARED_SPACETIME_ATLAS"


def test_live_gsc4f_audit_is_36d_and_candidate_only():
    data = load_federation()
    audits = data["live_36d_audits"]
    audit = audits["gsc4f_global_se3_quotient"]
    assert audit["shape"] == [12, 36]
    assert len(audit["terminal_receipt_sha256"]) == 64
    assert len(audit["phasenav_trace_sha256"]) == 64
    assert audits["authority"] == "CANDIDATE_ONLY"
    assert audits["promotion_evidence"] is False
