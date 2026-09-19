#!/usr/bin/env python3
"""Run source-drift diagnosis against the effective federation surface."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import diagnose_source_drift as base  # noqa: E402
from federation_surface import (  # noqa: E402
    BASE_CLAIMS_PATH,
    BASE_GRAPH_PATH,
    BASE_INTERFACES_PATH,
    load_effective_claims,
    load_effective_graph,
    load_effective_interfaces,
)


def _claims(path=BASE_CLAIMS_PATH):
    path = Path(path)
    if path.resolve() == BASE_CLAIMS_PATH.resolve():
        return load_effective_claims()
    return base.load_claims(path)


def _graph(path=BASE_GRAPH_PATH):
    path = Path(path)
    if path.resolve() == BASE_GRAPH_PATH.resolve():
        return load_effective_graph()
    return base.load_graph(path)


def _seam_yaml(path):
    path = Path(path)
    if path.resolve() == BASE_GRAPH_PATH.resolve():
        return load_effective_graph()
    if path.resolve() == BASE_INTERFACES_PATH.resolve():
        return load_effective_interfaces()
    return base.load_seam_yaml(path)


base.load_claims = _claims
base.load_graph = _graph
base.load_seam_yaml = _seam_yaml

if __name__ == "__main__":
    raise SystemExit(base.main())
