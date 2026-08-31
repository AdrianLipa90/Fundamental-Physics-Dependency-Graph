from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "interfaces" / "GSC3A_MATCHING_FLOW_SOLDERING_CANDIDATE_V0_1.json"


def _data():
    return json.loads(CANDIDATE.read_text(encoding="utf-8"))


def test_gsc3a_candidate_is_noncanonical_and_nonpromoting():
    data = _data()
    assert data["promotion_authority"] is False
    assert data["canonical_graph_mutation"] is False
    assert data["canon_mutations"] == []
    assert data["firewalls"]["candidate_edge_enters_canonical_graph"] is False


def test_source_head_and_hosted_validation_are_exactly_frozen():
    source = _data()["source"]
    assert source["pull_request"] == 99
    assert source["head"] == "caaf9d881aadb458f055ff5c2c3eb816222faebb"
    assert source["parent_pull_request"] == 97
    assert source["parent_head"] == "385528e1c87823dd6f681a0a7cdf277aa6389b38"
    assert source["hosted_validation"] == {
        "workflow": "RFC reference suite",
        "run_number": 414,
        "run_id": 33348300043,
        "conclusion": "success",
    }


def test_matching_field_and_product_theorems_are_recorded():
    exact = _data()["exact_candidate_results"]
    assert exact["matching_vector"] == "X=partial_t-b^i partial_i"
    assert exact["clock_pairing"] == "dt(X)=1"
    assert exact["matching_field_overlap"] == "b_q=A_qp b_p-v_qp"
    assert "INTERVAL_COMPLETE_MATCHING_FLOW" in exact["product_trivialization"]
    assert "GLOBAL_CLOCK_PROPERNESS" in exact["proper_clock_route"]


def test_flow_coverage_and_clock_properness_are_or_routes():
    data = _data()
    logic = data["route_logic"]
    assert logic["operator"] == "OR"
    assert logic["alternatives"] == [
        ["FPDG.GSC3A.FLOW_COVERAGE_V01"],
        ["FPDG.GSC3A.CLOCK_PROPERNESS_V01"],
    ]
    assert logic["target"] == "FPDG.GSC3A.PRODUCT_TRIVIALIZATION_V01"
    assert data["firewalls"]["or_routes_are_interpreted_as_and"] is False


def test_event_placement_remains_open_production_input():
    nodes = {node["id"]: node for node in _data()["candidate_nodes"]}
    assert nodes["FPDG.GSC3A.EVENT_PLACEMENT_V01"]["status"] == "OPEN_PRODUCTION_INPUT"
    assert nodes["FPDG.GSC3A.EVENT_ANCHOR_V01"]["status"] == "EXACT_ON_PRODUCTION_EVENT_PLACEMENT"
    assert "GSC3A_SOURCE_OWNED_PHYSICAL_EVENT_PLACEMENT" in _data()["refined_open_frontier"]


def test_live_36d_evidence_is_audit_only():
    audit = _data()["live_36d_audit"]
    assert audit["authority"] == "CANDIDATE_ONLY"
    assert audit["promotion_evidence"] is False
    assert audit["runtime_surface"] == "/dev/shm/ciel_noema"
    assert _data()["firewalls"]["gremlin_can_promote"] is False
    assert _data()["firewalls"]["phase36d_can_promote"] is False
    assert _data()["firewalls"]["terminal36d_can_promote"] is False


def test_candidate_edge_graph_is_acyclic():
    edges = [(edge["from"], edge["to"]) for edge in _data()["candidate_edges"]]
    nodes = {x for edge in edges for x in edge}
    adjacency = {node: [] for node in nodes}
    indegree = {node: 0 for node in nodes}
    for source, target in edges:
        adjacency[source].append(target)
        indegree[target] += 1
    stack = [node for node, degree in indegree.items() if degree == 0]
    seen = 0
    while stack:
        node = stack.pop()
        seen += 1
        for target in adjacency[node]:
            indegree[target] -= 1
            if indegree[target] == 0:
                stack.append(target)
    assert seen == len(nodes)
