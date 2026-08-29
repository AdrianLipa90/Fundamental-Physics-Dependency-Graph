import json
import tempfile
import unittest
from pathlib import Path

from tools.build_pain_signature import build_signature
from tools.match_pain_signatures import MatchError, load_signature, match_signature


class PainSignatureTests(unittest.TestCase):
    def diagnosis(self, frontier="IDT.B"):
        return {
            "schema": "FPDG_INCONSISTENCY_DIAGNOSIS_V0_1",
            "localization_mode": "EXACT",
            "pain_zones": [
                {
                    "frontier_claim": frontier,
                    "status": "PASS",
                    "symptom_anchors": [frontier, "IDT.C"],
                    "witness_paths": [[frontier], [frontier, "IDT.C"]],
                    "downstream_revalidation_count": 1,
                }
            ],
            "integration_pain_points": [],
        }

    def seams(self, frontier="IDT.B", seam_id="IFACE.TIR_TO_IDT.AB"):
        return {
            "schema": "FPDG_PAIN_SEAM_REPORT_V0_1",
            "zones": [
                {
                    "frontier_claim": frontier,
                    "claim_status": "PASS",
                    "seams": [
                        {
                            "seam_id": seam_id,
                            "role": "ENTRY_TO_FRONTIER",
                            "scope": "CROSS_REPOSITORY",
                            "authority": "CANONICAL_CROSS_REPO",
                            "registration_status": "REGISTERED_CROSS_REPO_INTERFACE",
                            "contract": {"status": "PASS", "validation": "SUITE_PASS"},
                        }
                    ],
                }
            ],
            "integration_targets": [],
        }

    def test_signature_is_repository_name_agnostic_for_same_shape(self):
        left = build_signature(self.diagnosis("IDT.B"), self.seams("IDT.B", "IFACE.ONE"))
        right = build_signature(self.diagnosis("RFC.X"), self.seams("RFC.X", "IFACE.TWO"))
        self.assertEqual(left["signature_hash"], right["signature_hash"])
        self.assertNotEqual(left["exact_coordinates"], right["exact_coordinates"])

    def test_exact_shape_match_scores_one(self):
        current = build_signature(self.diagnosis(), self.seams())
        historical = build_signature(self.diagnosis("RFC.X"), self.seams("RFC.X", "IFACE.OTHER"))
        report = match_signature(current, [(Path("incident.json"), historical)], 0.55)
        self.assertEqual(report["match_count"], 1)
        self.assertTrue(report["matches"][0]["exact_structural_match"])
        self.assertEqual(report["matches"][0]["feature_jaccard"], 1.0)

    def test_different_shape_can_be_filtered_by_threshold(self):
        current = build_signature(self.diagnosis(), self.seams())
        other_diagnosis = {
            "schema": "FPDG_INCONSISTENCY_DIAGNOSIS_V0_1",
            "localization_mode": "INTEGRATION_METADATA_EXACT",
            "pain_zones": [],
            "integration_pain_points": [{"location": "LOCK.X", "kind": "LOCK_DRIFT"}],
        }
        other_seams = {
            "schema": "FPDG_PAIN_SEAM_REPORT_V0_1",
            "zones": [],
            "integration_targets": [],
        }
        historical = build_signature(other_diagnosis, other_seams)
        report = match_signature(current, [(Path("other.json"), historical)], 0.9)
        self.assertEqual(report["match_count"], 0)

    def test_stored_hash_tamper_fails_closed(self):
        signature = build_signature(self.diagnosis(), self.seams())
        signature["structural_signature"]["localization_mode"] = "TAMPERED"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "incident.json"
            path.write_text(json.dumps(signature), encoding="utf-8")
            with self.assertRaises(MatchError):
                load_signature(path)

    def test_stored_feature_token_tamper_fails_closed(self):
        signature = build_signature(self.diagnosis(), self.seams())
        signature["feature_tokens"] = signature["feature_tokens"] + ["forged=true"]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "incident.json"
            path.write_text(json.dumps(signature), encoding="utf-8")
            with self.assertRaises(MatchError):
                load_signature(path)


if __name__ == "__main__":
    unittest.main()
