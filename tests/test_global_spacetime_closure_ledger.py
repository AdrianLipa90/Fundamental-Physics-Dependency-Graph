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

    def test_exact_input_contract_heads(self):
        self.assertEqual(
            self.payload["sources"]["TIR"]["exact_head"],
            "5cc9f1e1a33972cf89369a3b97716e04901324ba",
        )
        self.assertEqual(
            self.payload["sources"]["IDT"]["exact_head"],
            "5a2ddc1cba572011a517657aca0174667cf1da08",
        )
        self.assertEqual(
            self.payload["sources"]["RFC"]["research_stack_head"],
            "329bdcf981245189b52cea81509bf983c0396668",
        )

    def test_hosted_certifier_workflows_are_success(self):
        tir = self.payload["sources"]["TIR"]["gates"]
        self.assertEqual(tir["A5"]["conclusion"], "SUCCESS")
        self.assertEqual(tir["GSC-1_INPUT"]["workflow"]["run_id"], 33346010181)
        self.assertEqual(tir["GSC-1_INPUT"]["workflow"]["conclusion"], "SUCCESS")

        idt = self.payload["sources"]["IDT"]["gates"]
        self.assertEqual(idt["05G"]["conclusion"], "SUCCESS")
        self.assertEqual(idt["05H"]["conclusion"], "SUCCESS")
        self.assertEqual(idt["05I"]["workflow"]["run_id"], 33349376506)
        self.assertEqual(idt["05I"]["workflow"]["conclusion"], "SUCCESS")
        self.assertEqual(idt["05J"]["workflow"]["run_id"], 33349376515)
        self.assertEqual(idt["05J"]["workflow"]["conclusion"], "SUCCESS")

        rfc = self.payload["sources"]["RFC"]["gates"]
        self.assertEqual(rfc["RF-E24"]["conclusion"], "SUCCESS")
        self.assertEqual(rfc["RF-E25"]["conclusion"], "SUCCESS")
        self.assertEqual(rfc["RF-E26"]["workflow"]["run_id"], 33341138133)
        self.assertEqual(rfc["RF-E26"]["workflow"]["conclusion"], "SUCCESS")
        self.assertEqual(rfc["RF-L8"]["workflow"]["run_id"], 33341545793)
        self.assertEqual(rfc["RF-L8"]["workflow"]["conclusion"], "SUCCESS")

    def test_stale_source_receipt_hosted_fields_are_explicit(self):
        rfc = self.payload["sources"]["RFC"]["gates"]
        self.assertEqual(
            rfc["RF-E26"]["static_receipt_hosted_field"],
            "PENDING_STALE_RELATIVE_TO_HOSTED_RUN",
        )
        self.assertEqual(
            rfc["RF-L8"]["static_receipt_hosted_field"],
            "PENDING_STALE_RELATIVE_TO_HOSTED_RUN",
        )

    def test_idt_current_integration_is_full_suite_green(self):
        idt = self.payload["sources"]["IDT"]
        self.assertFalse(idt["parallel_research_heads"])
        base_suite = idt["integration_stack"]["base_reference_suite"]
        self.assertEqual(base_suite["run_id"], 33349229812)
        self.assertEqual(base_suite["passed"], 1083)
        self.assertEqual(base_suite["failed"], 0)
        self.assertEqual(base_suite["conclusion"], "SUCCESS")

        final_suite = idt["integration_stack"]["exact_head_reference_suite"]
        self.assertEqual(final_suite["run_id"], 33349376505)
        self.assertEqual(final_suite["passed"], 1106)
        self.assertEqual(final_suite["failed"], 0)
        self.assertEqual(final_suite["conclusion"], "SUCCESS")

    def test_global_frontier_has_six_typed_certifier_coordinates(self):
        rows = self.payload["global_frontier"]
        self.assertEqual([row["id"] for row in rows], [f"GSC-{i}" for i in range(1, 7)])
        by_id = {row["id"]: row for row in rows}
        expected = {
            "GSC-1": "INPUT_CONTRACT_PASS_WITH_PRODUCTION_SPATIAL_COMPLEX_OPEN_INPUT",
            "GSC-2": "INPUT_CONTRACT_PASS_WITH_PRODUCTION_EVENT_COMPLEX_OPEN_INPUT",
            "GSC-3": "CERTIFIER_PASS_WITH_PRODUCTION_REGULAR_CLOCK_WITNESS_OPEN_INPUT",
            "GSC-4": "CERTIFIER_PASS_WITH_PRODUCTION_SHARED_ATLAS_OPEN_INPUT",
            "GSC-5": "CERTIFIER_PASS_WITH_PRODUCTION_SHARED_ATLAS_AND_DOMAIN_COVERAGE_OPEN_INPUT",
            "GSC-6": "CERTIFIER_PASS_WITH_PRODUCTION_GLOBAL_LAPSE_BOUND_AND_WICK_COMPLETENESS_OPEN_INPUT",
        }
        for gate, status in expected.items():
            self.assertEqual(by_id[gate]["status"], status)
            self.assertIn("required_verdict", by_id[gate])

        self.assertEqual(by_id["GSC-5"]["certifier"], "RFC_RF-E26")
        self.assertEqual(by_id["GSC-6"]["certifier"], "RFC_RF-L8")

    def test_rfe26_and_rfl8_are_closed_certifier_surfaces(self):
        closed = self.payload["closed_surfaces"]
        self.assertIn("RFC_GLOBAL_EINSTEIN_CARRIER_GLUE_CERTIFIER", closed)
        self.assertIn("RFC_UNIFORM_TEMPORAL_GLOBAL_HYPERBOLICITY_CERTIFIER", closed)
        self.assertIn("PRODUCTION_GLOBAL_SPACETIME_OPEN", self.payload["overall_status"])
        self.assertIn("PRODUCTION_GLOBAL_HYPERBOLICITY_OPEN", self.payload["overall_status"])

    def test_production_frontier_remains_explicit(self):
        frontier = self.payload["production_frontier"]
        self.assertEqual(set(frontier), {f"GSC-{i}" for i in range(1, 7)})
        self.assertIn("domain coverage", frontier["GSC-5"])
        self.assertIn("complete ADM Wick-metric", frontier["GSC-6"])

    def test_global_pass_language_remains_blocked(self):
        overall = self.payload["overall_status"]
        forbidden = self.payload["promotion_firewall"][
            "forbidden_overall_statuses_while_production_frontier_open"
        ]
        for status in forbidden:
            self.assertNotEqual(overall, status)
        self.assertEqual(
            self.payload["verdict"],
            "PASS_CROSS_REPO_LEDGER_WITH_GSC1_TO_GSC6_CERTIFIERS_TYPED_AND_PRODUCTION_INPUTS_OPEN",
        )

    def test_ledger_names_rfe26_and_rfl8_and_production_firewalls(self):
        for token in (
            "RFC RF-E26 local-to-global tensor-gluing certifier",
            "RFC RF-L8 completely-uniform-temporal certifier",
            "CERTIFIER_PASS_WITH_PRODUCTION_SHARED_ATLAS_AND_DOMAIN_COVERAGE_OPEN_INPUT",
            "CERTIFIER_PASS_WITH_PRODUCTION_GLOBAL_LAPSE_BOUND_AND_WICK_COMPLETENESS_OPEN_INPUT",
            "GLOBAL_GR_CAUCHY_CARRIER",
            "1106/1106",
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
