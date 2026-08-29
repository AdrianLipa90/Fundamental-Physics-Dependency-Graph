import unittest

from tools.diagnose_inconsistency import diagnose, load_claims, load_graph
from tools.localize_interface_evidence import (
    InterfaceEvidenceError,
    claim_projection_evidence,
    enrich_interface_diagnosis,
)
from tools.localize_micro_coordinates import localize as localize_micro


class InterfaceEvidenceTests(unittest.TestCase):
    def evidence(self, interface_id="IFACE.IDT_TO_RFC.NOETHER_SOURCE"):
        return {
            "schema": "FPDG_INCONSISTENCY_EVIDENCE_V0_1",
            "incident_id": "IFACE_TEST",
            "observations": [
                {
                    "observation_id": "IFACE.001",
                    "kind": "CROSS_REPO_CONTRACT_FAILURE",
                    "repository": "IDT",
                    "source_path": "tests/reference/test_01AA_noether_rfc_conserved_current_binding.py",
                    "source_locator": {
                        "path": "tests/reference/test_01AA_noether_rfc_conserved_current_binding.py",
                        "test_id": "test_01aa_conserved_current",
                        "interface_id": interface_id,
                    },
                    "evidence_refs": ["pytest:test_01aa_conserved_current"],
                }
            ],
        }

    def test_interface_only_observation_does_not_trigger_repository_claim_fallback(self):
        evidence = self.evidence()
        claim_evidence = claim_projection_evidence(evidence)
        self.assertEqual(claim_evidence["observations"], [])
        base = diagnose(load_graph(), load_claims(), claim_evidence)
        self.assertEqual(base["status"], "UNLOCALIZED")
        self.assertEqual(base["minimal_failing_frontier"], [])

        result = enrich_interface_diagnosis(base, evidence)
        self.assertEqual(result["status"], "LOCALIZED")
        self.assertEqual(result["localization_mode"], "EXACT_INTERFACE_CONTRACT")
        self.assertEqual(result["minimal_failing_frontier"], [])
        point = result["integration_pain_points"][0]
        self.assertEqual(point["interface_id"], "IFACE.IDT_TO_RFC.NOETHER_SOURCE")
        self.assertEqual(point["upstream_claim"], "IDT.NOETHER.GAUGE_COVARIANT_SOURCE")
        self.assertEqual(point["downstream_claim"], "RFC.SOURCE.CONSERVED_CARRIER")
        self.assertFalse(point["causal_endpoint_projection_performed"])

    def test_micro_localizer_keeps_interface_contract_and_test_coordinate(self):
        evidence = self.evidence()
        diagnosis = enrich_interface_diagnosis(
            diagnose(load_graph(), load_claims(), claim_projection_evidence(evidence)),
            evidence,
        )
        micro = localize_micro(diagnosis, evidence)
        self.assertEqual(micro["status"], "LOCALIZED")
        coordinate = micro["coordinates"][0]
        self.assertEqual(coordinate["precision"], "INTERFACE_CONTRACT")
        self.assertEqual(
            coordinate["source_locator"]["interface_id"],
            "IFACE.IDT_TO_RFC.NOETHER_SOURCE",
        )
        self.assertFalse(micro["causal_inference_performed"])

    def test_unknown_interface_fails_closed(self):
        evidence = self.evidence("IFACE.DOES_NOT.EXIST")
        with self.assertRaises(InterfaceEvidenceError):
            enrich_interface_diagnosis(
                diagnose(load_graph(), load_claims(), claim_projection_evidence(evidence)),
                evidence,
            )


if __name__ == "__main__":
    unittest.main()
