import unittest

from tools.localize_micro_coordinates import MicroLocalizationError, localize


class MicroLocalizationTests(unittest.TestCase):
    def diagnosis(self):
        return {
            "schema": "FPDG_INCONSISTENCY_DIAGNOSIS_V0_1",
            "observations": [
                {
                    "observation_id": "o1",
                    "anchors": ["RFC.E20"],
                    "anchor_method": "EXACT_CLAIM",
                    "precision": "EXACT",
                },
                {
                    "observation_id": "o2",
                    "anchors": ["RFC.E20"],
                    "anchor_method": "EXACT_CLAIM",
                    "precision": "EXACT",
                },
            ],
            "pain_zones": [
                {
                    "frontier_claim": "RFC.E20",
                    "observation_ids": ["o1", "o2"],
                }
            ],
            "integration_pain_points": [],
        }

    def evidence(self):
        return {
            "schema": "FPDG_INCONSISTENCY_EVIDENCE_V0_1",
            "observations": [
                {
                    "observation_id": "o1",
                    "kind": "VALIDATOR_FAILURE",
                    "repository": "RFC",
                    "claim_id": "RFC.E20",
                    "source_path": "closure/einstein/RF_E20.md",
                    "source_locator": {
                        "path": "closure/einstein/RF_E20.md",
                        "equation_id": "RF-E20.17",
                        "line_start": 412,
                        "line_end": 419,
                        "validator_id": "test_rf_e20_mass_scale",
                    },
                    "expected": "residual <= 1e-12",
                    "observed": "residual = 4e-7",
                    "evidence_refs": ["ci:rf-e20:123"],
                },
                {
                    "observation_id": "o2",
                    "kind": "RECEIPT_FAILURE",
                    "repository": "RFC",
                    "claim_id": "RFC.E20",
                    "source_locator": {
                        "receipt_ref": "RF_E20_SCALE_RECEIPT.json",
                    },
                },
            ],
        }

    def test_preserves_exact_source_range_equation_and_validator(self):
        report = localize(self.diagnosis(), self.evidence())
        self.assertEqual(report["status"], "LOCALIZED")
        self.assertEqual(report["finest_precision"], "SOURCE_RANGE")
        coordinate = next(row for row in report["coordinates"] if row["observation_id"] == "o1")
        self.assertEqual(coordinate["precision"], "SOURCE_RANGE")
        self.assertEqual(coordinate["source_locator"]["equation_id"], "RF-E20.17")
        self.assertEqual(coordinate["source_locator"]["line_start"], 412)
        self.assertEqual(coordinate["source_locator"]["validator_id"], "test_rf_e20_mass_scale")
        self.assertEqual(report["zones"][0]["frontier_claim"], "RFC.E20")

    def test_receipt_only_evidence_remains_receipt_precision(self):
        report = localize(self.diagnosis(), self.evidence())
        coordinate = next(row for row in report["coordinates"] if row["observation_id"] == "o2")
        self.assertEqual(coordinate["precision"], "RECEIPT")
        self.assertEqual(coordinate["source_locator"]["receipt_ref"], "RF_E20_SCALE_RECEIPT.json")

    def test_source_path_and_locator_path_disagreement_fails_closed(self):
        evidence = self.evidence()
        evidence["observations"][0]["source_locator"]["path"] = "different.md"
        with self.assertRaisesRegex(MicroLocalizationError, "disagree"):
            localize(self.diagnosis(), evidence)

    def test_invalid_line_range_fails_closed(self):
        evidence = self.evidence()
        evidence["observations"][0]["source_locator"]["line_start"] = 500
        evidence["observations"][0]["source_locator"]["line_end"] = 499
        with self.assertRaisesRegex(MicroLocalizationError, "precedes"):
            localize(self.diagnosis(), evidence)

    def test_integration_coordinate_is_preserved_without_fabricating_claim(self):
        diagnosis = {
            "schema": "FPDG_INCONSISTENCY_DIAGNOSIS_V0_1",
            "observations": [],
            "pain_zones": [],
            "integration_pain_points": [
                {
                    "location": "FPDG.SOURCE_HEAD_LOCK.RFC",
                    "kind": "REPOSITORY_HEAD_ADVANCED_WITH_IDENTICAL_DEPENDENCY_SURFACE",
                    "repository": "RFC",
                    "witness_locations": ["RFC.main", "FPDG.source_exports.lock.json:RFC"],
                }
            ],
        }
        evidence = {
            "schema": "FPDG_INCONSISTENCY_EVIDENCE_V0_1",
            "observations": [{"observation_id": "dummy", "kind": "OTHER"}],
        }
        # Integration-only diagnosis intentionally does not reference the dummy observation.
        report = localize(diagnosis, evidence)
        self.assertEqual(report["integration_coordinates"][0]["location"], "FPDG.SOURCE_HEAD_LOCK.RFC")
        self.assertEqual(report["finest_precision"], "INTEGRATION_METADATA_LOCATION")


if __name__ == "__main__":
    unittest.main()
