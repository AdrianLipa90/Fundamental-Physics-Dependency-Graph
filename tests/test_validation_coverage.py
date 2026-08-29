import unittest

from tools.audit_validation_coverage import audit


class ValidationCoverageTests(unittest.TestCase):
    def graph(self):
        return {
            "nodes": [
                {"claim_id": "TIR.A", "repository": "TIR", "status": "CLOSED"},
                {"claim_id": "IDT.B", "repository": "IDT", "status": "PASS"},
                {"claim_id": "IDT.C", "repository": "IDT", "status": "ACTIVE_FRONTIER"},
            ],
            "edges": [
                {"from": "TIR.A", "to": "IDT.B", "authority": "CANONICAL_CROSS_REPO"},
                {"from": "IDT.B", "to": "IDT.C", "authority": "CANONICAL_FRONTIER"},
            ],
        }

    def registry(self):
        return {
            "schema": "FPDG_VALIDATION_PRODUCER_REGISTRY_V0_1",
            "producers": {
                "TIR": {"mapped_claims": []},
                "IDT": {"mapped_claims": ["IDT.B"]},
            },
        }

    def test_coverage_counts_only_explicit_direct_bindings(self):
        report = audit(self.graph(), self.registry())
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["graph_claim_count"], 3)
        self.assertEqual(report["directly_mapped_claim_count"], 1)
        self.assertFalse(report["scientific_validation_score"])

    def test_unmapped_cross_repo_boundary_is_priority_zero(self):
        report = audit(self.graph(), self.registry())
        tir = next(row for row in report["repositories"] if row["repository_id"] == "TIR")
        self.assertEqual(tir["priority_blind_spots"][0]["claim_id"], "TIR.A")
        self.assertEqual(tir["priority_blind_spots"][0]["priority"], 0)

    def test_wrong_repository_mapping_fails_registry(self):
        registry = self.registry()
        registry["producers"]["TIR"]["mapped_claims"] = ["IDT.B"]
        report = audit(self.graph(), registry)
        self.assertEqual(report["status"], "REGISTRY_INVALID")
        self.assertTrue(report["problems"])


if __name__ == "__main__":
    unittest.main()
