#!/usr/bin/env python3
"""Reconcile source DEPENDENCY_EXPORT.json files with the effective FPDG graph."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from federation_surface import (  # noqa: E402
    BASE_GRAPH_PATH,
    FederationSurfaceError,
    load_effective_graph,
    repository_registry,
)

GRAPH_PATH = BASE_GRAPH_PATH
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
    try:
        return repository_registry()
    except FederationSurfaceError as exc:
        raise ExportError(str(exc)) from exc


def validate_export(export: dict[str, Any], path: Path, registry: dict[str, dict[str, Any]]) -> None:
    if export.get("schema") != "FPDG_DEPENDENCY_EXPORT_V0_1":
        raise ExportError(f"{path}: unsupported schema {export.get('schema')!r}")
    repo_id = export.get("repository_id")
    if repo_id not in registry:
        raise ExportError(f"{path}: unknown repository_id {repo_id!r}")
    expected_repo = registry[repo_id].get("repository")
    if export.get("repository") != expected_repo:
        raise ExportError(f"{path}: repository mismatch")
    source_commit = export.get("source_commit")
    if not isinstance(source_commit, str) or not HEX40.fullmatch(source_commit):
        raise ExportError(f"{path}: source_commit must be a 40-character lowercase hex SHA")

    claims = export.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ExportError(f"{path}: claims must be a non-empty list")
    claim_ids = []
    for idx, claim in enumerate(claims, 1):
        if not isinstance(claim, dict):
            raise ExportError(f"{path}: claim {idx} must be an object")
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id.startswith(repo_id + "."):
            raise ExportError(f"{path}: claim {idx} has invalid repository prefix")
        for key in ("status", "source_path", "evidence_class"):
            if not isinstance(claim.get(key), str) or not claim[key]:
                raise ExportError(f"{path}: claim {claim_id} missing {key}")
        exact_head = claim.get("exact_head")
        if exact_head is not None and (
            not isinstance(exact_head, str) or not HEX40.fullmatch(exact_head)
        ):
            raise ExportError(f"{path}: claim {claim_id} has invalid exact_head")
        claim_ids.append(claim_id)
    if len(claim_ids) != len(set(claim_ids)):
        raise ExportError(f"{path}: duplicate claim_id")

    claim_set = set(claim_ids)
    local_edges = export.get("local_edges", [])
    if not isinstance(local_edges, list):
        raise ExportError(f"{path}: local_edges must be a list")
    seen_edges = set()
    for idx, edge in enumerate(local_edges, 1):
        if not isinstance(edge, dict):
            raise ExportError(f"{path}: local edge {idx} must be an object")
        src, dst, authority = edge.get("from"), edge.get("to"), edge.get("authority")
        if src not in claim_set or dst not in claim_set:
            raise ExportError(f"{path}: local edge {idx} escapes exported claim set")
        if authority not in ALLOWED_LOCAL_AUTHORITIES:
            raise ExportError(f"{path}: local edge {idx} has invalid authority")
        if src == dst:
            raise ExportError(f"{path}: local edge {idx} is a self-edge")
        key = (src, dst, authority)
        if key in seen_edges:
            raise ExportError(f"{path}: duplicate local edge")
        seen_edges.add(key)
        if authority == "CANDIDATE_ONLY":
            if edge.get("promotion_required") is not True or not edge.get("promotion_gate"):
                raise ExportError(f"{path}: candidate local edge {idx} lacks promotion gate")


def canonical_local_surface(graph, repo_id):
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


def export_surface(export):
    claims = {claim["claim_id"]: claim for claim in export["claims"]}
    edges = {
        (edge["from"], edge["to"], edge["authority"])
        for edge in export.get("local_edges", [])
    }
    return claims, edges


def reconcile(graph, export):
    repo_id = export["repository_id"]
    canonical_nodes, canonical_edges = canonical_local_surface(graph, repo_id)
    exported_claims, exported_edges = export_surface(export)
    problems = []
    canonical_ids = set(canonical_nodes)
    exported_ids = set(exported_claims)
    if canonical_ids - exported_ids:
        problems.append(
            f"{repo_id}: canonical claims missing from export: {sorted(canonical_ids - exported_ids)}"
        )
    if exported_ids - canonical_ids:
        problems.append(
            f"{repo_id}: export claims absent from effective graph: {sorted(exported_ids - canonical_ids)}"
        )
    for claim_id in sorted(canonical_ids & exported_ids):
        if canonical_nodes[claim_id].get("status") != exported_claims[claim_id].get("status"):
            problems.append(
                f"{repo_id}: status drift {claim_id}: "
                f"canonical={canonical_nodes[claim_id].get('status')} "
                f"export={exported_claims[claim_id].get('status')}"
            )
    if canonical_edges - exported_edges:
        problems.append(
            f"{repo_id}: canonical local edges missing from export: "
            f"{sorted(canonical_edges - exported_edges)}"
        )
    if exported_edges - canonical_edges:
        problems.append(
            f"{repo_id}: export local edges absent from effective graph: "
            f"{sorted(exported_edges - canonical_edges)}"
        )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exports", nargs="+", type=Path)
    parser.add_argument("--require-all", action="store_true")
    parser.add_argument("--summary-json", action="store_true")
    args = parser.parse_args()
    try:
        registry = repo_registry()
        graph = load_effective_graph()
        exports = []
        seen_repos = set()
        for path in args.exports:
            export = load_json(path)
            validate_export(export, path, registry)
            repo_id = export["repository_id"]
            if repo_id in seen_repos:
                raise ExportError(f"duplicate export for {repo_id}")
            seen_repos.add(repo_id)
            exports.append(export)

        if args.require_all and seen_repos != set(registry):
            raise ExportError(
                f"repository export set mismatch: "
                f"missing={sorted(set(registry) - seen_repos)}, "
                f"extra={sorted(seen_repos - set(registry))}"
            )

        problems = []
        summaries = []
        for export in exports:
            repo_id = export["repository_id"]
            repo_problems = reconcile(graph, export)
            problems.extend(repo_problems)
            summaries.append({
                "repository_id": repo_id,
                "source_commit": export["source_commit"],
                "claims": len(export["claims"]),
                "local_edges": len(export.get("local_edges", [])),
                "status": "PASS" if not repo_problems else "DRIFT",
            })
        if args.summary_json:
            print(json.dumps({
                "schema": "FPDG_EXPORT_RECONCILIATION_V0_2",
                "repositories_expected": sorted(registry),
                "effective_overlays": graph.get("effective_federation_overlays", []),
                "exports": summaries,
                "problems": problems,
            }, indent=2))
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
        print("PASS: all registered source exports reconcile with the effective graph")
        return 0
    except (
        OSError,
        json.JSONDecodeError,
        yaml.YAMLError,
        ExportError,
        FederationSurfaceError,
    ) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
