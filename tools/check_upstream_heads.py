#!/usr/bin/env python3
"""Fail closed when a locked source dependency export no longer targets current source main.

This is the freshness gate for cross-repository dependency holonomy: if any source main
advances beyond the source_commit recorded in source_exports.lock.json, FPDG must be
reconciled before the locked-source validation can return green again.
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
        "User-Agent": "FPDG-upstream-head-check/0.1",
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


def main() -> int:
    try:
        lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        sources = lock.get("sources", {})
        stale = []
        for repo_id in ("TIR", "IDT", "RFC", "SOH"):
            entry = sources[repo_id]
            expected = entry["source_commit"]
            actual = current_main_sha(entry["repository"])
            if actual == expected:
                print(f"{repo_id}: FRESH main={actual}")
            else:
                stale.append((repo_id, expected, actual))
                print(
                    f"{repo_id}: STALE locked_source_commit={expected} current_main={actual}",
                    file=sys.stderr,
                )
        if stale:
            print(
                "FAIL: upstream source main advanced; refresh source export(s), lock and downstream impact validation",
                file=sys.stderr,
            )
            return 2
        print("PASS: all locked source commits equal current source main heads")
        return 0
    except (OSError, KeyError, json.JSONDecodeError, RuntimeError, urllib.error.URLError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
