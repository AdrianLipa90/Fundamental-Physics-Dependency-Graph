import copy
import json
import unittest
from pathlib import Path

from tools.validate_global_gr_production_bundle import (
    ProductionBundleError,
    REQUIRED_GATES,
    validate_global_gr_production_bundle,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "global_gr_production_witness_bundle_reference_v0_1.json"


class GlobalGRProductionWitnessBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def production_control(self):
        payload = copy.deepcopy(self.reference)
        payload["bundle_id"] = "PRODUCTION_SHAPED_CONTROL_ONLY"
        payload["production"] = True
        payload["evidence_class"] = "PRODUCTION"
        for gate_id, expected in REQUIRED_GATES.items():
            gate = payload["gates"][gate_id]
            gate["production"] = True
            gate["evidence_class"] = "PRODUCTION"
            gate["observed_verdict"] = expected["required_verdict"]
        for witness in payload["global_witnesses"].values():
            witness["production"] = True
            witness["evidence_class"] = "PRODUCTION"
        return payload

    def test_reference_fixture_is_structurally_valid_but_never_promotable(self):
        cert = validate_global_gr_production_bundle(self.reference)
        self.assertTrue(cert.structural_pass)
        self.assertFalse(cert.production_promotable)
        self.assertFalse(cert.global_gr_cauchy_carrier_eligible)
        self.assertEqual(cert.gate_count, 6)
        self.assertEqual(cert.witness_count, 3)
        self.assertEqual(cert.production_status, "REFERENCE_CONTROL_ONLY_NO_PRODUCTION_PROMOTION")

    def test_production_shaped_control_exercises_full_promotion_logic(self):
        cert = validate_global_gr_production_bundle(self.production_control())
        self.assertTrue(cert.structural_pass)
        self.assertTrue(cert.production_promotable)
        self.assertTrue(cert.global_gr_cauchy_carrier_eligible)
        self.assertEqual(cert.production_status, "ELIGIBLE_FOR_SOURCE_OWNED_PRODUCTION_PROMOTION")

    def test_reference_bundle_cannot_be_promoted_by_flipping_top_level_flag(self):
        payload = copy.deepcopy(self.reference)
        payload["production"] = True
        with self.assertRaisesRegex(ProductionBundleError, "incompatible with production"):
            validate_global_gr_production_bundle(payload)

    def test_synthetic_evidence_class_is_rejected(self):
        payload = copy.deepcopy(self.reference)
        payload["evidence_class"] = "SYNTHETIC"
        with self.assertRaisesRegex(ProductionBundleError, "synthetic/fixture classes are inadmissible"):
            validate_global_gr_production_bundle(payload)

    def test_missing_gate_fails_closed(self):
        payload = copy.deepcopy(self.reference)
        del payload["gates"]["GSC-4"]
        with self.assertRaisesRegex(ProductionBundleError, "gates must be exactly"):
            validate_global_gr_production_bundle(payload)

    def test_wrong_source_owner_fails_closed(self):
        payload = copy.deepcopy(self.reference)
        payload["gates"]["GSC-5"]["source_repository"] = "AdrianLipa90/Informational-Dynamics-of-Time"
        with self.assertRaisesRegex(ProductionBundleError, "source_repository"):
            validate_global_gr_production_bundle(payload)

    def test_bad_source_commit_fails_closed(self):
        payload = copy.deepcopy(self.reference)
        payload["gates"]["GSC-2"]["source_commit"] = "deadbeef"
        with self.assertRaisesRegex(ProductionBundleError, "40-hex"):
            validate_global_gr_production_bundle(payload)

    def test_receipt_digest_collision_fails_closed(self):
        payload = copy.deepcopy(self.reference)
        payload["gates"]["GSC-6"]["receipt_sha256"] = payload["gates"]["GSC-5"]["receipt_sha256"]
        with self.assertRaisesRegex(ProductionBundleError, "digest collision"):
            validate_global_gr_production_bundle(payload)

    def test_lineage_mismatch_fails_closed(self):
        payload = copy.deepcopy(self.reference)
        payload["gates"]["GSC-3"]["lineage_id"] = "different-lineage"
        with self.assertRaisesRegex(ProductionBundleError, "lineage_id"):
            validate_global_gr_production_bundle(payload)

    def test_target_domain_mismatch_fails_closed(self):
        payload = copy.deepcopy(self.reference)
        payload["global_witnesses"]["target_domain_coverage"]["target_domain_id"] = "other-domain"
        with self.assertRaisesRegex(ProductionBundleError, "target_domain_id"):
            validate_global_gr_production_bundle(payload)

    def test_gsc5_parent_digest_must_bind_supplied_gsc4_receipt(self):
        payload = copy.deepcopy(self.reference)
        payload["dependencies"]["GSC-5"]["GSC-4"] = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        with self.assertRaisesRegex(ProductionBundleError, "does not bind"):
            validate_global_gr_production_bundle(payload)

    def test_gsc6_parent_digest_must_bind_supplied_gsc5_receipt(self):
        payload = copy.deepcopy(self.reference)
        payload["dependencies"]["GSC-6"]["GSC-5"] = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        with self.assertRaisesRegex(ProductionBundleError, "does not bind"):
            validate_global_gr_production_bundle(payload)

    def test_production_observed_verdict_must_equal_source_required_verdict(self):
        payload = self.production_control()
        payload["gates"]["GSC-6"]["observed_verdict"] = "REFERENCE_CONTROL_PASS"
        with self.assertRaisesRegex(ProductionBundleError, "production receipt must observe"):
            validate_global_gr_production_bundle(payload)

    def test_missing_target_domain_coverage_fails_closed(self):
        payload = copy.deepcopy(self.reference)
        payload["global_witnesses"]["target_domain_coverage"]["covers_target_domain"] = False
        with self.assertRaisesRegex(ProductionBundleError, "full target-domain coverage"):
            validate_global_gr_production_bundle(payload)

    def test_nonpositive_global_lapse_bound_fails_closed(self):
        payload = copy.deepcopy(self.reference)
        payload["global_witnesses"]["global_lapse_upper_bound"]["n_max"] = 0.0
        with self.assertRaisesRegex(ProductionBundleError, "finite and positive"):
            validate_global_gr_production_bundle(payload)

    def test_uncertified_global_lapse_bound_fails_closed(self):
        payload = copy.deepcopy(self.reference)
        payload["global_witnesses"]["global_lapse_upper_bound"]["globally_certified"] = False
        with self.assertRaisesRegex(ProductionBundleError, "globally certified"):
            validate_global_gr_production_bundle(payload)

    def test_incomplete_wick_metric_fails_closed(self):
        payload = copy.deepcopy(self.reference)
        payload["global_witnesses"]["adm_wick_completeness"]["complete"] = False
        with self.assertRaisesRegex(ProductionBundleError, "certify completeness"):
            validate_global_gr_production_bundle(payload)


if __name__ == "__main__":
    unittest.main()
