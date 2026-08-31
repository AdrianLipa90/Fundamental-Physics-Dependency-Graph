import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "receipts" / "GSC_INPUT_CONTRACTS_V0_1.json"
NOTE = ROOT / "interfaces" / "GSC_INPUT_CONTRACTS_V0_1.md"


class GSCInputContractsV01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(RECEIPT.read_text(encoding="utf-8"))
        cls.note = NOTE.read_text(encoding="utf-8")

    def test_authority_is_noncanonical(self):
        self.assertEqual(cls := self.payload["authority"], "NONCANONICAL_CROSS_REPO_AUDIT")
        self.assertFalse(self.payload["promotion_authority"])
        self.assertFalse(self.payload["firewall"]["gremlin_promotion_authority"])

    def test_gsc1_contract_is_green_but_production_witness_open(self):
        row = self.payload["gsc_1"]
        self.assertEqual(row["head"], "5aaf572e9e931525f16bb0fa105afbb0d34c59c9")
        self.assertEqual(row["workflow_run_id"], 33343473631)
        self.assertEqual(row["conclusion"], "SUCCESS")
        self.assertEqual(row["input_contract_status"], "PASS")
        self.assertEqual(row["production_witness_status"], "OPEN_INPUT")

    def test_gsc2_contract_is_green_but_production_witness_open(self):
        row = self.payload["gsc_2"]
        self.assertEqual(row["head"], "44e2da0a7048df387f277f4e93e6970c445d4b67")
        self.assertEqual(row["workflow_run_id"], 33343481792)
        self.assertEqual(row["conclusion"], "SUCCESS")
        self.assertEqual(row["input_contract_status"], "PASS")
        self.assertEqual(row["production_witness_status"], "OPEN_INPUT")

    def test_current_05i_full_reference_suite_is_green(self):
        row = self.payload["idt_05i"]
        self.assertEqual(row["head"], "c5f256c1435c4174c4ac531e40be2902aa32651b")
        self.assertEqual(row["reference_suite_run_number"], 939)
        self.assertEqual(row["reference_suite_run_id"], 33343691489)
        self.assertEqual(row["conclusion"], "SUCCESS")

    def test_reference_and_phase36_cannot_replace_production_witnesses(self):
        firewall = self.payload["firewall"]
        self.assertFalse(firewall["reference_controls_are_production_witnesses"])
        self.assertFalse(firewall["phase36_distance_promotes_dependencies"])
        self.assertTrue(firewall["production_witnesses_remain_source_owned"])
        self.assertIn("No PhaseNav distance", self.note)

    def test_verdict_retains_open_inputs(self):
        self.assertEqual(
            self.payload["verdict"],
            "PASS_INPUT_CONTRACT_LAYER_WITH_GSC1_GSC2_PRODUCTION_WITNESSES_OPEN",
        )
        self.assertIn("production tetrahedral incidence witness OPEN", self.note)
        self.assertIn("production event incidence/quotient witness OPEN", self.note)


if __name__ == "__main__":
    unittest.main()
