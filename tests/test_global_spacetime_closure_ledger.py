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
            "TIR": "5aaf572e9e931525f16bb0fa105afbb0d34c59c9",
            "IDT": "44e2da0a7048df387f277f4e93e6970c445d4b67",
            "RFC": "4d581ac8d03e637f65fdefa2b9326ffc1effe0e1",
        }
        for source, sha in expected.items():
            self.assertEqual(self.payload["sources"][source]["exact_head"], sha)
            self.assertEqual(len(sha), 40)

    def test_new_input_contract_workflows_are_success(self):
        tir = self.payload["sources"]["TIR"]["gates"]["GSC-1_INPUT"]["workflow"]
        self.assertEqual(tir["run_id"], 33343473631)
        self.assertEqual(tir["conclusion"], "SUCCESS")
        idt = self.payload["sources"]["IDT"]["gates"]["05J"]["workflow"]
        self.assertEqual(idt["run_id"], 33343481792)
        self.assertEqual(idt["conclusion"], "SUCCESS")

    def test_parent_certifier_workflows_remain_success(self):
        self.assertEqual(self.payload["sources"]["TIR"]["gates"]["A5"]["conclusion"], "SUCCESS")
        idt = self.payload["sources"]["IDT"]["gates"]
        self.assertEqual(idt["05G"]["conclusion"], "SUCCESS")
        self.assertEqual(idt["05H"]["conclusion"], "SUCCESS")
        self.assertEqual(idt["05I"]["workflow"]["conclusion"], "SUCCESS")
        rfc = self.payload["sources"]["RFC"]["gates"]
        self.assertEqual(rfc["RF-E24"]["conclusion"], "SUCCESS")
        self.assertEqual(rfc["RF-E25"]["conclusion"], "SUCCESS")

    def test_idt_full_suite_blocker_is_kept_separate(self):
        blocker = self.payload["sources"]["IDT"]["full_reference_suite_blocker"]
        self.assertEqual(blocker["exact_head_run_number"], 935)
        self.assertEqual(blocker["exact_head_run_id"], 33343481782)
        self.assertEqual(blocker["class"], "PRE_EXISTING_SEAM_COLLECTION_IMPORT")
        self.assertEqual(blocker["symbol"], "onsager_dissipation")
        self.assertEqual(blocker["affected_test_count"], 3)
        self.assertTrue(blocker["independent_of_05J_gate"])
        self.assertTrue(blocker["independent_of_05I_gate"])

    def test_global_frontier_is_complete_and_typed_open(self):
        rows = self.payload["global_frontier"]
        self.assertEqual([row["id"] for row in rows], [f"GSC-{i}" for i in range(1, 7)])
        by_id = {row["id"]: row for row in rows}
        self.assertEqual(
            by_id["GSC-1"]["status"],
            "INPUT_CONTRACT_PASS_WITH_PRODUCTION_SPATIAL_COMPLEX_OPEN_INPUT",
        )
        self.assertEqual(by_id["GSC-1"]["certifier"], "TIR_GSC1_INPUT_PLUS_A5")
        self.assertEqual(
            by_id["GSC-2"]["status"],
            "INPUT_CONTRACT_PASS_WITH_PRODUCTION_EVENT_COMPLEX_OPEN_INPUT",
        )
        self.assertEqual(by_id["GSC-2"]["certifier"], "IDT_05J_PLUS_05H")
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
            "CONDITIONAL_ON_PRODUCTION_PASS_GSC_1_TO_GSC_4",
        )
        self.assertEqual(by_id["GSC-6"]["status"], "OPEN_SEPARATE_GATE")

    def test_input_contracts_are_closed_surfaces_but_production_remains_open(self):
        closed = self.payload["closed_surfaces"]
        self.assertIn("TIR_GLOBAL_SPATIAL_COMPLEX_INPUT_CONTRACT", closed)
        self.assertIn("IDT_PRODUCTION_EVENT_COMPLEX_INPUT_CONTRACT", closed)
        overall = self.payload["overall_status"]
        self.assertIn("SPATIAL_INPUT_CONTRACT_PASS", overall)
        self.assertIn("TEMPORAL_INPUT_CONTRACT_PASS", overall)
        self.assertIn("PRODUCTION_GLOBAL_SPACETIME_OPEN", overall)

    def test_global_pass_language_remains_blocked(self):
        overall = self.payload["overall_status"]
        for forbidden in self.payload["promotion_firewall"]["forbidden_overall_statuses_while_frontier_open"]:
            self.assertNotEqual(overall, forbidden)
        self.assertIn("GLOBAL_HYPERBOLICITY_OPEN", overall)
        self.assertEqual(
            self.payload["verdict"],
            "PASS_CROSS_REPO_LEDGER_WITH_TYPED_PRODUCTION_INPUTS_OPEN",
        )

    def test_ledger_names_all_four_executable_production_interfaces(self):
        for token in (
            "TIR GSC-1 spatial input contract",
            "IDT 05J explicit occurrence-to-event quotient/input contract",
            "IDT 05I regular smooth-clock extension certifier",
            "RFC RF-E25 shared atlas/coframe cocycle certifier",
            "INPUT_CONTRACT_PASS_WITH_PRODUCTION_SPATIAL_COMPLEX_OPEN_INPUT",
            "INPUT_CONTRACT_PASS_WITH_PRODUCTION_EVENT_COMPLEX_OPEN_INPUT",
            "CERTIFIER_PASS_WITH_PRODUCTION_REGULAR_CLOCK_WITNESS_OPEN_INPUT",
            "CERTIFIER_PASS_WITH_PRODUCTION_SHARED_ATLAS_OPEN_INPUT",
        ):
            self.assertIn(token, self.ledger)

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
