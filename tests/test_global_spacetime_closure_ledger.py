import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts" / "GLOBAL_SPACETIME_CLOSURE_LEDGER_V0_1.json"
LEDGER = ROOT / "interfaces" / "GLOBAL_SPACETIME_CLOSURE_LEDGER_V0_1.md"


class GlobalSpacetimeClosureLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(RECEIPT.read_text(encoding="utf-8"))
        cls.ledger = LEDGER.read_text(encoding="utf-8")

    def test_authority_firewall(self):
        self.assertEqual(self.payload["schema"], "FPDG_GLOBAL_SPACETIME_CLOSURE_LEDGER_V0_1")
        self.assertEqual(self.payload["authority"], "NONCANONICAL_CROSS_REPO_AUDIT")
        self.assertFalse(self.payload["promotion_authority"])
        self.assertFalse(self.payload["canonical_graph_mutated"])
        self.assertFalse(self.payload["canonical_source_locks_mutated"])
        self.assertFalse(self.payload["promotion_firewall"]["gremlin_promotion_authority"])

    def test_exact_source_heads(self):
        expected = {
            "TIR": "2568fb24e0bc91e8f1c75dcfdc5659a57ca382b9",
            "IDT": "fc87c4176dfcc480529ba28bd67042d3ebf02c72",
            "RFC": "4d581ac8d03e637f65fdefa2b9326ffc1effe0e1",
        }
        for source, sha in expected.items():
            self.assertEqual(self.payload["sources"][source]["exact_head"], sha)
            self.assertEqual(len(sha), 40)

    def test_pinned_certifier_workflows_are_success(self):
        self.assertEqual(self.payload["sources"]["TIR"]["workflow"]["conclusion"], "SUCCESS")
        idt = self.payload["sources"]["IDT"]["gates"]
        self.assertEqual(idt["05G"]["conclusion"], "SUCCESS")
        self.assertEqual(idt["05H"]["conclusion"], "SUCCESS")
        self.assertEqual(idt["05I"]["workflow"]["conclusion"], "SUCCESS")
        rfc = self.payload["sources"]["RFC"]["gates"]
        self.assertEqual(rfc["RF-E24"]["conclusion"], "SUCCESS")
        self.assertEqual(rfc["RF-E25"]["conclusion"], "SUCCESS")

    def test_05i_diagnostic_failure_precedes_assertions(self):
        failed = self.payload["sources"]["IDT"]["gates"]["05I"]["diagnostic_failed_run"]
        self.assertEqual(failed["run_number"], 1)
        self.assertEqual(failed["run_id"], 33339745130)
        self.assertEqual(failed["class"], "WORKFLOW_DEPENDENCY_ENVIRONMENT")
        self.assertFalse(failed["mathematical_assertions_executed"])

    def test_idt_full_suite_blocker_is_kept_separate(self):
        blocker = self.payload["sources"]["IDT"]["full_reference_suite_baseline_blocker"]
        self.assertEqual(blocker["main_run_number"], 925)
        self.assertEqual(blocker["exact_head_run_number"], 928)
        self.assertEqual(blocker["class"], "PRE_EXISTING_SEAM_COLLECTION_IMPORT")
        self.assertEqual(blocker["symbol"], "onsager_dissipation")
        self.assertTrue(blocker["independent_of_05I_gate"])

    def test_global_frontier_is_complete_and_fail_closed(self):
        rows = self.payload["global_frontier"]
        self.assertEqual([row["id"] for row in rows], [f"GSC-{i}" for i in range(1, 7)])
        by_id = {row["id"]: row for row in rows}
        self.assertEqual(by_id["GSC-1"]["status"], "OPEN_INPUT")
        self.assertEqual(by_id["GSC-2"]["status"], "OPEN_INPUT")
        self.assertEqual(
            by_id["GSC-3"]["status"],
            "CERTIFIER_PASS_WITH_PRODUCTION_REGULAR_CLOCK_WITNESS_OPEN_INPUT",
        )
        self.assertEqual(by_id["GSC-3"]["certifier"], "IDT_05I")
        self.assertEqual(
            by_id["GSC-4"]["status"],
            "CERTIFIER_PASS_WITH_PRODUCTION_SHARED_ATLAS_OPEN_INPUT",
        )
        self.assertEqual(by_id["GSC-4"]["certifier"], "RFC_RF-E25")
        self.assertEqual(
            by_id["GSC-5"]["status"],
            "CONDITIONAL_ON_PRODUCTION_PASS_GSC_1_TO_GSC_4",
        )
        self.assertEqual(by_id["GSC-6"]["status"], "OPEN_SEPARATE_GATE")

    def test_05i_and_rfe25_certifiers_are_closed_but_production_is_open(self):
        closed = self.payload["closed_surfaces"]
        self.assertIn("IDT_REGULAR_SMOOTH_CLOCK_EXTENSION_WITNESS_CERTIFIER", closed)
        self.assertIn("RFC_SHARED_SPACETIME_ATLAS_COCYCLE_CERTIFIER", closed)
        overall = self.payload["overall_status"]
        self.assertIn("REGULAR_CLOCK_EXTENSION_CERTIFIER_PASS", overall)
        self.assertIn("SHARED_ATLAS_CERTIFIER_PASS", overall)
        self.assertIn("GLOBAL_SPACETIME_REALIZATION_INPUT_OPEN", overall)

    def test_global_pass_language_remains_blocked(self):
        overall = self.payload["overall_status"]
        for forbidden in self.payload["promotion_firewall"]["forbidden_overall_statuses_while_frontier_open"]:
            self.assertNotEqual(overall, forbidden)
        self.assertIn("GLOBAL_HYPERBOLICITY_OPEN", overall)
        self.assertEqual(
            self.payload["verdict"],
            "PASS_CROSS_REPO_LEDGER_WITH_GLOBAL_REALIZATION_INPUT_OPEN",
        )

    def test_ledger_names_both_executable_global_interface_gates(self):
        self.assertIn("IDT 05I regular smooth-clock extension witness certifier", self.ledger)
        self.assertIn("RFC RF-E25 shared atlas/coframe cocycle certifier", self.ledger)
        self.assertIn("CERTIFIER_PASS_WITH_PRODUCTION_REGULAR_CLOCK_WITNESS_OPEN_INPUT", self.ledger)
        self.assertIn("CERTIFIER_PASS_WITH_PRODUCTION_SHARED_ATLAS_OPEN_INPUT", self.ledger)

    def test_canonical_files_are_immutable_surfaces(self):
        for name in (
            "dependency_graph.yaml",
            "claims.jsonl",
            "source_export_heads.yaml",
            "source_exports.lock.json",
        ):
            self.assertIn(name, self.ledger)


if __name__ == "__main__":
    unittest.main()
