import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from impact import compute_impact, load_graph


class ImpactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = load_graph()

    def ids(self, claim, include_candidates=False):
        return {
            row["claim_id"]
            for row in compute_impact(self.graph, claim, include_candidates)
        }

    def test_clock_revalidates_adm_chain(self):
        impacted = self.ids("IDT.CLOCK.GAMMA_T")
        for claim in (
            "RFC.ADM.E8",
            "RFC.ADM.E9",
            "RFC.ADM.E10",
            "RFC.ADM.E11",
            "RFC.ADM.E12",
            "RFC.ADM.E13",
            "RFC.PHYSICAL_SCALE_COUPLING",
        ):
            self.assertIn(claim, impacted)
        self.assertNotIn("IDT.RELATIVISTIC.FIELD_BRIDGE", impacted)

    def test_hardened_rfm1_rfe0_bridge_reaches_einstein_closure(self):
        impacted = self.ids("RFC.SOURCE.CONSERVED_CARRIER")
        self.assertIn("IDT.RELATIVISTIC.FIELD_BRIDGE", impacted)
        self.assertIn("IDT.EINSTEIN.CLOSURE", impacted)

    def test_candidate_edges_are_isolated_by_default(self):
        self.assertEqual(self.ids("SOH.SU2.DOUBLE_COVER"), set())
        self.assertIn(
            "IDT.HALF_SEAM.DOUBLE_COVER_SIGNATURE",
            self.ids("SOH.SU2.DOUBLE_COVER", include_candidates=True),
        )

    def test_time_join_reaches_temporal_and_relativistic_spines(self):
        impacted = self.ids("TIR.TIME_JOIN")
        self.assertIn("IDT.TEMPORAL.PRIMITIVE", impacted)
        self.assertIn("IDT.RETRODICTION", impacted)
        self.assertIn("RFC.ADM.E13", impacted)
        self.assertIn("IDT.RELATIVISTIC.FIELD_BRIDGE", impacted)
        self.assertIn("IDT.EINSTEIN.CLOSURE", impacted)

    def test_unknown_claim_fails(self):
        with self.assertRaises(KeyError):
            compute_impact(self.graph, "UNKNOWN.CLAIM")


if __name__ == "__main__":
    unittest.main()
