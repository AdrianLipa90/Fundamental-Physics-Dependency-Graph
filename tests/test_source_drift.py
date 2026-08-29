import unittest

from tools.watch_source_drift import aggregate_impact, map_paths_to_claims


class SourceDriftTests(unittest.TestCase):
    def test_path_mapping_is_repository_local(self):
        claims = [
            {"claim_id": "TIR.A", "repository": "TIR", "source_path": "a.md"},
            {"claim_id": "TIR.B", "repository": "TIR", "source_path": "b.md"},
            {"claim_id": "IDT.A", "repository": "IDT", "source_path": "a.md"},
        ]
        mapped, fallback = map_paths_to_claims("TIR", ["a.md"], claims)
        self.assertEqual(mapped, ["TIR.A"])
        self.assertFalse(fallback)

    def test_unmapped_change_falls_back_to_all_owned_claims(self):
        claims = [
            {"claim_id": "TIR.A", "repository": "TIR", "source_path": "a.md"},
            {"claim_id": "TIR.B", "repository": "TIR", "source_path": "b.md"},
            {"claim_id": "IDT.A", "repository": "IDT", "source_path": "other.md"},
        ]
        mapped, fallback = map_paths_to_claims("TIR", ["new_formalism.md"], claims)
        self.assertEqual(mapped, ["TIR.A", "TIR.B"])
        self.assertTrue(fallback)

    def test_aggregate_impact_excludes_candidate_edges(self):
        graph = {
            "nodes": [
                {"claim_id": "TIR.A", "repository": "TIR", "status": "CLOSED"},
                {"claim_id": "IDT.B", "repository": "IDT", "status": "PASS"},
                {"claim_id": "SOH.C", "repository": "SOH", "status": "CANDIDATE"},
            ],
            "edges": [
                {"from": "TIR.A", "to": "IDT.B", "authority": "CANONICAL_CROSS_REPO"},
                {"from": "TIR.A", "to": "SOH.C", "authority": "CANDIDATE_ONLY"},
            ],
        }
        impacted = aggregate_impact(graph, ["TIR.A"])
        self.assertEqual([row["claim_id"] for row in impacted], ["IDT.B"])


if __name__ == "__main__":
    unittest.main()
