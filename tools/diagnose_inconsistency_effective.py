#!/usr/bin/env python3
"""CLI adapter for deterministic inconsistency diagnosis on the effective federation."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import diagnose_inconsistency as base  # noqa: E402
from federation_surface import (  # noqa: E402
    BASE_CLAIMS_PATH,
    BASE_GRAPH_PATH,
    load_effective_claims,
    load_effective_graph,
)


def _graph(path=BASE_GRAPH_PATH):
    path = Path(path)
    return load_effective_graph() if path.resolve() == BASE_GRAPH_PATH.resolve() else base.load_graph(path)


def _claims(path=BASE_CLAIMS_PATH):
    path = Path(path)
    return load_effective_claims() if path.resolve() == BASE_CLAIMS_PATH.resolve() else base.load_claims(path)


base.load_graph = _graph
base.load_claims = _claims

if __name__ == "__main__":
    raise SystemExit(base.main())
