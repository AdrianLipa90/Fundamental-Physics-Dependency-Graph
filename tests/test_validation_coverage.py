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

    def interfaces(self):
        return {
            "schema": "FPDG_CROSS_REPO_INTERFACES_TEST",
            "interfaces": [
                {
                    "interface_id": "IFACE.TIR_TO_IDT.AB",
                    "upstream_repository": "TIR",
                    "downstream_repository": "IDT",
                    "upstream_claim": "TIR.A",
                    "downstream_claim": "IDT.B",
                    "contract": {"status": "CANONICAL_CROSS_REPO"},
                },
                {
                    "interface_id": "IFACE.CANDIDATE",
                    "upstream_repository": "TIR",
                    "downstream_repository": "IDT",
                    "upstream_claim": "TIR.A",
                    "downstream_claim": "IDT.C",
                    "contract": {"status": "CANDIDATE_ONLY"},
                },
            ],
        }

    def registry(self):
        return {
            "schema": "FPDG_VALIDATION_PRODUCER_REGISTRY_V0_1",
            "producers": {
                "TIR": {"mapped_claims": [], "mapped_interfaces": []},
                "IDT": {
                    "mapped_claims": ["IDT.B"],
                    "mapped_interfaces": ["IFACE.TIR_TO_IDT.AB"],
                },
            },
        }

    def test_coverage_counts_explicit_claim_and_interface_bindings_separately(self):
        report = audit(self.graph(), self.registry(), self.interfaces())
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["schema"], "FPDG_VALIDATION_COVERAGE_REPORT_V0_2")
        self.assertEqual(report["graph_claim_count"], 3)
        self.assertEqual(report["directly_mapped_claim_count"], 1)
        self.assertEqual(report["promoted_interface_count"], 1)
        self.assertEqual(report["directly_mapped_interface_count"], 1)
        self.assertEqual(report["mapped_interfaces"], ["IFACE.TIR_TO_IDT.AB"])
        self.assertFalse(report["scientific_validation_score"])

    def test_unmapped_cross_repo_boundary_is_priority_zero(self):
        report = audit(self.graph(), self.registry(), self.interfaces())
        tir = next(row for row in report["repositories"] if row["repository_id"] == "TIR")
        self.assertEqual(tir["priority_blind_spots"][0]["claim_id"], "TIR.A")
        self.assertEqual(tir["priority_blind_spots"][0]["priority"], 0)

    def test_wrong_repository_mapping_fails_registry(self):
        registry = self.registry()
        registry["producers"]["TIR"]["mapped_claims"] = ["IDT.B"]
        report = audit(self.graph(), registry, self.interfaces())
        self.assertEqual(report["status"], "REGISTRY_INVALID")
        self.assertTrue(report["problems"])

    def test_candidate_interface_cannot_count_as_direct_promoted_coverage(self):
        registry = self.registry()
        registry["producers"]["IDT"]["mapped_interfaces"] = ["IFACE.CANDIDATE"]
        report = audit(self.graph(), registry, self.interfaces())
        self.assertEqual(report["status"], "REGISTRY_INVALID")
        self.assertEqual(report["directly_mapped_interface_count"], 0)


if __name__ == "__main__":
    unittest.main()
