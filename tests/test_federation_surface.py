import unittest

from tools.federation_surface import (
    load_effective_claims,
    load_effective_graph,
    load_effective_interfaces,
    repository_registry,
)
from tools.impact import compute_impact


class FederationSurfaceTests(unittest.TestCase):
    def test_resonant_chemistry_is_registered(self):
        registry = repository_registry()
        self.assertIn("RC", registry)
        self.assertEqual(
            registry["RC"]["repository"],
            "AdrianLipa90/Resonant-Chemistry",
        )

    def test_effective_graph_contains_nucleon_boundary(self):
        graph = load_effective_graph()
        nodes = {row["claim_id"]: row for row in graph["nodes"]}
        self.assertIn("RC.NUCLEON_BOUNDARY", nodes)
        self.assertIn("RC.ATOM_FORMALISM", nodes)
        self.assertEqual(
            nodes["RC.NUCLEON_BOUNDARY"]["status"],
            "SOURCE_BOUND_EFFECTIVE_INPUT_CONTRACT",
        )

    def test_candidate_tir_to_rc_edge_does_not_propagate_by_default(self):
        graph = load_effective_graph()
        impacted = compute_impact(graph, "TIR.STANDARD_MODEL", include_candidates=False)
        self.assertNotIn("RC.NUCLEON_BOUNDARY", {row["claim_id"] for row in impacted})
        candidate_impact = compute_impact(graph, "TIR.STANDARD_MODEL", include_candidates=True)
        self.assertIn("RC.NUCLEON_BOUNDARY", {row["claim_id"] for row in candidate_impact})

    def test_claim_and_interface_overlays_are_visible(self):
        claims = {row["claim_id"] for row in load_effective_claims()}
        self.assertIn("RC.NUCLEON_BOUNDARY", claims)
        interfaces = {
            row["interface_id"]
            for row in load_effective_interfaces()["interfaces"]
        }
        self.assertIn("IFACE.TIR_TO_RC.ENDOGENOUS_NUCLEON", interfaces)


if __name__ == "__main__":
    unittest.main()
