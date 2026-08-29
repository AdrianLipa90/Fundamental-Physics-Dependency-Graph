#!/usr/bin/env python3
"""Reconcile source-repository DEPENDENCY_EXPORT.json files with the canonical FPDG graph.

The source repositories remain authoritative for local claim state and local dependency
edges. This tool validates source exports, then checks that the canonical meta-graph
contains the same local surfaces while preserving cross-repository edges as FPDG-owned
integration contracts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "dependency_graph.yaml"
REGISTRY_PATH = ROOT / "repos.yaml"

HEX40 = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_LOCAL_AUTHORITIES = {"CANONICAL", "CANONICAL_FRONTIER", "CANDIDATE_ONLY"}


class ExportError(RuntimeError):
    pass


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    if not isinstance(value, dict):
        raise ExportError(f"{path}: expected a mapping")
    return value


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise ExportError(f"{path}: expected a JSON object")
    return value


def repo_registry() -> dict[str, dict[str, Any]]:
    registry = load_yaml(REGISTRY_PATH)
    repos = registry.get("repositories")
    if not isinstance(repos, dict):
        raise ExportError("repos.yaml: repositories must be a mapping")
    return repos


def validate_export(export: dict[str, Any], path: Path, registry: dict[str, dict[str, Any]]) -> None:
    if export.get("schema") != "FPDG_DEPENDENCY_EXPORT_V0_1":
        raise ExportError(f"{path}: unsupported schema {export.get('schema')!r}")

    repo_id = export.get("repository_id")
    if repo_id not in registry:
        raise ExportError(f"{path}: unknown repository_id {repo_id!r}")

    expected_repo = registry[repo_id].get("repository")
    if export.get("repository") != expected_repo:
        raise ExportError(
            f"{path}: repository mismatch: {export.get('repository')!r} != {expected_repo!r}"
        )

    source_commit = export.get("source_commit")
    if not isinstance(source_commit, str) or not HEX40.fullmatch(source_commit):
        raise ExportError(f"{path}: source_commit must be a 40-character lowercase hex SHA")

    claims = export.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ExportError(f"{path}: claims must be a non-empty list")

    claim_ids: list[str] = []
    for idx, claim in enumerate(claims, 1):
        if not isinstance(claim, dict):
            raise ExportError(f"{path}: claim {idx} must be an object")
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id.startswith(repo_id + "."):
            raise ExportError(f"{path}: claim {idx} has invalid repository prefix: {claim_id!r}")
        for key in ("status", "source_path", "evidence_class"):
            if not isinstance(claim.get(key), str) or not claim[key]:
                raise ExportError(f"{path}: claim {claim_id} missing {key}")
        exact_head = claim.get("exact_head")
        if exact_head is not None and (not isinstance(exact_head, str) or not HEX40.fullmatch(exact_head)):
            raise ExportError(f"{path}: claim {claim_id} has invalid exact_head")
        claim_ids.append(claim_id)

    if len(claim_ids) != len(set(claim_ids)):
        raise ExportError(f"{path}: duplicate claim_id")

    claim_set = set(claim_ids)
    local_edges = export.get("local_edges", [])
    if not isinstance(local_edges, list):
        raise ExportError(f"{path}: local_edges must be a list")

    seen_edges: set[tuple[str, str, str]] = set()
    for idx, edge in enumerate(local_edges, 1):
        if not isinstance(edge, dict):
            raise ExportError(f"{path}: local edge {idx} must be an object")
        src, dst, authority = edge.get("from"), edge.get("to"), edge.get("authority")
        if src not in claim_set or dst not in claim_set:
            raise ExportError(f"{path}: local edge {idx} escapes exported claim set: {src} -> {dst}")
        if authority not in ALLOWED_LOCAL_AUTHORITIES:
            raise ExportError(f"{path}: local edge {idx} has invalid authority {authority!r}")
        if src == dst:
            raise ExportError(f"{path}: local edge {idx} is a self-edge")
        key = (src, dst, authority)
        if key in seen_edges:
            raise ExportError(f"{path}: duplicate local edge {src} -> {dst} [{authority}]")
        seen_edges.add(key)
        if authority == "CANDIDATE_ONLY":
            if edge.get("promotion_required") is not True or not edge.get("promotion_gate"):
                raise ExportError(f"{path}: candidate local edge {idx} lacks promotion gate")


def canonical_local_surface(graph: dict[str, Any], repo_id: str) -> tuple[dict[str, dict[str, Any]], set[tuple[str, str, str]]]:
    nodes = {
        node["claim_id"]: node
        for node in graph.get("nodes", [])
        if node.get("repository") == repo_id
    }
    node_ids = set(nodes)
    edges = {
        (edge["from"], edge["to"], edge["authority"])
        for edge in graph.get("edges", [])
        if edge.get("from") in node_ids and edge.get("to") in node_ids
    }
    return nodes, edges


def export_surface(export: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], set[tuple[str, str, str]]]:
    claims = {claim["claim_id"]: claim for claim in export["claims"]}
    edges = {
        (edge["from"], edge["to"], edge["authority"])
        for edge in export.get("local_edges", [])
    }
    return claims, edges


def reconcile(graph: dict[str, Any], export: dict[str, Any]) -> list[str]:
    repo_id = export["repository_id"]
    canonical_nodes, canonical_edges = canonical_local_surface(graph, repo_id)
    exported_claims, exported_edges = export_surface(export)

    problems: list[str] = []
    canonical_ids = set(canonical_nodes)
    exported_ids = set(exported_claims)

    missing_export = sorted(canonical_ids - exported_ids)
    extra_export = sorted(exported_ids - canonical_ids)
    if missing_export:
        problems.append(f"{repo_id}: canonical claims missing from export: {missing_export}")
    if extra_export:
        problems.append(f"{repo_id}: export claims absent from canonical graph: {extra_export}")

    for claim_id in sorted(canonical_ids & exported_ids):
        canonical = canonical_nodes[claim_id]
        exported = exported_claims[claim_id]
        if canonical.get("status") != exported.get("status"):
            problems.append(
                f"{repo_id}: status drift {claim_id}: canonical={canonical.get('status')} export={exported.get('status')}"
            )

    missing_edges = sorted(canonical_edges - exported_edges)
    extra_edges = sorted(exported_edges - canonical_edges)
    if missing_edges:
        problems.append(f"{repo_id}: canonical local edges missing from export: {missing_edges}")
    if extra_edges:
        problems.append(f"{repo_id}: export local edges absent from canonical graph: {extra_edges}")

    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exports", nargs="+", type=Path, help="DEPENDENCY_EXPORT.json files")
    parser.add_argument(
        "--require-all",
        action="store_true",
        help="require exactly one export for every repository in repos.yaml",
    )
    parser.add_argument(
        "--summary-json",
        action="store_true",
        help="emit a machine-readable reconciliation summary",
    )
    args = parser.parse_args()

    try:
        registry = repo_registry()
        graph = load_yaml(GRAPH_PATH)
        exports: list[dict[str, Any]] = []
        seen_repos: set[str] = set()

        for path in args.exports:
            export = load_json(path)
            validate_export(export, path, registry)
            repo_id = export["repository_id"]
            if repo_id in seen_repos:
                raise ExportError(f"duplicate export for {repo_id}")
            seen_repos.add(repo_id)
            exports.append(export)

        if args.require_all and seen_repos != set(registry):
            missing = sorted(set(registry) - seen_repos)
            extra = sorted(seen_repos - set(registry))
            raise ExportError(f"repository export set mismatch: missing={missing}, extra={extra}")

        problems: list[str] = []
        summaries: list[dict[str, Any]] = []
        for export in exports:
            repo_id = export["repository_id"]
            repo_problems = reconcile(graph, export)
            problems.extend(repo_problems)
            summaries.append(
                {
                    "repository_id": repo_id,
                    "source_commit": export["source_commit"],
                    "claims": len(export["claims"]),
                    "local_edges": len(export.get("local_edges", [])),
                    "status": "PASS" if not repo_problems else "DRIFT",
                }
            )

        if args.summary_json:
            print(json.dumps({"schema": "FPDG_EXPORT_RECONCILIATION_V0_1", "exports": summaries, "problems": problems}, indent=2))
        else:
            for item in summaries:
                print(
                    f"{item['repository_id']}: {item['status']} "
                    f"claims={item['claims']} local_edges={item['local_edges']} "
                    f"source_commit={item['source_commit']}"
                )
            for problem in problems:
                print(f"DRIFT: {problem}", file=sys.stderr)

        if problems:
            return 2
        print("PASS: source exports reconcile exactly with canonical local graph surfaces")
        return 0
    except (OSError, json.JSONDecodeError, yaml.YAMLError, ExportError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
