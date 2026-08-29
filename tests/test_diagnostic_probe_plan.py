import unittest

from tools.build_diagnostic_probe_plan import build_plan


class DiagnosticProbePlanTests(unittest.TestCase):
    def seam_report(self):
        return {
            "schema": "FPDG_PAIN_SEAM_REPORT_V0_1",
            "zones": [
                {
                    "frontier_claim": "RFC.E20",
                    "repository": "RFC",
                    "claim_source": "closure/einstein/RF_E20.md",
                    "claim_status": "CONDITIONAL",
                    "seams": [
                        {
                            "seam_id": "IFACE.IDT_TO_RFC.CLOCK",
                            "role": "ENTRY_TO_FRONTIER",
                            "from": "IDT.CLOCK",
                            "to": "RFC.E20",
                            "scope": "CROSS_REPOSITORY",
                            "registration_status": "REGISTERED_CROSS_REPO_INTERFACE",
                            "interface_id": "IFACE.IDT_TO_RFC.CLOCK",
                            "contract": {"status": "PASS"},
                        },
                        {
                            "seam_id": "EDGE.RFC.E20->RFC.FRONTIER",
                            "role": "EXIT_FROM_FRONTIER",
                            "from": "RFC.E20",
                            "to": "RFC.FRONTIER",
                            "scope": "LOCAL_REPOSITORY",
                            "registration_status": "LOCAL_DEPENDENCY_EDGE",
                            "contract": {},
                        },
                    ],
                }
            ],
            "integration_targets": [],
        }

    def micro_report(self, precision="EQUATION"):
        return {
            "schema": "FPDG_PAIN_MICRO_COORDINATES_V0_1",
            "status": "LOCALIZED",
            "causal_inference_performed": False,
            "candidate_edges_included": False,
            "coordinates": [
                {
                    "coordinate_id": "MICRO.OBS.1",
                    "repository": "RFC",
                    "claim_id": "RFC.E20",
                    "anchored_claims": ["RFC.E20"],
                    "precision": precision,
                    "source_locator": {"path": "closure/einstein/RF_E20.md", "equation_id": "E20.17"},
                    "evidence_refs": ["validator:rf_e20"],
                }
            ],
            "zones": [
                {
                    "frontier_claim": "RFC.E20",
                    "coordinate_ids": ["MICRO.OBS.1"],
                    "finest_precision": precision,
                }
            ],
            "integration_coordinates": [],
        }

    def test_direct_micro_coordinate_is_first_probe(self):
        plan = build_plan(self.seam_report(), self.micro_report(), None)
        first = plan["zones"][0]["first_probe"]
        self.assertEqual(first["kind"], "OBSERVED_EVIDENCE_COORDINATE")
        self.assertEqual(first["precision"], "EQUATION")
        self.assertFalse(plan["causal_inference_performed"])

    def test_entry_seam_precedes_claim_and_exit_when_no_fine_coordinate(self):
        micro = self.micro_report("UNSPECIFIED")
        micro["zones"][0]["coordinate_ids"] = []
        micro["coordinates"] = []
        plan = build_plan(self.seam_report(), micro, None)
        probes = plan["zones"][0]["probes"]
        self.assertEqual(probes[0]["kind"], "DEPENDENCY_SEAM")
        self.assertEqual(probes[0]["role"], "ENTRY_TO_FRONTIER")
        self.assertEqual(probes[1]["kind"], "FRONTIER_CLAIM_SOURCE")
        self.assertEqual(probes[2]["role"], "EXIT_FROM_FRONTIER")

    def test_gremlin_match_is_candidate_hint_only(self):
        matches = {
            "schema": "FPDG_PAIN_SIGNATURE_MATCHES_V0_1",
            "matches": [
                {
                    "incident_path": "diagnostics/incidents/INC-1.json",
                    "signature_hash": "a" * 64,
                    "exact_structural_match": True,
                    "feature_jaccard": 1.0,
                    "exact_coordinates": {"frontier_claims": ["TIR.X"]},
                }
            ],
        }
        plan = build_plan(self.seam_report(), self.micro_report(), matches)
        self.assertEqual(plan["gremlin_hints"][0]["authority"], "CANDIDATE_ONLY")
        self.assertNotEqual(
            plan["zones"][0]["first_probe"]["kind"],
            "INCIDENT_RECURRENCE_CANDIDATE",
        )


if __name__ == "__main__":
    unittest.main()
