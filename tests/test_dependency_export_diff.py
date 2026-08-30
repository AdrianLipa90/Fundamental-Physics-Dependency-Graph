import unittest

from tools.diff_dependency_export import diff_exports, observations_from_diff


class DependencyExportDiffTests(unittest.TestCase):
    def export(self, claims, edges=None, source_commit="a" * 40, generated_at="t0"):
        return {
            "schema": "FPDG_DEPENDENCY_EXPORT_V0_1",
            "repository_id": "RFC",
            "repository": "owner/rfc",
            "source_commit": source_commit,
            "generated_at": generated_at,
            "claims": claims,
            "local_edges": edges or [],
        }

    def test_provenance_only_change_is_not_scientific_surface_drift(self):
        claim = {"claim_id": "RFC.A", "status": "PASS", "source_path": "a.md"}
        old = self.export([claim], source_commit="a" * 40, generated_at="t0")
        new = self.export([claim], source_commit="b" * 40, generated_at="t1")
        diff = diff_exports(old, new)
        self.assertFalse(diff["surface_changed"])
        self.assertIn("source_commit", diff["provenance_changes"])
        self.assertIn("generated_at", diff["provenance_changes"])

    def test_status_change_localizes_exact_claim(self):
        old = self.export([{"claim_id": "RFC.A", "status": "PASS", "source_path": "a.md"}])
        new = self.export([{"claim_id": "RFC.A", "status": "OPEN", "source_path": "a.md"}])
        diff = diff_exports(old, new)
        self.assertTrue(diff["surface_changed"])
        self.assertEqual(diff["claims_changed"][0]["claim_id"], "RFC.A")
        observations = observations_from_diff(diff, "receipt:test")
        self.assertEqual(observations[0]["kind"], "STATUS_DRIFT")
        self.assertEqual(observations[0]["claim_id"], "RFC.A")

    def test_edge_change_localizes_exact_endpoints(self):
        claims = [
            {"claim_id": "RFC.A", "status": "PASS", "source_path": "a.md"},
            {"claim_id": "RFC.B", "status": "PASS", "source_path": "b.md"},
        ]
        old = self.export(claims, [])
        new = self.export(claims, [{"from": "RFC.A", "to": "RFC.B", "authority": "CANONICAL"}])
        diff = diff_exports(old, new)
        self.assertTrue(diff["surface_changed"])
        observations = observations_from_diff(diff, "receipt:test")
        self.assertEqual(observations[0]["kind"], "EXTRA_EDGE")
        self.assertEqual(observations[0]["edge"]["from"], "RFC.A")
        self.assertEqual(observations[0]["edge"]["to"], "RFC.B")


if __name__ == "__main__":
    unittest.main()
