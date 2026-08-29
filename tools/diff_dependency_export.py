#!/usr/bin/env python3
"""Compute an exact semantic diff between two FPDG DEPENDENCY_EXPORT documents.

Volatile/top-level provenance fields such as generated_at and source_commit are reported
separately from the scientific dependency surface. Claims are keyed by claim_id; local
edges are keyed by their complete JSON content. This lets the pain localizer distinguish
"repository head moved" from "a claim or local dependency actually changed".
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SURFACE_CLAIM_IGNORED_FIELDS: set[str] = set()
TOP_LEVEL_PROVENANCE_FIELDS = {"source_commit", "generated_at"}


class ExportDiffError(RuntimeError):
    pass


def load_export(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    validate_export(value)
    return value


def validate_export(value: Any) -> None:
    if not isinstance(value, dict):
        raise ExportDiffError("dependency export must be an object")
    if value.get("schema") != "FPDG_DEPENDENCY_EXPORT_V0_1":
        raise ExportDiffError(f"unsupported export schema {value.get('schema')!r}")
    if not isinstance(value.get("repository_id"), str):
        raise ExportDiffError("dependency export missing repository_id")
    if not isinstance(value.get("claims"), list) or not isinstance(value.get("local_edges", []), list):
        raise ExportDiffError("dependency export claims/local_edges must be arrays")


def _claim_map(export: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in export.get("claims", []):
        if not isinstance(row, dict) or not isinstance(row.get("claim_id"), str):
            raise ExportDiffError("every exported claim must have claim_id")
        claim_id = row["claim_id"]
        if claim_id in out:
            raise ExportDiffError(f"duplicate claim_id {claim_id}")
        out[claim_id] = row
    return out


def _edge_key(edge: dict[str, Any]) -> str:
    return json.dumps(edge, sort_keys=True, separators=(",", ":"))


def _edge_map(export: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out = {}
    for row in export.get("local_edges", []):
        if not isinstance(row, dict):
            raise ExportDiffError("every local edge must be an object")
        if not isinstance(row.get("from"), str) or not isinstance(row.get("to"), str):
            raise ExportDiffError("every local edge requires from/to")
        out[_edge_key(row)] = row
    return out


def _field_changes(old: dict[str, Any], new: dict[str, Any]) -> dict[str, dict[str, Any]]:
    changes = {}
    for key in sorted(set(old) | set(new)):
        if key == "claim_id" or key in SURFACE_CLAIM_IGNORED_FIELDS:
            continue
        if old.get(key) != new.get(key):
            changes[key] = {"old": old.get(key), "new": new.get(key)}
    return changes


def diff_exports(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    validate_export(old)
    validate_export(new)
    if old["repository_id"] != new["repository_id"]:
        raise ExportDiffError(
            f"repository_id mismatch old={old['repository_id']} new={new['repository_id']}"
        )

    old_claims = _claim_map(old)
    new_claims = _claim_map(new)
    old_edges = _edge_map(old)
    new_edges = _edge_map(new)

    claims_added = [new_claims[cid] for cid in sorted(set(new_claims) - set(old_claims))]
    claims_removed = [old_claims[cid] for cid in sorted(set(old_claims) - set(new_claims))]
    claims_changed = []
    for claim_id in sorted(set(old_claims) & set(new_claims)):
        changes = _field_changes(old_claims[claim_id], new_claims[claim_id])
        if changes:
            claims_changed.append({"claim_id": claim_id, "changes": changes})

    edges_added = [new_edges[key] for key in sorted(set(new_edges) - set(old_edges))]
    edges_removed = [old_edges[key] for key in sorted(set(old_edges) - set(new_edges))]

    provenance_changes = {}
    for field in sorted(TOP_LEVEL_PROVENANCE_FIELDS):
        if old.get(field) != new.get(field):
            provenance_changes[field] = {"old": old.get(field), "new": new.get(field)}

    surface_changed = bool(
        claims_added or claims_removed or claims_changed or edges_added or edges_removed
    )
    return {
        "schema": "FPDG_DEPENDENCY_EXPORT_SEMANTIC_DIFF_V0_1",
        "repository_id": old["repository_id"],
        "repository": new.get("repository") or old.get("repository"),
        "surface_changed": surface_changed,
        "claims_added": claims_added,
        "claims_removed": claims_removed,
        "claims_changed": claims_changed,
        "edges_added": edges_added,
        "edges_removed": edges_removed,
        "provenance_changes": provenance_changes,
    }


def observations_from_diff(diff: dict[str, Any], evidence_ref: str) -> list[dict[str, Any]]:
    repo_id = diff["repository_id"]
    observations: list[dict[str, Any]] = []
    sequence = 0

    for row in diff.get("claims_added", []):
        sequence += 1
        observations.append(
            {
                "observation_id": f"EXPORT.{sequence:03d}.{repo_id}.ADDED.{row['claim_id']}",
                "kind": "EXTRA_CLAIM",
                "repository": repo_id,
                "claim_id": row["claim_id"],
                "source_path": row.get("source_path"),
                "expected": None,
                "observed": row,
                "evidence_refs": [evidence_ref],
            }
        )
    for row in diff.get("claims_removed", []):
        sequence += 1
        observations.append(
            {
                "observation_id": f"EXPORT.{sequence:03d}.{repo_id}.REMOVED.{row['claim_id']}",
                "kind": "MISSING_CLAIM",
                "repository": repo_id,
                "claim_id": row["claim_id"],
                "source_path": row.get("source_path"),
                "expected": row,
                "observed": None,
                "evidence_refs": [evidence_ref],
            }
        )
    for row in diff.get("claims_changed", []):
        sequence += 1
        observations.append(
            {
                "observation_id": f"EXPORT.{sequence:03d}.{repo_id}.CHANGED.{row['claim_id']}",
                "kind": "STATUS_DRIFT" if "status" in row["changes"] else "OTHER",
                "repository": repo_id,
                "claim_id": row["claim_id"],
                "expected": {k: v["old"] for k, v in row["changes"].items()},
                "observed": {k: v["new"] for k, v in row["changes"].items()},
                "evidence_refs": [evidence_ref],
            }
        )
    for edge in diff.get("edges_added", []):
        sequence += 1
        observations.append(
            {
                "observation_id": f"EXPORT.{sequence:03d}.{repo_id}.EDGE_ADDED",
                "kind": "EXTRA_EDGE",
                "repository": repo_id,
                "edge": edge,
                "expected": None,
                "observed": edge,
                "evidence_refs": [evidence_ref],
            }
        )
    for edge in diff.get("edges_removed", []):
        sequence += 1
        observations.append(
            {
                "observation_id": f"EXPORT.{sequence:03d}.{repo_id}.EDGE_REMOVED",
                "kind": "MISSING_EDGE",
                "repository": repo_id,
                "edge": edge,
                "expected": edge,
                "observed": None,
                "evidence_refs": [evidence_ref],
            }
        )
    return observations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    args = parser.parse_args()
    try:
        result = diff_exports(load_export(args.old), load_export(args.new))
        print(json.dumps(result, indent=2))
        return 2 if result["surface_changed"] else 0
    except (OSError, json.JSONDecodeError, ExportDiffError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
