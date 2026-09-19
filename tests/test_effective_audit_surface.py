from tools import audit_validation_coverage as coverage
from tools.analyze_diagnostic_bottlenecks_effective import load_graph as load_bottleneck_graph
from tools.audit_validation_coverage_effective import load_effective_registry
from tools.federation_surface import load_effective_graph, load_effective_interfaces


def test_validation_coverage_observes_rc_overlay_without_overclaiming_atom_gate():
    report = coverage.audit(
        load_effective_graph(),
        load_effective_registry(),
        load_effective_interfaces(),
    )
    assert report["status"] == "PASS"
    rc = next(row for row in report["repositories"] if row["repository_id"] == "RC")
    assert rc["graph_claim_count"] == 2
    assert rc["directly_mapped_claim_count"] == 1
    assert rc["mapped_claims"] == ["RC.NUCLEON_BOUNDARY"]
    assert "RC.ATOM_FORMALISM" in rc["unmapped_claims"]
    assert any(
        row["claim_id"] == "RC.ATOM_FORMALISM"
        and "CANONICAL_FRONTIER_INCIDENT" in row["reasons"]
        for row in rc["priority_blind_spots"]
    )


def test_bottleneck_graph_observes_effective_rc_surface():
    graph = load_bottleneck_graph()
    nodes = {row["claim_id"] for row in graph["nodes"]}
    assert "RC.NUCLEON_BOUNDARY" in nodes
    assert "RC.ATOM_FORMALISM" in nodes
