import unittest

from tools.diagnose_inconsistency import diagnose, load_claims, load_graph
from tools.ingest_validation_failure import ReceiptError, receipt_to_evidence
from tools.localize_micro_coordinates import localize as localize_micro


class ValidationFailureIngressTests(unittest.TestCase):
    def receipt(self):
        return {
            "schema": "FPDG_VALIDATION_FAILURE_RECEIPT_V0_1",
            "repository_id": "RFC",
            "repository": "AdrianLipa90/Relational-Field-Closure",
            "source_commit": "a" * 40,
            "workflow": "RFC exact validation",
            "job": "rf-e20",
            "run_id": 123,
            "status": "FAIL",
            "failures": [
                {
                    "failure_id": "RF_E20_MASS_SCALE",
                    "kind": "EQUATION_CHECK_FAILURE",
                    "claim_id": "RFC.E20.TETRA_CLOCK_MASS_SCALE",
                    "expected": "dimensionally_closed",
                    "observed": "scale_unresolved",
                    "source_locator": {
                        "path": "closure/einstein/RF_E20_TETRA_CLOCK_MASS_SCALE_CLOSURE.md",
                        "equation_id": "RF-E20.17",
                        "line_start": 412,
                        "line_end": 419,
                        "validator_id": "test_rf_e20_mass_scale",
                        "receipt_ref": "RF_E20_SCALE_RECEIPT.json",
                    },
                    "evidence_refs": ["validator:rf-e20"],
                }
            ],
        }

    def test_receipt_preserves_exact_source_locator(self):
        evidence = receipt_to_evidence(self.receipt())
        obs = evidence["observations"][0]
        self.assertEqual(obs["claim_id"], "RFC.E20.TETRA_CLOCK_MASS_SCALE")
        self.assertEqual(obs["source_locator"]["equation_id"], "RF-E20.17")
        self.assertEqual(obs["source_locator"]["line_start"], 412)
        self.assertIn("source-commit:RFC:" + "a" * 40, obs["evidence_refs"])

    def test_full_localization_reaches_source_range_without_inference(self):
        evidence = receipt_to_evidence(self.receipt())
        diagnosis = diagnose(load_graph(), load_claims(), evidence)
        self.assertEqual(diagnosis["status"], "LOCALIZED")
        self.assertEqual(diagnosis["minimal_failing_frontier"], ["RFC.E20.TETRA_CLOCK_MASS_SCALE"])
        micro = localize_micro(diagnosis, evidence)
        self.assertEqual(micro["finest_precision"], "SOURCE_RANGE")
        self.assertFalse(micro["causal_inference_performed"])
        coordinate = micro["coordinates"][0]
        self.assertEqual(coordinate["source_locator"]["line_end"], 419)

    def test_line_end_without_start_fails_closed(self):
        receipt = self.receipt()
        receipt["failures"][0]["source_locator"].pop("line_start")
        with self.assertRaises(ReceiptError):
            receipt_to_evidence(receipt)

    def test_failure_requires_claim_or_locator(self):
        receipt = self.receipt()
        receipt["failures"][0].pop("claim_id")
        receipt["failures"][0].pop("source_locator")
        with self.assertRaises(ReceiptError):
            receipt_to_evidence(receipt)


if __name__ == "__main__":
    unittest.main()
