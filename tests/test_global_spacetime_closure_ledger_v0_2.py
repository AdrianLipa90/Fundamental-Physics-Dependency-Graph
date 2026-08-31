import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts" / "GLOBAL_SPACETIME_CLOSURE_LEDGER_V0_2.json"
LEDGER = ROOT / "interfaces" / "GLOBAL_SPACETIME_CLOSURE_LEDGER_V0_2.md"


class GlobalSpacetimeClosureLedgerV02Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(RECEIPT.read_text(encoding="utf-8"))
        cls.ledger = LEDGER.read_text(encoding="utf-8")

    def test_authority_firewall(self):
        self.assertEqual(self.payload["schema"], "FPDG_GLOBAL_SPACETIME_CLOSURE_LEDGER_V0_2")
        self.assertEqual(self.payload["authority"], "NONCANONICAL_CROSS_REPO_AUDIT")
        self.assertFalse(self.payload["promotion_authority"])
        self.assertFalse(self.payload["canonical_graph_mutated"])
        self.assertFalse(self.payload["canonical_source_locks_mutated"])
        self.assertFalse(self.payload["promotion_firewall"]["gremlin_promotion_authority"])

    def test_v02_is_based_on_current_federated_main(self):
        self.assertEqual(
            self.payload["fpdg_base"]["main_commit"],
            "1e5e46a214c141bb07aa422740038b10a38f57d8",
        )
        self.assertEqual(
            self.payload["fpdg_base"]["state"],
            "POST_MERGE_V0_4_FEDERATION_WITH_REFRESHED_SOURCE_LOCKS",
        )

    def test_current_main_heads_are_pinned(self):
        expected = {
            "TIR": "62a13ba92f0db641d6d699a88059aedf33528300",
            "IDT": "f186aab6024a592be406684785069edfe2f3d5bf",
            "RFC": "012d4aa790bca7d631caf5c8002bebaa3a07710a",
            "FPDG": "1e5e46a214c141bb07aa422740038b10a38f57d8",
        }
        self.assertEqual(self.payload["current_main_heads"], expected)
        for sha in expected.values():
            self.assertEqual(len(sha), 40)

    def test_hosted_closure_witnesses_are_success(self):
        witnesses = self.payload["validated_witnesses"]
        for key in (
            "TIR_A5",
            "IDT_05I",
            "RFC_RF_E24",
            "RFC_RF_E25",
            "RFC_RF_E26",
            "RFC_RF_L8",
        ):
            self.assertEqual(witnesses[key]["conclusion"], "SUCCESS")

    def test_rfe26_exact_head_and_run_are_frozen(self):
        rfe26 = self.payload["validated_witnesses"]["RFC_RF_E26"]
        self.assertEqual(rfe26["head"], "d9779608754aae294e3a37a5e5c9fef63ff37a39")
        self.assertEqual(rfe26["workflow_run_number"], 401)
        self.assertEqual(rfe26["workflow_run_id"], 33341138133)
        self.assertEqual(
            rfe26["status"],
            "PASS_GLOBAL_EINSTEIN_CARRIER_CERTIFIER_WITH_PRODUCTION_INPUT_OPEN",
        )

    def test_rfe26_diagnostic_failure_was_pre_assertion(self):
        failed = self.payload["validated_witnesses"]["RFC_RF_E26"]["diagnostic_failed_run"]
        self.assertEqual(failed["workflow_run_number"], 400)
        self.assertEqual(failed["workflow_run_id"], 33341085574)
        self.assertEqual(failed["class"], "TEST_IMPORT_LAYOUT")
        self.assertFalse(failed["mathematical_assertions_executed"])

    def test_rfl8_exact_head_and_run_are_frozen(self):
        rfl8 = self.payload["validated_witnesses"]["RFC_RF_L8"]
        self.assertEqual(rfl8["head"], "329bdcf981245189b52cea81509bf983c0396668")
        self.assertEqual(rfl8["workflow_run_number"], 402)
        self.assertEqual(rfl8["workflow_run_id"], 33341545793)
        self.assertEqual(
            rfl8["status"],
            "PASS_UNIFORM_TEMPORAL_GLOBAL_HYPERBOLICITY_CERTIFIER_WITH_COMPLETENESS_INPUT_OPEN",
        )
        self.assertEqual(rfl8["epsilon"], "(1+N_max^2)^(-1/2)")

    def test_global_frontier_is_complete_and_typed(self):
        rows = self.payload["global_frontier"]
        self.assertEqual([row["id"] for row in rows], [f"GSC-{i}" for i in range(1, 7)])
        by_id = {row["id"]: row for row in rows}
        self.assertEqual(by_id["GSC-1"]["status"], "OPEN_INPUT")
        self.assertEqual(by_id["GSC-2"]["status"], "OPEN_INPUT")
        self.assertEqual(
            by_id["GSC-3"]["status"],
            "CERTIFIER_PASS_WITH_PRODUCTION_REGULAR_CLOCK_WITNESS_OPEN_INPUT",
        )
        self.assertEqual(
            by_id["GSC-4"]["status"],
            "CERTIFIER_PASS_WITH_PRODUCTION_SHARED_ATLAS_OPEN_INPUT",
        )
        self.assertEqual(
            by_id["GSC-5"]["status"],
            "CERTIFIER_PASS_WITH_PRODUCTION_GSC_1_TO_GSC_4_AND_DOMAIN_COVERAGE_OPEN_INPUT",
        )
        self.assertEqual(by_id["GSC-5"]["certifier"], "RFC_RF-E26")
        self.assertEqual(
            by_id["GSC-6"]["status"],
            "CERTIFIER_PASS_WITH_PRODUCTION_GLOBAL_LAPSE_BOUND_AND_WICK_COMPLETENESS_OPEN_INPUT",
        )
        self.assertEqual(by_id["GSC-6"]["certifier"], "RFC_RF-L8")

    def test_all_six_certifier_layers_are_closed_but_production_is_open(self):
        closed = self.payload["closed_surfaces"]
        self.assertIn("RFC_GLOBAL_EINSTEIN_CARRIER_GLUE_CERTIFIER", closed)
        self.assertIn("RFC_UNIFORM_TEMPORAL_GLOBAL_HYPERBOLICITY_CERTIFIER", closed)
        overall = self.payload["overall_status"]
        self.assertIn("GLOBAL_EINSTEIN_CARRIER_CERTIFIER_PASS", overall)
        self.assertIn("GLOBAL_HYPERBOLICITY_CERTIFIER_PASS", overall)
        self.assertIn("PRODUCTION_GLOBAL_SPACETIME_REALIZATION_OPEN", overall)
        self.assertIn("PRODUCTION_GLOBAL_CAUSALITY_WITNESSES_OPEN", overall)

    def test_rfl8_keeps_completeness_and_lapse_bound_as_production_inputs(self):
        rfl8 = self.payload["validated_witnesses"]["RFC_RF_L8"]
        self.assertIn("GLOBAL_FINITE_LAPSE_UPPER_BOUND", rfl8["production_inputs"])
        self.assertIn("COMPLETE_ADM_WICK_METRIC", rfl8["production_inputs"])
        self.assertIn("complete ADM Wick metric", self.ledger)
        self.assertIn("certified global finite lapse upper bound", self.ledger)

    def test_final_gr_composition_requires_production_gsc5_and_gsc6(self):
        final = self.payload["final_composition"]
        self.assertEqual(
            final["global_gr_cauchy_carrier"],
            "PRODUCTION_GSC_5_PLUS_PRODUCTION_GSC_6",
        )
        self.assertEqual(
            final["status"],
            "CERTIFIER_LAYER_COMPLETE__PRODUCTION_WITNESSES_OPEN",
        )
        self.assertIn("production GSC-5 + production GSC-6", self.ledger)

    def test_global_pass_language_remains_blocked(self):
        overall = self.payload["overall_status"]
        for forbidden in self.payload["promotion_firewall"]["forbidden_overall_promotions"]:
            self.assertNotEqual(overall, forbidden)
        self.assertEqual(
            self.payload["verdict"],
            "PASS_GSC_1_TO_GSC_6_CERTIFIER_LAYER_WITH_PRODUCTION_REALIZATION_INPUTS_OPEN",
        )

    def test_canonical_files_remain_immutable_surfaces(self):
        for name in (
            "dependency_graph.yaml",
            "claims.jsonl",
            "source_export_heads.yaml",
            "source_exports.lock.json",
        ):
            self.assertIn(name, self.ledger)


if __name__ == "__main__":
    unittest.main()
