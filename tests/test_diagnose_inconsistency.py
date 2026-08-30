import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


diagnose_mod = load_module("diagnose_inconsistency", TOOLS / "diagnose_inconsistency.py")
gremlin_mod = load_module("build_gremlin_pain_packet", TOOLS / "build_gremlin_pain_packet.py")


class PainLocalizationTests(unittest.TestCase):
    def setUp(self):
        self.graph = {
            "nodes": [
                {"claim_id": "TIR.A", "repository": "TIR", "status": "PASS", "source": "a.md"},
                {"claim_id": "IDT.B", "repository": "IDT", "status": "PASS", "source": "b.md"},
                {"claim_id": "RFC.C", "repository": "RFC", "status": "PASS", "source": "c.md"},
                {"claim_id": "RFC.D", "repository": "RFC", "status": "PASS", "source": "d.md"},
                {"claim_id": "SOH.X", "repository": "SOH", "status": "CANDIDATE", "source": "x.md"},
            ],
            "edges": [
                {"from": "TIR.A", "to": "IDT.B", "authority": "CANONICAL_CROSS_REPO"},
                {"from": "IDT.B", "to": "RFC.C", "authority": "CANONICAL_CROSS_REPO"},
                {"from": "TIR.A", "to": "RFC.D", "authority": "CANONICAL_CROSS_REPO"},
                {"from": "SOH.X", "to": "RFC.C", "authority": "CANDIDATE_ONLY"},
            ],
        }
        self.claims = [
            {"claim_id": "TIR.A", "repository": "TIR", "source_path": "a.md"},
            {"claim_id": "IDT.B", "repository": "IDT", "source_path": "b.md"},
            {"claim_id": "RFC.C", "repository": "RFC", "source_path": "c.md"},
            {"claim_id": "RFC.D", "repository": "RFC", "source_path": "d.md"},
            {"claim_id": "SOH.X", "repository": "SOH", "source_path": "x.md"},
        ]

    def evidence(self, *observations):
        return {"schema": "FPDG_INCONSISTENCY_EVIDENCE_V0_1", "observations": list(observations)}

    def test_downstream_symptoms_collapse_to_earliest_observed_frontier(self):
        report = diagnose_mod.diagnose(
            self.graph,
            self.claims,
            self.evidence(
                {"observation_id": "o1", "kind": "STATUS_DRIFT", "claim_id": "IDT.B"},
                {"observation_id": "o2", "kind": "VALIDATOR_FAILURE", "claim_id": "RFC.C"},
            ),
        )
        self.assertEqual(report["localization_mode"], "EXACT")
        self.assertEqual(report["minimal_failing_frontier"], ["IDT.B"])
        zone = report["pain_zones"][0]
        self.assertIn(["IDT.B", "RFC.C"], zone["witness_paths"])
        self.assertTrue(any(edge["from"] == "TIR.A" for edge in zone["incoming_boundary_edges"]))

    def test_independent_failures_remain_two_frontiers(self):
        report = diagnose_mod.diagnose(
            self.graph,
            self.claims,
            self.evidence(
                {"observation_id": "o1", "kind": "STATUS_DRIFT", "claim_id": "IDT.B"},
                {"observation_id": "o2", "kind": "STATUS_DRIFT", "claim_id": "RFC.D"},
            ),
        )
        self.assertEqual(report["minimal_failing_frontier"], ["IDT.B", "RFC.D"])

    def test_candidate_edge_cannot_make_soh_an_upstream_failure(self):
        report = diagnose_mod.diagnose(
            self.graph,
            self.claims,
            self.evidence(
                {"observation_id": "o1", "kind": "STATUS_DRIFT", "claim_id": "SOH.X"},
                {"observation_id": "o2", "kind": "VALIDATOR_FAILURE", "claim_id": "RFC.C"},
            ),
        )
        self.assertEqual(report["minimal_failing_frontier"], ["RFC.C", "SOH.X"])
        self.assertFalse(report["candidate_edges_included"])

    def test_exact_source_path_maps_without_repository_fallback(self):
        report = diagnose_mod.diagnose(
            self.graph,
            self.claims,
            self.evidence(
                {
                    "observation_id": "o1",
                    "kind": "SOURCE_PATH_DRIFT",
                    "repository": "RFC",
                    "source_path": "c.md",
                }
            ),
        )
        self.assertEqual(report["observations"][0]["anchor_method"], "EXACT_SOURCE_PATH")
        self.assertEqual(report["minimal_failing_frontier"], ["RFC.C"])

    def test_gremlin_packet_never_fabricates_kaku_or_36d(self):
        report = diagnose_mod.diagnose(
            self.graph,
            self.claims,
            self.evidence(
                {"observation_id": "o1", "kind": "STATUS_DRIFT", "claim_id": "IDT.B"},
                {"observation_id": "o2", "kind": "VALIDATOR_FAILURE", "claim_id": "RFC.C"},
            ),
        )
        packet = gremlin_mod.build_packet(report)
        self.assertEqual(packet["promotion_state"], "CANDIDATE_ONLY")
        self.assertFalse(packet["runtime_execution_authority"])
        self.assertFalse(packet["canon_write_authority"])
        self.assertFalse(packet["vector_guessing_allowed"])
        self.assertEqual(
            packet["zones"][0]["compiler_state"],
            "BLOCKED_PENDING_GREMLIN_ALIGNMENT_AND_KAKU_RESOLUTION",
        )
        self.assertNotIn("Kaku", packet["zones"][0])


if __name__ == "__main__":
    unittest.main()
