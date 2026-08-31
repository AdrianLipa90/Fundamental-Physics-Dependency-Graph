import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FEDERATION = ROOT / "interfaces" / "GLOBAL_SPACETIME_CLOSURE_CANDIDATE_FEDERATION_V0_7.json"


def load_federation():
    return json.loads(FEDERATION.read_text(encoding="utf-8"))


def test_candidate_authority_remains_noncanonical():
    data = load_federation()
    assert data["promotion_authority"] is False
    assert data["canonical_graph_mutation"] is False
    assert data["canon_mutations"] == []
    assert data["authority"]["runtime_audit_role"] == "CANDIDATE_GENERATION_AND_AUDIT_ONLY"


def test_rigid_spatial_packet_consumes_overlap_local_magnitude_samples():
    data = load_federation()
    rigid = next(
        route
        for route in data["gsc4_spatial_geometry_packet"]["alternatives"]
        if route["route"] == "ANCHORED_PHASE_SCALED_RIGID_PACKET"
    )
    requirements = set(rigid["requirements"])
    assert "FPDG.GSC4E.PRODUCTION_OVERLAP_LOCAL_PHASE_MAGNITUDE_SAMPLES" in requirements
    assert "FPDG.GSC4E.PRODUCTION_PHASE_MAGNITUDE_FIELD_ID" in requirements
    assert "FPDG.GSC4E.PRODUCTION_PHYSICAL_SAMPLE_IDENTITIES" in requirements
    assert rigid["pointwise_gluing"] == "nu_p(x_alpha)=nu_q(x_alpha)"


def test_signed_phase_rate_identity_is_removed_from_rigid_spatial_frontier():
    data = load_federation()
    eliminated = data["derived_or_eliminated_from_frontier"]
    assert "SIGNED_PHASE_RATE_IDENTITY_AS_RIGID_SPATIAL_SCALE_INPUT" in eliminated
    ownership = data["typed_carrier_ownership"]
    assert ownership["SIGNED_PHASE_RATE_DYNAMICS"]["carrier"] == "omega_t(x)"
    assert ownership["RIGID_SPATIAL_SCALE"]["carrier"] == "nu(x)=abs(omega_t(x))"


def test_patch_constant_representation_is_removed_but_variable_scale_connection_is_preserved():
    data = load_federation()
    eliminated = data["derived_or_eliminated_from_frontier"]
    assert "PATCH_CONSTANT_PHASE_SCALE_AS_RIGID_SPATIAL_REPRESENTATION" in eliminated
    preserved = data["preserved_structure"]
    assert preserved["RF02I_VARIABLE_PHASE_SCALE_CONNECTION"] == "PRESERVED_BY_OVERLAP_LOCAL_FIELD_SEMANTICS"
    assert preserved["RF02I_PHASE_SCALE_GRADIENTS"] == "SOURCE_REPRESENTABLE"


def test_rigid_spatial_route_keeps_lapse_and_event_clock_as_separate_typed_carriers():
    data = load_federation()
    ownership = data["typed_carrier_ownership"]
    assert ownership["TEMPORAL_LAPSE"]["carrier"] == "N_R"
    assert ownership["TEMPORAL_LAPSE"]["owner"] == "IDT_RFN0_LINEAGE"
    assert ownership["EVENT_CLOCK"]["owner"] == "IDT_05H_LINEAGE"
    assert "IDT_SHARED_CLOCK_LAPSE_AND_CALIBRATION" in data["open_frontier"]["GSC4"]


def test_general_and_flow_routes_share_the_same_spatial_packet_abstraction():
    data = load_federation()
    general = data["global_routes"]["general_gsc4a_atlas"]["requirements"]
    flow = data["global_routes"]["flow_adapted_gsc4b_atlas"]["requirements"]
    assert "FPDG.GSC4.SPATIAL_GEOMETRY_PACKET" in general
    assert "FPDG.GSC4.SPATIAL_GEOMETRY_PACKET" in flow
    assert "FPDG.GSC3.PRODUCT_TRIVIALIZATION" not in general
    assert "FPDG.GSC3.PRODUCT_TRIVIALIZATION" in flow


def test_rigid_route_outputs_keep_a_equals_r_specialization_local_to_packet_constructor():
    data = load_federation()
    rigid = next(
        route
        for route in data["gsc4_spatial_geometry_packet"]["alternatives"]
        if route["route"] == "ANCHORED_PHASE_SCALED_RIGID_PACKET"
    )
    outputs = set(rigid["derived_outputs"])
    assert "A_qp=Q_q^T Q_p" in outputs
    assert "R_qp=Q_q^T Q_p" in outputs
    assert data["preserved_structure"]["GENERAL_SMOOTH_GSC4A_ROUTE"] == "PARALLEL_SUFFICIENT_ROUTE"


def test_gsc4_union_still_targets_rfe25():
    data = load_federation()
    route = data["global_routes"]["gsc4_atlas"]
    assert route["operator"] == "OR"
    assert route["target"] == "RFC.E25.SHARED_SPACETIME_ATLAS"
    assert set(route["alternatives"]) == {
        "FPDG.GSC4.GENERAL_SOURCE_ASSEMBLED_RF_E25_PACKET",
        "FPDG.GSC4.FLOW_ADAPTED_SOURCE_ASSEMBLED_RF_E25_PACKET",
    }


def test_recorded_live_audits_are_36d_and_candidate_only():
    data = load_federation()
    audits = data["live_36d_audits"]
    assert audits["authority"] == "CANDIDATE_ONLY"
    assert audits["promotion_evidence"] is False
    assert audits["gsc4d_pointwise_field_correction"]["shape"] == [12, 36]
    assert audits["gsc4e_magnitude_quotient_after_sync"]["shape"] == [9, 36]
