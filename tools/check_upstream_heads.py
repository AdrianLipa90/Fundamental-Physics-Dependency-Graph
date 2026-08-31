#!/usr/bin/env python3
"""Fail closed when any registered locked repository head differs from current main."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from federation_surface import FederationSurfaceError, repository_registry  # noqa: E402

LOCK_PATH = ROOT / "source_exports.lock.json"


def current_main_sha(repository: str) -> str:
    url = f"https://api.github.com/repos/{repository}/commits/main"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "FPDG-upstream-head-check/0.3",
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
        registry = repository_registry()
        if set(sources) != set(registry):
            raise RuntimeError(
                f"source lock/registry mismatch: lock={sorted(sources)} registry={sorted(registry)}"
            )
        stale = []
        for repo_id in sorted(registry):
            entry = sources[repo_id]
            if entry.get("repository") != registry[repo_id].get("repository"):
                raise RuntimeError(f"{repo_id}: repository identity mismatch")
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
                    f"{repo_id}: STALE locked_repository_head={expected} "
                    f"current_main={actual} represented_source={represented}",
                    file=sys.stderr,
                )
        if stale:
            print(
                "FAIL: upstream main advanced; run semantic export diff, refresh lock, "
                "and revalidate affected surface",
                file=sys.stderr,
            )
            return 2
        print(f"PASS: all {len(registry)} registered repository heads are fresh")
        return 0
    except (
        OSError,
        KeyError,
        json.JSONDecodeError,
        RuntimeError,
        FederationSurfaceError,
        urllib.error.URLError,
    ) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
