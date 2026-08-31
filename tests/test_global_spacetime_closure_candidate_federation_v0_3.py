from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FEDERATION = ROOT / "interfaces" / "GLOBAL_SPACETIME_CLOSURE_CANDIDATE_FEDERATION_V0_3.json"
CANONICAL = [
    ROOT / "dependency_graph.yaml",
    ROOT / "claims.jsonl",
    ROOT / "source_export_heads.yaml",
    ROOT / "source_exports.lock.json",
]


def _load():
    return json.loads(FEDERATION.read_text(encoding="utf-8"))


def test_candidate_federation_is_explicitly_noncanonical_and_fail_closed():
    data = _load()
    assert data["schema"] == "FPDG_GLOBAL_SPACETIME_CLOSURE_CANDIDATE_FEDERATION_V0_3"
    assert data["status"] == "NONCANONICAL_VALIDATED_CANDIDATE_FEDERATION"
    assert data["promotion_authority"] is False
    assert data["canonical_graph_mutation"] is False
    assert data["firewalls"] == {
        "reference_fixture_promotes_production": False,
        "hosted_certifier_pass_closes_open_input": False,
        "gremlin_can_promote": False,
        "candidate_edge_enters_canonical_graph": False,
    }


def test_all_three_source_candidate_heads_are_hosted_success_with_open_physical_inputs():
    data = _load()["source_candidates"]
    assert data["TIR_GSC1"]["hosted_validation"]["conclusion"] == "success"
    assert data["TIR_GSC1"]["production_spatial_complex"] == "OPEN_INPUT"
    assert data["IDT_GSC2"]["hosted_validation"]["conclusion"] == "success"
    assert data["IDT_GSC2"]["production_event_complex"] == "OPEN_INPUT"
    assert data["RFC_GSC3_PRODUCT"]["hosted_validation"]["conclusion"] == "success"
    assert data["RFC_GSC3_PRODUCT"]["physical_product_realization"] == "OPEN_BINDING"
    assert data["RFC_GSC3_PRODUCT"]["production_event_placement"] == "OPEN_INPUT"


def test_gsc1_and_gsc2_minimality_controls_are_preserved():
    data = _load()["source_candidates"]
    assert data["TIR_GSC1"]["minimal_combinatorial_witness"] == "LOSSLESS_TETRAHEDRAL_FACET_INCIDENCE"
    assert data["TIR_GSC1"]["same_f_vector_falsifier"] == {
        "f_vector": [6, 14, 16, 8],
        "result": "PASS_AGGREGATE_COUNTS_INSUFFICIENT",
    }
    assert data["IDT_GSC2"]["minimal_nontrivial_cycle_witness"] == {
        "events": 3,
        "edges": 3,
        "exactness_identity": "theta_ab + theta_bc = theta_ac",
    }


def test_product_clock_route_has_exact_coordinate_layer_and_open_physical_binding():
    product = _load()["source_candidates"]["RFC_GSC3_PRODUCT"]
    theorem = product["exact_coordinate_theorem"]
    assert theorem["carrier"] == "M=I x Sigma"
    assert theorem["dimension"] == 4
    assert theorem["clock"] == "t=pr_I"
    assert theorem["dt_nowhere_zero"] is True
    assert theorem["shared_clock_first_row"] == [1, 0, 0, 0]
    assert theorem["determinant_identity"] == "det(J)=det(D_x f)"
    assert product["physical_product_realization"] == "OPEN_BINDING"


def test_every_candidate_edge_has_explicit_promotion_gate_and_no_canonical_authority():
    edges = _load()["candidate_edges"]
    assert len(edges) == 6
    for edge in edges:
        assert edge["authority"] == "CANDIDATE_ONLY"
        assert isinstance(edge["promotion_gate"], str) and edge["promotion_gate"]


def test_open_frontier_retains_all_production_coordinates():
    frontier = set(_load()["open_frontier"])
    assert {
        "GSC1_PRODUCTION_GLOBAL_TETRAHEDRAL_FACET_INCIDENCE",
        "GSC2_PRODUCTION_PHYSICAL_EVENT_INCIDENCE_AND_ELAPSED_EDGES",
        "PHYSICAL_TIR_IDT_PRODUCT_REALIZATION_AND_EVENT_PLACEMENT",
        "GSC4_PRODUCTION_SHARED_ADM_COFRAME_ATLAS",
        "GSC5_PRODUCTION_GLOBAL_EINSTEIN_CARRIER_AND_DOMAIN_COVERAGE",
        "GSC6_GLOBAL_FINITE_LAPSE_BOUND_AND_COMPLETE_ADM_WICK_METRIC",
    } <= frontier


def test_canonical_surface_files_remain_present_as_separate_authority_surface():
    # The candidate federation is intentionally stored outside canonical graph files.
    # This test guards against accidentally treating the addendum itself as a replacement.
    for path in CANONICAL:
        assert path.is_file(), path
