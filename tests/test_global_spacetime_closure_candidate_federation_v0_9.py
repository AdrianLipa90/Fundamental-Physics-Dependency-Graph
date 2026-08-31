import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FEDERATION = ROOT / "interfaces" / "GLOBAL_SPACETIME_CLOSURE_CANDIDATE_FEDERATION_V0_9.json"


def load_federation():
    return json.loads(FEDERATION.read_text(encoding="utf-8"))


def rigid_route(data):
    return next(
        route
        for route in data["gsc4_spatial_geometry_packet"]["alternatives"]
        if route["route"] == "RIGID_SE3_COCYCLE_PLUS_POINTWISE_PHASE_SCALE"
    )


def test_candidate_remains_noncanonical():
    data = load_federation()
    assert data["promotion_authority"] is False
    assert data["canonical_graph_mutation"] is False
    assert data["canon_mutations"] == []
    assert data["authority"]["runtime_audit_role"] == "CANDIDATE_GENERATION_AND_AUDIT_ONLY"


def test_gsc4g_hosted_pass_is_recorded():
    data = load_federation()
    g = data["source_validations"]["gsc4g_rigid_overlap_cocycle_reconstruction"]
    assert g["rfc_pr"] == 112
    assert g["reference_suite_run"] == 467
    assert g["conclusion"] == "success"
    assert g["pytest"].startswith("1412 passed")


def test_rigid_route_uses_numeric_se3_cocycle_not_opaque_patch_anchor_frame_packet():
    data = load_federation()
    req = set(rigid_route(data)["requirements"])
    assert "FPDG.GSC4G.PRODUCTION_CONNECTED_NUMERIC_SE3_OVERLAP_COCYCLE" in req
    assert "FPDG.GSC4G.RIGID_OVERLAP_COCYCLE_RECONSTRUCTION_THEOREM" in req
    assert "FPDG.GSC4F.PRODUCTION_RELATIVE_RIGID_CONFIGURATION_MOD_GLOBAL_SE3" not in req


def test_spanning_tree_is_minimal_continuous_relative_representation():
    data = load_federation()
    rep = rigid_route(data)["minimal_numeric_geometry_representation"]
    assert rep["tree_edge_count"] == "N-1"
    assert rep["continuous_dof"] == "6(N-1)=6N-6"
    assert rep["tree_reconstruction"] == ["Q_q=Q_p A_qp^T", "r_q=r_p-Q_q t_qp"]
    assert rep["non_tree_edges"] == "HOLONOMY_AND_PATH_INDEPENDENCE_CHECKS"


def test_non_tree_edges_leave_independent_local_dof_frontier():
    data = load_federation()
    eliminated = set(data["derived_or_eliminated_from_frontier"])
    assert "NON_TREE_SE3_EDGES_AS_INDEPENDENT_LOCAL_DEGREES_OF_FREEDOM" in eliminated
    assert "PRODUCTION_NON_TREE_EDGE_HOLONOMY_CLOSURE_WHEN_REDUNDANT_EDGES_ARE_SUPPLIED" in data["open_frontier"]["GSC4"]


def test_a5_topology_and_numeric_geometry_remain_separate_typed_carriers():
    data = load_federation()
    owners = data["typed_carrier_ownership"]
    assert owners["TOPOLOGY_AND_COVER"]["owner"] == "TIR_A5_GSC4C"
    assert owners["RIGID_NUMERIC_GEOMETRY"]["owner"] == "RFC_GSC4G"
    assert data["preserved_structure"]["NUMERIC_SE3_COCYCLE"] == "SEPARATELY_SOURCE_BOUND"


def test_pointwise_phase_scale_remains_separate_from_rigid_numeric_cocycle():
    data = load_federation()
    req = set(rigid_route(data)["requirements"])
    assert "FPDG.GSC4E.PRODUCTION_OVERLAP_LOCAL_PHASE_MAGNITUDE_SAMPLES" in req
    assert data["preserved_structure"]["GSC4E_POINTWISE_MAGNITUDE_FIELD"] == "SEPARATELY_SOURCE_BOUND"


def test_global_se3_and_opaque_per_patch_representations_are_eliminated():
    data = load_federation()
    eliminated = set(data["derived_or_eliminated_from_frontier"])
    assert "GLOBAL_SE3_GAUGE_COORDINATES_6" in eliminated
    assert "PER_PATCH_ANCHOR_VECTOR_PACKET_AS_INDEPENDENT_REPRESENTATION" in eliminated
    assert "PER_PATCH_SO3_FRAME_PACKET_AS_INDEPENDENT_REPRESENTATION" in eliminated
    assert "RELATIVE_RIGID_CONFIGURATION_AS_OPAQUE_PER_PATCH_INPUT" in eliminated


def test_live_gsc4g_audit_is_36d_candidate_only():
    data = load_federation()
    audits = data["live_36d_audits"]
    audit = audits["gsc4g_rigid_overlap_cocycle"]
    assert audit["shape"] == [12, 36]
    assert len(audit["terminal_receipt_sha256"]) == 64
    assert len(audit["phasenav_trace_sha256"]) == 64
    assert audits["authority"] == "CANDIDATE_ONLY"
    assert audits["promotion_evidence"] is False
