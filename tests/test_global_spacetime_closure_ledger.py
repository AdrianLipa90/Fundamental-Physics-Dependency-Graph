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

    def test_schema_and_authority_firewall(self):
        self.assertEqual(
            self.payload["schema"],
            "FPDG_GLOBAL_SPACETIME_CLOSURE_LEDGER_V0_1",
        )
        self.assertEqual(self.payload["authority"], "NONCANONICAL_CROSS_REPO_AUDIT")
        self.assertFalse(self.payload["promotion_authority"])
        self.assertFalse(self.payload["canonical_graph_mutated"])
        self.assertFalse(self.payload["canonical_source_locks_mutated"])
        self.assertFalse(self.payload["promotion_firewall"]["gremlin_promotion_authority"])

    def test_exact_source_heads_are_frozen(self):
        expected = {
            "TIR": "2568fb24e0bc91e8f1c75dcfdc5659a57ca382b9",
            "IDT": "a36cdb7bffa3789bef154c2b987ebab68ccfb2d5",
            "RFC": "4d581ac8d03e637f65fdefa2b9326ffc1effe0e1",
        }
        for source, sha in expected.items():
            self.assertEqual(self.payload["sources"][source]["exact_head"], sha)
            self.assertEqual(len(sha), 40)

    def test_all_pinned_hosted_workflows_are_success(self):
        self.assertEqual(self.payload["sources"]["TIR"]["workflow"]["conclusion"], "SUCCESS")
        self.assertEqual(self.payload["sources"]["IDT"]["gates"]["05G"]["conclusion"], "SUCCESS")
        self.assertEqual(self.payload["sources"]["IDT"]["gates"]["05H"]["conclusion"], "SUCCESS")
        self.assertEqual(self.payload["sources"]["RFC"]["gates"]["RF-E24"]["conclusion"], "SUCCESS")
        self.assertEqual(self.payload["sources"]["RFC"]["gates"]["RF-E25"]["conclusion"], "SUCCESS")

    def test_rfe25_diagnostic_failure_is_typed_nonmathematical(self):
        failed = self.payload["sources"]["RFC"]["gates"]["RF-E25"]["diagnostic_failed_run"]
        self.assertEqual(failed["run_number"], 391)
        self.assertEqual(failed["run_id"], 33337107285)
        self.assertEqual(failed["class"], "TEST_IMPORT_LAYOUT")
        self.assertFalse(failed["mathematical_assertions_executed"])

    def test_global_frontier_is_complete_and_fail_closed(self):
        rows = self.payload["global_frontier"]
        self.assertEqual([row["id"] for row in rows], [f"GSC-{i}" for i in range(1, 7)])
        by_id = {row["id"]: row for row in rows}
        self.assertEqual(by_id["GSC-1"]["status"], "OPEN_INPUT")
        self.assertEqual(by_id["GSC-2"]["status"], "OPEN_INPUT")
        self.assertEqual(by_id["GSC-3"]["status"], "OPEN_INTERFACE")
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

    def test_shared_atlas_certifier_is_closed_but_production_input_is_open(self):
        self.assertIn(
            "RFC_SHARED_SPACETIME_ATLAS_COCYCLE_CERTIFIER",
            self.payload["closed_surfaces"],
        )
        overall = self.payload["overall_status"]
        self.assertIn("SHARED_ATLAS_CERTIFIER_PASS", overall)
        self.assertIn("GLOBAL_SPACETIME_REALIZATION_INPUT_OPEN", overall)

    def test_open_frontier_blocks_global_pass_language(self):
        overall = self.payload["overall_status"]
        forbidden = self.payload["promotion_firewall"]["forbidden_overall_statuses_while_frontier_open"]
        for status in forbidden:
            self.assertNotEqual(overall, status)
        self.assertIn("GLOBAL_HYPERBOLICITY_OPEN", overall)
        self.assertEqual(
            self.payload["verdict"],
            "PASS_CROSS_REPO_LEDGER_WITH_GLOBAL_REALIZATION_INPUT_OPEN",
        )

    def test_ledger_names_rfe25_joint_compatibility_gate(self):
        self.assertIn("RFC RF-E25 shared atlas/coframe cocycle certifier", self.ledger)
        self.assertIn("CERTIFIER_PASS_WITH_PRODUCTION_SHARED_ATLAS_OPEN_INPUT", self.ledger)
        self.assertIn("GSC-4 — shared spatial-temporal realization", self.ledger)
        self.assertIn("PRODUCTION_SHARED_SPACETIME_ATLAS", self.ledger)

    def test_canonical_files_are_only_referenced_as_immutable_surfaces(self):
        for name in (
            "dependency_graph.yaml",
            "claims.jsonl",
            "source_export_heads.yaml",
            "source_exports.lock.json",
        ):
            self.assertIn(name, self.ledger)


if __name__ == "__main__":
    unittest.main()
