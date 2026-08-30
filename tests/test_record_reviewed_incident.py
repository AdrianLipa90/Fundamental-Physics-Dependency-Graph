import json
import tempfile
import unittest
from pathlib import Path

from tools.build_pain_signature import build_signature
from tools.match_pain_signatures import load_signature
from tools.record_reviewed_incident import IncidentRecordError, record_incident


class ReviewedIncidentTests(unittest.TestCase):
    def signature(self):
        diagnosis = {
            "schema": "FPDG_INCONSISTENCY_DIAGNOSIS_V0_1",
            "localization_mode": "EXACT",
            "pain_zones": [
                {
                    "frontier_claim": "IDT.B",
                    "status": "PASS",
                    "symptom_anchors": ["IDT.B"],
                    "witness_paths": [["IDT.B"]],
                    "downstream_revalidation_count": 2,
                }
            ],
            "integration_pain_points": [],
        }
        seams = {
            "schema": "FPDG_PAIN_SEAM_REPORT_V0_1",
            "zones": [
                {
                    "frontier_claim": "IDT.B",
                    "claim_status": "PASS",
                    "seams": [],
                }
            ],
            "integration_targets": [],
        }
        return build_signature(diagnosis, seams)

    def packet(self):
        return {
            "schema": "FPDG_GREMLIN_PAIN_PACKET_V0_1",
            "epistemic": "CHYBA",
            "promotion_state": "CANDIDATE_ONLY",
            "runtime_execution_authority": False,
            "canon_write_authority": False,
            "vector_guessing_allowed": False,
            "candidate_edges_enter_canon": False,
            "zones": [],
            "integration_zones": [],
        }

    def test_records_signature_and_packet_append_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            incidents = root / "incidents"
            packets = incidents / "packets"
            sig_path, packet_path = record_incident(
                self.signature(),
                self.packet(),
                incident_id="INC-001",
                reviewed_by="reviewer",
                evidence_refs=["receipt:abc"],
                incident_dir=incidents,
                packet_dir=packets,
            )
            self.assertTrue(sig_path.exists())
            self.assertTrue(packet_path.exists())
            loaded = load_signature(sig_path)
            self.assertEqual(loaded["incident_review"]["incident_id"], "INC-001")
            stored_packet = json.loads(packet_path.read_text(encoding="utf-8"))
            self.assertEqual(stored_packet["incident_review"]["incident_id"], "INC-001")
            with self.assertRaises(IncidentRecordError):
                record_incident(
                    self.signature(),
                    self.packet(),
                    incident_id="INC-001",
                    reviewed_by="reviewer",
                    evidence_refs=[],
                    incident_dir=incidents,
                    packet_dir=packets,
                )

    def test_unsafe_packet_is_rejected(self):
        packet = self.packet()
        packet["canon_write_authority"] = True
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaises(IncidentRecordError):
                record_incident(
                    self.signature(),
                    packet,
                    incident_id="INC-UNSAFE",
                    reviewed_by="reviewer",
                    evidence_refs=[],
                    incident_dir=root / "incidents",
                    packet_dir=root / "incidents" / "packets",
                )


if __name__ == "__main__":
    unittest.main()
