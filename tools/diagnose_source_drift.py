#!/usr/bin/env python3
"""Translate SOURCE_DRIFT_REPORT into exact FPDG pain localization + GREMLIN packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build"
DRIFT_PATH = BUILD_DIR / "SOURCE_DRIFT_REPORT.json"
CLAIMS_PATH = ROOT / "claims.jsonl"

sys.path.insert(0, str(ROOT / "tools"))
from build_gremlin_pain_packet import build_packet  # noqa: E402
from diagnose_inconsistency import diagnose, load_claims, load_graph, render_markdown  # noqa: E402


class DriftDiagnosisError(RuntimeError):
    pass


def load_report(path: Path = DRIFT_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        report = json.load(fh)
    if not isinstance(report, dict) or report.get("schema") != "FPDG_SOURCE_DRIFT_REPORT_V0_1":
        raise DriftDiagnosisError("expected FPDG_SOURCE_DRIFT_REPORT_V0_1")
    return report


def claim_lookup(claims: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        row["claim_id"]: row
        for row in claims
        if isinstance(row.get("claim_id"), str)
    }


def report_to_evidence(
    report: dict[str, Any], claims: list[dict[str, Any]]
) -> dict[str, Any] | None:
    if report.get("status") != "DRIFT":
        return None

    by_claim = claim_lookup(claims)
    observations = []
    sequence = 0

    for source in report.get("sources", []):
        if source.get("status") != "DRIFT":
            continue
        repo_id = source["repository_id"]
        repo = source["repository"]
        compare_ref = (
            f"github-compare:{repo}@{source['locked_source_commit']}...{source['current_main']}"
        )

        if source.get("fallback_all_owned"):
            sequence += 1
            observations.append(
                {
                    "observation_id": f"DRIFT.{sequence:03d}.{repo_id}.REPOSITORY",
                    "kind": "SOURCE_HEAD_DRIFT",
                    "repository": repo_id,
                    "expected": source["locked_source_commit"],
                    "observed": source["current_main"],
                    "evidence_refs": [compare_ref],
                    "mapping_note": "changed paths did not map to known source_path; repository fallback required",
                }
            )
            continue

        for claim_id in source.get("changed_claims", []):
            sequence += 1
            claim = by_claim.get(claim_id, {})
            observation = {
                "observation_id": f"DRIFT.{sequence:03d}.{claim_id}",
                "kind": "SOURCE_PATH_DRIFT",
                "repository": repo_id,
                "claim_id": claim_id,
                "expected": source["locked_source_commit"],
                "observed": source["current_main"],
                "evidence_refs": [compare_ref],
            }
            if isinstance(claim.get("source_path"), str):
                observation["source_path"] = claim["source_path"]
            observations.append(observation)

    if not observations:
        raise DriftDiagnosisError("drift report contains no diagnosable drift observations")

    return {
        "schema": "FPDG_INCONSISTENCY_EVIDENCE_V0_1",
        "incident_id": "SOURCE_DRIFT",
        "observations": observations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        report = load_report()
        claims = load_claims(CLAIMS_PATH)
        evidence = report_to_evidence(report, claims)
        if evidence is None:
            print("FRESH: no inconsistency diagnosis required")
            return 0

        graph = load_graph()
        diagnosis = diagnose(graph, claims, evidence)
        packet = build_packet(diagnosis)

        BUILD_DIR.mkdir(exist_ok=True)
        (BUILD_DIR / "INCONSISTENCY_EVIDENCE.json").write_text(
            json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
        )
        (BUILD_DIR / "INCONSISTENCY_DIAGNOSIS.json").write_text(
            json.dumps(diagnosis, indent=2) + "\n", encoding="utf-8"
        )
        (BUILD_DIR / "INCONSISTENCY_DIAGNOSIS.md").write_text(
            render_markdown(diagnosis), encoding="utf-8"
        )
        (BUILD_DIR / "GREMLIN_PAIN_PACKET.json").write_text(
            json.dumps(packet, indent=2) + "\n", encoding="utf-8"
        )

        if args.json:
            print(json.dumps(diagnosis, indent=2))
        else:
            print(
                f"{diagnosis['status']}: frontier={diagnosis['minimal_failing_frontier']} "
                f"gremlin_zones={len(packet['zones'])}"
            )
        return 0 if diagnosis["status"] == "LOCALIZED" else 2
    except (OSError, json.JSONDecodeError, DriftDiagnosisError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
