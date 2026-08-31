#!/usr/bin/env python3
"""Load the effective FPDG federation surface.

The base graph/claim/interface registries remain stable files. Canonical federation
extensions live under ``federation_overlays`` and are merged deterministically in
lexicographic filename order. This keeps source-owned additions reviewable without
rewriting the large base registries.
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE_GRAPH_PATH = ROOT / "dependency_graph.yaml"
BASE_CLAIMS_PATH = ROOT / "claims.jsonl"
BASE_INTERFACES_PATH = ROOT / "interfaces" / "cross_repo_interfaces.yaml"
REPOS_PATH = ROOT / "repos.yaml"
OVERLAY_DIR = ROOT / "federation_overlays"

GRAPH_OVERLAY_GLOB = "*.graph.yaml"
CLAIMS_OVERLAY_GLOB = "*.claims.jsonl"
INTERFACE_OVERLAY_GLOB = "*.interfaces.yaml"


class FederationSurfaceError(RuntimeError):
    pass


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    if not isinstance(value, dict):
        raise FederationSurfaceError(f"{path}: expected mapping")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise FederationSurfaceError(f"{path}:{line_no}: {exc}") from exc
            if not isinstance(row, dict):
                raise FederationSurfaceError(f"{path}:{line_no}: expected object")
            rows.append(row)
    return rows


def repository_registry() -> dict[str, dict[str, Any]]:
    payload = load_yaml_mapping(REPOS_PATH)
    repos = payload.get("repositories")
    if not isinstance(repos, dict) or not repos:
        raise FederationSurfaceError("repos.yaml: repositories must be a non-empty mapping")
    return repos


def repository_ids() -> tuple[str, ...]:
    return tuple(sorted(repository_registry()))


def load_effective_graph(path: Path | str = BASE_GRAPH_PATH) -> dict[str, Any]:
    path = Path(path)
    graph = deepcopy(load_yaml_mapping(path))
    if path.resolve() != BASE_GRAPH_PATH.resolve():
        return graph

    applied: list[str] = []
    if OVERLAY_DIR.exists():
        for overlay_path in sorted(OVERLAY_DIR.glob(GRAPH_OVERLAY_GLOB)):
            overlay = load_yaml_mapping(overlay_path)
            if overlay.get("schema") != "FPDG_CANONICAL_FEDERATION_OVERLAY_V0_1":
                raise FederationSurfaceError(
                    f"{overlay_path}: unsupported graph overlay schema {overlay.get('schema')!r}"
                )
            nodes = overlay.get("nodes", [])
            edges = overlay.get("edges", [])
            if not isinstance(nodes, list) or not isinstance(edges, list):
                raise FederationSurfaceError(f"{overlay_path}: nodes/edges must be lists")
            graph.setdefault("nodes", []).extend(deepcopy(nodes))
            graph.setdefault("edges", []).extend(deepcopy(edges))
            applied.append(str(overlay_path.relative_to(ROOT)))

    graph["effective_federation_overlays"] = applied
    return graph


def load_effective_claims(path: Path | str = BASE_CLAIMS_PATH) -> list[dict[str, Any]]:
    path = Path(path)
    rows = load_jsonl(path)
    if path.resolve() != BASE_CLAIMS_PATH.resolve():
        return rows

    if OVERLAY_DIR.exists():
        for overlay_path in sorted(OVERLAY_DIR.glob(CLAIMS_OVERLAY_GLOB)):
            rows.extend(load_jsonl(overlay_path))
    return rows


def load_effective_interfaces(
    path: Path | str = BASE_INTERFACES_PATH,
) -> dict[str, Any]:
    path = Path(path)
    payload = deepcopy(load_yaml_mapping(path))
    if path.resolve() != BASE_INTERFACES_PATH.resolve():
        return payload

    rows = payload.get("interfaces")
    if not isinstance(rows, list):
        raise FederationSurfaceError("cross_repo_interfaces.yaml: interfaces must be a list")
    applied: list[str] = []
    if OVERLAY_DIR.exists():
        for overlay_path in sorted(OVERLAY_DIR.glob(INTERFACE_OVERLAY_GLOB)):
            overlay = load_yaml_mapping(overlay_path)
            if overlay.get("schema") != "FPDG_CROSS_REPO_INTERFACE_OVERLAY_V0_1":
                raise FederationSurfaceError(
                    f"{overlay_path}: unsupported interface overlay schema {overlay.get('schema')!r}"
                )
            extra = overlay.get("interfaces", [])
            if not isinstance(extra, list):
                raise FederationSurfaceError(f"{overlay_path}: interfaces must be a list")
            rows.extend(deepcopy(extra))
            applied.append(str(overlay_path.relative_to(ROOT)))
    payload["effective_federation_overlays"] = applied
    return payload
