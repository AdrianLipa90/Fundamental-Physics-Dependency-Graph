#!/usr/bin/env python3
"""Detect source-main drift and project its dependency blast radius.

Repository freshness is compared against `repository_head` in source_exports.lock.json.
The export's `source_commit` is a different quantity: the scientific source state that
the dependency export represents. This distinction prevents dependency-export/addendum
merges from being misclassified as scientific claim changes.

When a repository head genuinely advances beyond the locked repository_head, changed file
paths are mapped conservatively to source-owned claims. The downstream diagnosis layer
then performs a semantic dependency-export diff before accepting that coarse mapping.
CANDIDATE_ONLY edges are excluded from canonical revalidation impact.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "source_exports.lock.json"
CLAIMS_PATH = ROOT / "claims.jsonl"
BUILD_DIR = ROOT / "build"

sys.path.insert(0, str(ROOT / "tools"))
from impact import compute_impact, load_graph  # noqa: E402


def github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "FPDG-source-drift-watch/0.2",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def github_json(url: str) -> Any:
    request = urllib.request.Request(url, headers=github_headers())
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def current_main_sha(repository: str) -> str:
    payload = github_json(f"https://api.github.com/repos/{repository}/commits/main")
    sha = payload.get("sha") if isinstance(payload, dict) else None
    if not isinstance(sha, str) or len(sha) != 40:
        raise RuntimeError(f"{repository}: GitHub did not return a 40-char main SHA")
    return sha


def expected_repository_head(entry: dict[str, Any]) -> str:
    value = entry.get("repository_head", entry.get("source_commit"))
    if not isinstance(value, str) or len(value) != 40:
        raise RuntimeError("source lock entry has no valid repository_head/source_commit")
    return value


def changed_paths(repository: str, base: str, head: str) -> list[str]:
    base_q = urllib.parse.quote(base, safe="")
    head_q = urllib.parse.quote(head, safe="")
    payload = github_json(
        f"https://api.github.com/repos/{repository}/compare/{base_q}...{head_q}"
    )
    files = payload.get("files", []) if isinstance(payload, dict) else []
    paths = []
    for row in files:
        if isinstance(row, dict) and isinstance(row.get("filename"), str):
            paths.append(row["filename"])
    return sorted(set(paths))


def load_claim_rows(path: Path = CLAIMS_PATH) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def map_paths_to_claims(
    repo_id: str,
    paths: list[str],
    claims: list[dict[str, Any]],
) -> tuple[list[str], bool]:
    owned = [row for row in claims if row.get("repository") == repo_id]
    path_set = set(paths)
    mapped = sorted(
        {
            row["claim_id"]
            for row in owned
            if isinstance(row.get("source_path"), str) and row["source_path"] in path_set
        }
    )
    if mapped:
        return mapped, False
    return sorted(row["claim_id"] for row in owned), True


def aggregate_impact(graph: dict[str, Any], changed_claims: list[str]) -> list[dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    roots: defaultdict[str, list[str]] = defaultdict(list)
    for claim_id in changed_claims:
        for row in compute_impact(graph, claim_id, include_candidates=False):
            target = row["claim_id"]
            roots[target].append(claim_id)
            previous = best.get(target)
            if previous is None or row["distance"] < previous["distance"]:
                best[target] = dict(row)
    out = []
    for target, row in best.items():
        item = dict(row)
        item["changed_roots"] = sorted(set(roots[target]))
        out.append(item)
    return sorted(out, key=lambda row: (row["distance"], row["repository"], row["claim_id"]))


def render_markdown(report: dict[str, Any]) -> str:
    lines = ["# FPDG Source Drift Report", ""]
    lines.append(f"Status: **{report['status']}**")
    lines.append("")
    for source in report["sources"]:
        lines.append(
            f"- **{source['repository_id']}** — {source['status']} — "
            f"locked head `{source['locked_repository_head'][:12]}` / current `{source['current_main'][:12]}`"
        )
        lines.append(f"  - represented scientific source: `{source['represented_source_commit'][:12]}`")
        if source.get("changed_paths"):
            lines.append(f"  - changed paths: {len(source['changed_paths'])}")
        if source.get("changed_claims"):
            mode = "conservative all-owned fallback" if source.get("fallback_all_owned") else "path-mapped"
            lines.append(f"  - provisional changed claims: {len(source['changed_claims'])} ({mode})")
    lines.extend(["", f"Promoted downstream claims provisionally requiring revalidation: **{len(report['impacted'])}**", ""])
    for row in report["impacted"]:
        lines.append(f"- `{row['claim_id']}` ({row['repository']}, distance {row['distance']})")
    if not report["impacted"]:
        lines.append("- none")
    lines.append("")
    lines.append("`CANDIDATE_ONLY` edges were excluded. Semantic export diagnosis runs downstream of this provisional detector.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fail-on-drift", action="store_true")
    parser.add_argument("--json", action="store_true", help="also print the report JSON")
    args = parser.parse_args()

    try:
        lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        claims = load_claim_rows()
        graph = load_graph()
        source_reports = []
        all_changed_claims: set[str] = set()

        for repo_id in ("TIR", "IDT", "RFC", "SOH"):
            entry = lock["sources"][repo_id]
            repository = entry["repository"]
            expected_head = expected_repository_head(entry)
            represented_source = entry["source_commit"]
            actual = current_main_sha(repository)
            source = {
                "repository_id": repo_id,
                "repository": repository,
                "locked_repository_head": expected_head,
                "locked_source_commit": represented_source,
                "represented_source_commit": represented_source,
                "current_main": actual,
            }
            if actual == expected_head:
                source.update(
                    {
                        "status": "FRESH",
                        "changed_paths": [],
                        "changed_claims": [],
                        "fallback_all_owned": False,
                    }
                )
            else:
                paths = changed_paths(repository, expected_head, actual)
                mapped, fallback = map_paths_to_claims(repo_id, paths, claims)
                all_changed_claims.update(mapped)
                source.update(
                    {
                        "status": "DRIFT",
                        "changed_paths": paths,
                        "changed_claims": mapped,
                        "fallback_all_owned": fallback,
                    }
                )
            source_reports.append(source)

        impacted = aggregate_impact(graph, sorted(all_changed_claims))
        drifted = [row["repository_id"] for row in source_reports if row["status"] == "DRIFT"]
        report = {
            "schema": "FPDG_SOURCE_DRIFT_REPORT_V0_2",
            "status": "DRIFT" if drifted else "FRESH",
            "drifted_repositories": drifted,
            "changed_claims": sorted(all_changed_claims),
            "sources": source_reports,
            "impacted": impacted,
            "candidate_edges_included": False,
            "changed_claims_are_provisional_until_semantic_export_diff": True,
        }

        BUILD_DIR.mkdir(exist_ok=True)
        (BUILD_DIR / "SOURCE_DRIFT_REPORT.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        (BUILD_DIR / "SOURCE_DRIFT_REPORT.md").write_text(render_markdown(report), encoding="utf-8")

        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(
                f"{report['status']}: drifted={drifted} "
                f"provisional_changed_claims={len(all_changed_claims)} impacted={len(impacted)}"
            )

        if drifted and args.fail_on_drift:
            return 2
        return 0
    except (OSError, KeyError, json.JSONDecodeError, RuntimeError, urllib.error.URLError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
