#!/usr/bin/env python3
"""Audit direct source-validator claim coverage for the FPDG graph.

This is an observability audit, not a scientific validation score. A mapped claim means
that a registered source-side producer can attach a failing test to that exact FPDG
claim. Unmapped claims remain diagnosable through broader graph/source evidence, but do
not yet have a registered direct test-to-claim nerve ending in this registry.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "dependency_graph.yaml"
REGISTRY_PATH = ROOT / "diagnostics" / "VALIDATION_PRODUCERS_V0_1.yaml"
BUILD_DIR = ROOT / "build"
PROMOTED = {"CANONICAL", "CANONICAL_CROSS_REPO", "CANONICAL_FRONTIER"}


class CoverageError(RuntimeError):
    pass


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    if not isinstance(value, dict):
        raise CoverageError(f"{path}: expected mapping")
    return value


def cross_repo_boundary_claims(graph: dict[str, Any]) -> set[str]:
    nodes = {row["claim_id"]: row for row in graph.get("nodes", [])}
    out = set()
    for edge in graph.get("edges", []):
        if edge.get("authority") != "CANONICAL_CROSS_REPO":
            continue
        src = edge.get("from")
        dst = edge.get("to")
        if src in nodes and dst in nodes:
            out.update((src, dst))
    return out


def frontier_claims(graph: dict[str, Any]) -> set[str]:
    out = set()
    for edge in graph.get("edges", []):
        if edge.get("authority") == "CANONICAL_FRONTIER":
            if isinstance(edge.get("from"), str):
                out.add(edge["from"])
            if isinstance(edge.get("to"), str):
                out.add(edge["to"])
    return out


def audit(graph: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    if registry.get("schema") != "FPDG_VALIDATION_PRODUCER_REGISTRY_V0_1":
        raise CoverageError("unsupported validation producer registry schema")
    producers = registry.get("producers")
    if not isinstance(producers, dict):
        raise CoverageError("producer registry requires producers mapping")

    nodes = graph.get("nodes")
    if not isinstance(nodes, list):
        raise CoverageError("dependency graph requires nodes list")
    node_by_id = {}
    owned: defaultdict[str, list[str]] = defaultdict(list)
    for row in nodes:
        if not isinstance(row, dict):
            raise CoverageError("graph node must be an object")
        claim_id = row.get("claim_id")
        repo = row.get("repository")
        if not isinstance(claim_id, str) or not isinstance(repo, str):
            raise CoverageError("graph nodes require claim_id and repository")
        if claim_id in node_by_id:
            raise CoverageError(f"duplicate graph claim {claim_id}")
        node_by_id[claim_id] = row
        owned[repo].append(claim_id)

    boundary = cross_repo_boundary_claims(graph)
    frontier = frontier_claims(graph)
    problems = []
    repo_reports = []

    for repo_id in sorted(producers):
        producer = producers[repo_id]
        if not isinstance(producer, dict):
            problems.append(f"{repo_id}: producer entry must be mapping")
            continue
        mapped = producer.get("mapped_claims", [])
        if not isinstance(mapped, list) or any(not isinstance(value, str) for value in mapped):
            problems.append(f"{repo_id}: mapped_claims must be string list")
            continue
        if len(mapped) != len(set(mapped)):
            problems.append(f"{repo_id}: duplicate mapped_claims")
        for claim_id in mapped:
            node = node_by_id.get(claim_id)
            if node is None:
                problems.append(f"{repo_id}: mapped unknown claim {claim_id}")
            elif node.get("repository") != repo_id:
                problems.append(
                    f"{repo_id}: mapped claim {claim_id} belongs to {node.get('repository')}"
                )

        all_owned = sorted(owned.get(repo_id, []))
        mapped_set = set(mapped) & set(all_owned)
        unmapped = sorted(set(all_owned) - mapped_set)
        priority_rows = []
        for claim_id in unmapped:
            node = node_by_id[claim_id]
            reasons = []
            priority = 3
            if claim_id in boundary:
                reasons.append("PROMOTED_CROSS_REPO_BOUNDARY")
                priority = min(priority, 0)
            if claim_id in frontier:
                reasons.append("CANONICAL_FRONTIER_INCIDENT")
                priority = min(priority, 1)
            status = str(node.get("status", ""))
            if "OPEN" in status or "FRONTIER" in status or "ACTIVE" in status:
                reasons.append("ACTIVE_OR_OPEN_STATUS")
                priority = min(priority, 2)
            if reasons:
                priority_rows.append(
                    {
                        "claim_id": claim_id,
                        "status": node.get("status"),
                        "priority": priority,
                        "reasons": reasons,
                    }
                )
        priority_rows.sort(key=lambda row: (row["priority"], row["claim_id"]))
        total = len(all_owned)
        repo_reports.append(
            {
                "repository_id": repo_id,
                "producer_status": producer.get("status", "REGISTERED"),
                "graph_claim_count": total,
                "directly_mapped_claim_count": len(mapped_set),
                "direct_binding_coverage_fraction": (len(mapped_set) / total) if total else 0.0,
                "mapped_claims": sorted(mapped_set),
                "unmapped_claims": unmapped,
                "priority_blind_spots": priority_rows,
            }
        )

    total_claims = sum(row["graph_claim_count"] for row in repo_reports)
    total_mapped = sum(row["directly_mapped_claim_count"] for row in repo_reports)
    return {
        "schema": "FPDG_VALIDATION_COVERAGE_REPORT_V0_1",
        "status": "PASS" if not problems else "REGISTRY_INVALID",
        "semantics": "DIRECT_TEST_TO_CLAIM_OBSERVABILITY_COVERAGE",
        "scientific_validation_score": False,
        "graph_claim_count": total_claims,
        "directly_mapped_claim_count": total_mapped,
        "direct_binding_coverage_fraction": (total_mapped / total_claims) if total_claims else 0.0,
        "repositories": repo_reports,
        "problems": problems,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = ["# FPDG Validation Nerve Coverage", "", f"Status: **{report['status']}**", ""]
    lines.append(
        f"Direct test-to-claim observability: **{report['directly_mapped_claim_count']} / {report['graph_claim_count']}** "
        f"({100.0 * report['direct_binding_coverage_fraction']:.1f}%)"
    )
    lines.extend(["", "This percentage is an instrumentation coverage metric, not a scientific validation score.", ""])
    for repo in report["repositories"]:
        lines.append(
            f"- **{repo['repository_id']}** — {repo['directly_mapped_claim_count']} / {repo['graph_claim_count']} direct claim bindings"
        )
        for row in repo["priority_blind_spots"][:12]:
            lines.append(
                f"  - priority {row['priority']}: `{row['claim_id']}` — {', '.join(row['reasons'])}"
            )
    if report["problems"]:
        lines.extend(["", "Registry problems:"])
        for problem in report["problems"]:
            lines.append(f"- {problem}")
    return "\n".join(lines) + "\n"


def main() -> int:
    try:
        report = audit(load_yaml(GRAPH_PATH), load_yaml(REGISTRY_PATH))
        BUILD_DIR.mkdir(exist_ok=True)
        (BUILD_DIR / "VALIDATION_COVERAGE_REPORT.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        (BUILD_DIR / "VALIDATION_COVERAGE_REPORT.md").write_text(
            render_markdown(report), encoding="utf-8"
        )
        print(json.dumps(report, indent=2))
        return 0 if report["status"] == "PASS" else 2
    except (OSError, yaml.YAMLError, CoverageError, KeyError, TypeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
