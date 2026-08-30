import unittest

from tools.localize_interface_seams import localize


class InterfaceSeamLocalizationTests(unittest.TestCase):
    def graph(self):
        return {
            "nodes": [
                {"claim_id": "TIR.A", "repository": "TIR", "status": "PASS", "source": "a.md"},
                {"claim_id": "IDT.B", "repository": "IDT", "status": "PASS", "source": "b.md"},
                {"claim_id": "IDT.C", "repository": "IDT", "status": "PASS", "source": "c.md"},
                {"claim_id": "SOH.X", "repository": "SOH", "status": "CANDIDATE", "source": "x.md"},
            ],
            "edges": [
                {"from": "TIR.A", "to": "IDT.B", "authority": "CANONICAL_CROSS_REPO"},
                {"from": "IDT.B", "to": "IDT.C", "authority": "CANONICAL"},
                {"from": "SOH.X", "to": "IDT.B", "authority": "CANDIDATE_ONLY"},
            ],
        }

    def interfaces(self):
        return {
            "interfaces": [
                {
                    "interface_id": "IFACE.TIR_TO_IDT.AB",
                    "upstream_repository": "TIR",
                    "downstream_repository": "IDT",
                    "upstream_claim": "TIR.A",
                    "downstream_claim": "IDT.B",
                    "contract": {
                        "status": "PASS",
                        "relation": "A -> B",
                        "validation": "SUITE_PASS",
                    },
                }
            ]
        }

    def diagnosis(self):
        return {
            "schema": "FPDG_INCONSISTENCY_DIAGNOSIS_V0_1",
            "status": "LOCALIZED",
            "localization_mode": "EXACT",
            "pain_zones": [
                {
                    "frontier_claim": "IDT.B",
                    "incoming_boundary_edges": [],
                    "outgoing_boundary_edges": [],
                }
            ],
            "integration_pain_points": [],
        }

    def test_registered_cross_repo_entry_seam_is_exact(self):
        report = localize(self.diagnosis(), self.graph(), self.interfaces())
        zone = report["zones"][0]
        entry = next(row for row in zone["seams"] if row["role"] == "ENTRY_TO_FRONTIER")
        self.assertEqual(entry["interface_id"], "IFACE.TIR_TO_IDT.AB")
        self.assertEqual(entry["registration_status"], "REGISTERED_CROSS_REPO_INTERFACE")
        self.assertEqual(entry["contract"]["validation"], "SUITE_PASS")
        self.assertEqual(zone["claim_source"], "b.md")

    def test_candidate_edge_is_not_a_seam(self):
        report = localize(self.diagnosis(), self.graph(), self.interfaces())
        edges = {(row["from"], row["to"]) for row in report["zones"][0]["seams"]}
        self.assertNotIn(("SOH.X", "IDT.B"), edges)

    def test_missing_cross_repo_contract_is_explicit(self):
        report = localize(self.diagnosis(), self.graph(), {"interfaces": []})
        self.assertEqual(report["status"], "LOCALIZED_WITH_UNREGISTERED_CROSS_REPO_SEAMS")
        self.assertEqual(len(report["unregistered_cross_repo_seams"]), 1)
        self.assertEqual(
            report["unregistered_cross_repo_seams"][0]["registration_status"],
            "MISSING_CROSS_REPO_INTERFACE_CONTRACT",
        )

    def test_integration_only_pain_remains_exact_metadata_target(self):
        diagnosis = {
            "schema": "FPDG_INCONSISTENCY_DIAGNOSIS_V0_1",
            "status": "LOCALIZED",
            "localization_mode": "INTEGRATION_METADATA_EXACT",
            "pain_zones": [],
            "integration_pain_points": [
                {
                    "location": "FPDG.SOURCE_HEAD_LOCK.RFC",
                    "repository": "RFC",
                    "witness_locations": ["RFC.main", "FPDG.source_exports.lock.json:RFC"],
                }
            ],
        }
        report = localize(diagnosis, self.graph(), self.interfaces())
        self.assertEqual(report["status"], "LOCALIZED")
        self.assertEqual(report["integration_targets"][0]["location"], "FPDG.SOURCE_HEAD_LOCK.RFC")


if __name__ == "__main__":
    unittest.main()
