import unittest

from tools.analyze_diagnostic_bottlenecks import analyze


class DiagnosticBottleneckTests(unittest.TestCase):
    def diagnosis(self, symptoms):
        return {
            "schema": "FPDG_INCONSISTENCY_DIAGNOSIS_V0_1",
            "pain_zones": [
                {
                    "frontier_claim": "A",
                    "symptom_anchors": ["A", *symptoms],
                }
            ],
        }

    def test_common_mandatory_node_and_edge_are_reported(self):
        graph = {
            "nodes": [
                {"claim_id": name, "repository": "R"}
                for name in ("A", "B", "C", "D", "E")
            ],
            "edges": [
                {"from": "A", "to": "B", "authority": "CANONICAL"},
                {"from": "B", "to": "C", "authority": "CANONICAL"},
                {"from": "B", "to": "D", "authority": "CANONICAL"},
                {"from": "C", "to": "E", "authority": "CANONICAL"},
                {"from": "D", "to": "E", "authority": "CANONICAL"},
            ],
        }
        report = analyze(self.diagnosis(["C", "D"]), graph)
        zone = report["zones"][0]
        self.assertEqual(zone["mandatory_nodes"], ["B"])
        self.assertEqual(
            zone["mandatory_edges"],
            [{"from": "A", "to": "B", "authority": "CANONICAL"}],
        )
        self.assertFalse(report["candidate_edges_included"])
        self.assertFalse(report["causal_inference_performed"])

    def test_parallel_bypass_removes_false_bottleneck(self):
        graph = {
            "nodes": [
                {"claim_id": name, "repository": "R"}
                for name in ("A", "B", "C", "D")
            ],
            "edges": [
                {"from": "A", "to": "B", "authority": "CANONICAL"},
                {"from": "B", "to": "D", "authority": "CANONICAL"},
                {"from": "A", "to": "C", "authority": "CANONICAL"},
                {"from": "C", "to": "D", "authority": "CANONICAL"},
            ],
        }
        report = analyze(self.diagnosis(["D"]), graph)
        target = report["zones"][0]["target_analyses"][0]
        self.assertEqual(target["mandatory_nodes"], [])
        self.assertEqual(target["mandatory_edges"], [])

    def test_candidate_only_edge_never_creates_bypass(self):
        graph = {
            "nodes": [
                {"claim_id": name, "repository": "R"}
                for name in ("A", "B", "C", "D")
            ],
            "edges": [
                {"from": "A", "to": "B", "authority": "CANONICAL"},
                {"from": "B", "to": "D", "authority": "CANONICAL"},
                {"from": "A", "to": "C", "authority": "CANDIDATE_ONLY"},
                {"from": "C", "to": "D", "authority": "CANDIDATE_ONLY"},
            ],
        }
        report = analyze(self.diagnosis(["D"]), graph)
        target = report["zones"][0]["target_analyses"][0]
        self.assertEqual(target["mandatory_nodes"], ["B"])
        self.assertEqual(
            target["mandatory_edges"],
            [
                {"from": "A", "to": "B", "authority": "CANONICAL"},
                {"from": "B", "to": "D", "authority": "CANONICAL"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
