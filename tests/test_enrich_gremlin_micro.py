import unittest

from tools.enrich_gremlin_pain_packet_with_micro import MicroPacketError, enrich


class GremlinMicroEnrichmentTests(unittest.TestCase):
    def packet(self):
        return {
            "schema": "FPDG_GREMLIN_PAIN_PACKET_V0_1",
            "epistemic": "CHYBA",
            "promotion_state": "CANDIDATE_ONLY",
            "runtime_execution_authority": False,
            "canon_write_authority": False,
            "vector_guessing_allowed": False,
            "candidate_edges_enter_canon": False,
            "zones": [
                {
                    "frontier_claim": "RFC.E20",
                    "raw_chains": [{"chain_id": "c", "claims": ["RFC.E20"]}],
                }
            ],
            "integration_zones": [],
        }

    def micro(self):
        return {
            "schema": "FPDG_PAIN_MICRO_COORDINATES_V0_1",
            "status": "LOCALIZED",
            "finest_precision": "SOURCE_RANGE",
            "causal_inference_performed": False,
            "candidate_edges_included": False,
            "coordinates": [
                {
                    "coordinate_id": "MICRO.o1",
                    "observation_id": "o1",
                    "precision": "SOURCE_RANGE",
                    "source_locator": {
                        "path": "closure/einstein/RF_E20.md",
                        "line_start": 412,
                        "line_end": 419,
                    },
                }
            ],
            "zones": [
                {
                    "frontier_claim": "RFC.E20",
                    "coordinate_ids": ["MICRO.o1"],
                    "finest_precision": "SOURCE_RANGE",
                }
            ],
            "integration_coordinates": [],
        }

    def test_exact_micro_coordinate_is_attached_to_claim_zone(self):
        packet = enrich(self.packet(), self.micro())
        zone = packet["zones"][0]
        self.assertEqual(zone["finest_micro_precision"], "SOURCE_RANGE")
        self.assertEqual(zone["micro_coordinates"][0]["source_locator"]["line_start"], 412)
        self.assertEqual(packet["source_micro_schema"], "FPDG_PAIN_MICRO_COORDINATES_V0_1")
        self.assertFalse(packet["runtime_execution_authority"])
        self.assertFalse(packet["canon_write_authority"])

    def test_missing_coordinate_reference_fails_closed(self):
        micro = self.micro()
        micro["zones"][0]["coordinate_ids"] = ["MICRO.missing"]
        with self.assertRaisesRegex(MicroPacketError, "missing coordinates"):
            enrich(self.packet(), micro)

    def test_causal_micro_input_is_rejected(self):
        micro = self.micro()
        micro["causal_inference_performed"] = True
        with self.assertRaisesRegex(MicroPacketError, "non-causal"):
            enrich(self.packet(), micro)


if __name__ == "__main__":
    unittest.main()
