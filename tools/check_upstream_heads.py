#!/usr/bin/env python3
"""Fail closed when a locked source repository head no longer matches current main.

`repository_head` tracks repository-level freshness. `source_commit` separately records
the scientific source state represented by DEPENDENCY_EXPORT.json. Keeping these values
distinct prevents a metadata-only merge of an already locked export from masquerading as
scientific claim drift.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "source_exports.lock.json"


def current_main_sha(repository: str) -> str:
    url = f"https://api.github.com/repos/{repository}/commits/main"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "FPDG-upstream-head-check/0.2",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    sha = payload.get("sha")
    if not isinstance(sha, str) or len(sha) != 40:
        raise RuntimeError(f"{repository}: GitHub did not return a 40-char main SHA")
    return sha


def expected_repository_head(entry: dict) -> str:
    value = entry.get("repository_head", entry.get("source_commit"))
    if not isinstance(value, str) or len(value) != 40:
        raise RuntimeError("source lock entry has no valid repository_head/source_commit")
    return value


def main() -> int:
    try:
        lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        sources = lock.get("sources", {})
        stale = []
        for repo_id in ("TIR", "IDT", "RFC", "SOH"):
            entry = sources[repo_id]
            expected = expected_repository_head(entry)
            represented = entry["source_commit"]
            actual = current_main_sha(entry["repository"])
            if actual == expected:
                print(
                    f"{repo_id}: FRESH repository_head={actual} represented_source={represented}"
                )
            else:
                stale.append((repo_id, expected, actual))
                print(
                    f"{repo_id}: STALE locked_repository_head={expected} current_main={actual} "
                    f"represented_source={represented}",
                    file=sys.stderr,
                )
        if stale:
            print(
                "FAIL: upstream repository main advanced; run semantic export diff, refresh repository_head, and revalidate affected dependency surface",
                file=sys.stderr,
            )
            return 2
        print("PASS: all locked repository heads equal current source main heads")
        return 0
    except (OSError, KeyError, json.JSONDecodeError, RuntimeError, urllib.error.URLError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
