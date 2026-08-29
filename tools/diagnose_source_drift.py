#!/usr/bin/env python3
"""Translate SOURCE_DRIFT_REPORT into exact FPDG pain localization + GREMLIN packet.

For drifted repositories this layer first compares the locked dependency export with the
export present at current main. If the scientific dependency surface is unchanged, the
pain is localized exactly to the integration freshness/lock layer instead of falsely
invalidating every scientific claim in the repository.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build"
DRIFT_PATH = BUILD_DIR / "SOURCE_DRIFT_REPORT.json"
CLAIMS_PATH = ROOT / "claims.jsonl"
LOCK_PATH = ROOT / "source_exports.lock.json"

sys.path.insert(0, str(ROOT / "tools"))
from build_gremlin_pain_packet import build_packet  # noqa: E402
from diagnose_inconsistency import diagnose, load_claims, load_graph, render_markdown  # noqa: E402
from diff_dependency_export import diff_exports, observations_from_diff, validate_export  # noqa: E402


class DriftDiagnosisError(RuntimeError):
    pass


def load_report(path: Path = DRIFT_PATH) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        report = json.load(fh)
    if not isinstance(report, dict) or report.get("schema") != "FPDG_SOURCE_DRIFT_REPORT_V0_1":
        raise DriftDiagnosisError("expected FPDG_SOURCE_DRIFT_REPORT_V0_1")
    return report


def github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "FPDG-pain-localizer/0.2",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_export(repository: str, path: str, ref: str) -> dict[str, Any]:
    quoted_path = urllib.parse.quote(path, safe="/")
    quoted_ref = urllib.parse.quote(ref, safe="")
    url = f"https://api.github.com/repos/{repository}/contents/{quoted_path}?ref={quoted_ref}"
    request = urllib.request.Request(url, headers=github_headers())
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict) or payload.get("encoding") != "base64":
        raise DriftDiagnosisError(f"{repository}@{ref}: dependency export content unavailable")
    content = payload.get("content")
    if not isinstance(content, str):
        raise DriftDiagnosisError(f"{repository}@{ref}: dependency export content missing")
    export = json.loads(base64.b64decode(content).decode("utf-8"))
    validate_export(export)
    return export


def claim_lookup(claims: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        row["claim_id"]: row
        for row in claims
        if isinstance(row.get("claim_id"), str)
    }


def path_fallback_observations(
    source: dict[str, Any], claims: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_claim = claim_lookup(claims)
    repo_id = source["repository_id"]
    repo = source["repository"]
    compare_ref = f"github-compare:{repo}@{source['locked_source_commit']}...{source['current_main']}"
    observations = []
    if source.get("fallback_all_owned"):
        return [
            {
                "observation_id": f"DRIFT.{repo_id}.REPOSITORY",
                "kind": "SOURCE_HEAD_DRIFT",
                "repository": repo_id,
                "expected": source["locked_source_commit"],
                "observed": source["current_main"],
                "evidence_refs": [compare_ref],
                "mapping_note": "semantic export diff unavailable; repository fallback required",
            }
        ]
    for index, claim_id in enumerate(source.get("changed_claims", []), 1):
        claim = by_claim.get(claim_id, {})
        row = {
            "observation_id": f"DRIFT.{repo_id}.{index:03d}.{claim_id}",
            "kind": "SOURCE_PATH_DRIFT",
            "repository": repo_id,
            "claim_id": claim_id,
            "expected": source["locked_source_commit"],
            "observed": source["current_main"],
            "evidence_refs": [compare_ref],
        }
        if isinstance(claim.get("source_path"), str):
            row["source_path"] = claim["source_path"]
        observations.append(row)
    return observations


def semantic_drift_evidence(
    report: dict[str, Any], claims: list[dict[str, Any]], lock: dict[str, Any]
) -> tuple[dict[str, Any] | None, list[dict[str, Any]], list[dict[str, Any]]]:
    if report.get("status") != "DRIFT":
        return None, [], []

    observations: list[dict[str, Any]] = []
    integration_points: list[dict[str, Any]] = []
    semantic_diffs: list[dict[str, Any]] = []

    for source in report.get("sources", []):
        if source.get("status") != "DRIFT":
            continue
        repo_id = source["repository_id"]
        entry = lock["sources"][repo_id]
        repository = source["repository"]
        export_path = entry.get("path", "DEPENDENCY_EXPORT.json")
        evidence_ref = (
            f"dependency-export-diff:{repository}@{entry['export_commit']}...{source['current_main']}"
        )
        try:
            old_export = fetch_export(repository, export_path, entry["export_commit"])
            new_export = fetch_export(repository, export_path, source["current_main"])
            semantic = diff_exports(old_export, new_export)
            semantic["locked_export_commit"] = entry["export_commit"]
            semantic["current_repository_head"] = source["current_main"]
            semantic_diffs.append(semantic)
            if semantic["surface_changed"]:
                observations.extend(observations_from_diff(semantic, evidence_ref))
            else:
                integration_points.append(
                    {
                        "location": f"FPDG.SOURCE_HEAD_LOCK.{repo_id}",
                        "kind": "REPOSITORY_HEAD_ADVANCED_WITH_IDENTICAL_DEPENDENCY_SURFACE",
                        "repository": repo_id,
                        "repository_full_name": repository,
                        "locked_repository_head": source["locked_source_commit"],
                        "current_repository_head": source["current_main"],
                        "represented_source_commit": new_export.get("source_commit"),
                        "locked_export_commit": entry["export_commit"],
                        "changed_paths": source.get("changed_paths", []),
                        "semantic_surface_changed": False,
                        "witness_locations": [
                            f"{repo_id}.main",
                            f"{repo_id}.{export_path}",
                            f"FPDG.source_exports.lock.json:{repo_id}",
                        ],
                        "evidence_refs": [evidence_ref],
                    }
                )
        except (OSError, KeyError, json.JSONDecodeError, DriftDiagnosisError, urllib.error.URLError) as exc:
            semantic_diffs.append(
                {
                    "schema": "FPDG_DEPENDENCY_EXPORT_SEMANTIC_DIFF_V0_1",
                    "repository_id": repo_id,
                    "status": "UNAVAILABLE",
                    "error": str(exc),
                }
            )
            observations.extend(path_fallback_observations(source, claims))

    evidence = None
    if observations:
        evidence = {
            "schema": "FPDG_INCONSISTENCY_EVIDENCE_V0_1",
            "incident_id": "SOURCE_DRIFT",
            "observations": observations,
        }
    return evidence, integration_points, semantic_diffs


def integration_only_diagnosis(points: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": "FPDG_INCONSISTENCY_DIAGNOSIS_V0_1",
        "status": "LOCALIZED",
        "localization_mode": "INTEGRATION_METADATA_EXACT",
        "candidate_edges_included": False,
        "observations": [],
        "observed_claim_anchors": [],
        "minimal_failing_frontier": [],
        "pain_zones": [],
        "integration_pain_points": points,
        "coarse_observation_ids": [],
        "unanchored_observation_ids": [],
        "gremlin_role": "CANDIDATE_PATTERN_MINING_ONLY",
    }


def render_full_markdown(diagnosis: dict[str, Any]) -> str:
    base = render_markdown(diagnosis).rstrip() + "\n"
    points = diagnosis.get("integration_pain_points", [])
    if not points:
        return base
    lines = [base, "", "## Exact integration pain points", ""]
    for point in points:
        lines.append(f"- `{point['location']}` — {point['kind']}")
        lines.append(f"  - repository: `{point['repository']}`")
        lines.append(f"  - dependency surface changed: `{point['semantic_surface_changed']}`")
        lines.append(
            f"  - head: `{point['locked_repository_head'][:12]}` -> `{point['current_repository_head'][:12]}`"
        )
        lines.append(
            "  - diagnosis: source-head freshness metadata is stale; no claim/local-edge drift was observed in the dependency export"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        report = load_report()
        if report.get("status") != "DRIFT":
            print("FRESH: no inconsistency diagnosis required")
            return 0
        claims = load_claims(CLAIMS_PATH)
        lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        evidence, integration_points, semantic_diffs = semantic_drift_evidence(report, claims, lock)

        if evidence:
            diagnosis = diagnose(load_graph(), claims, evidence)
            diagnosis["integration_pain_points"] = integration_points
            if integration_points and diagnosis["status"] == "LOCALIZED":
                diagnosis["localization_mode"] = "EXACT_MIXED_CLAIM_AND_INTEGRATION"
        elif integration_points:
            diagnosis = integration_only_diagnosis(integration_points)
        else:
            raise DriftDiagnosisError("drift exists but no diagnostic evidence could be produced")

        packet = build_packet(diagnosis)
        BUILD_DIR.mkdir(exist_ok=True)
        if evidence:
            (BUILD_DIR / "INCONSISTENCY_EVIDENCE.json").write_text(
                json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
            )
        (BUILD_DIR / "DEPENDENCY_EXPORT_SEMANTIC_DIFF.json").write_text(
            json.dumps(semantic_diffs, indent=2) + "\n", encoding="utf-8"
        )
        (BUILD_DIR / "INCONSISTENCY_DIAGNOSIS.json").write_text(
            json.dumps(diagnosis, indent=2) + "\n", encoding="utf-8"
        )
        (BUILD_DIR / "INCONSISTENCY_DIAGNOSIS.md").write_text(
            render_full_markdown(diagnosis), encoding="utf-8"
        )
        (BUILD_DIR / "GREMLIN_PAIN_PACKET.json").write_text(
            json.dumps(packet, indent=2) + "\n", encoding="utf-8"
        )

        if args.json:
            print(json.dumps(diagnosis, indent=2))
        else:
            print(
                f"{diagnosis['status']}: mode={diagnosis['localization_mode']} "
                f"claim_frontier={diagnosis['minimal_failing_frontier']} "
                f"integration_points={len(integration_points)}"
            )
        return 0 if diagnosis["status"] == "LOCALIZED" else 2
    except (
        OSError,
        json.JSONDecodeError,
        DriftDiagnosisError,
        KeyError,
        urllib.error.URLError,
    ) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
