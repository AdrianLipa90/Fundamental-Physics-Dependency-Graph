#!/usr/bin/env python3
"""Run validation nerve-coverage audit on the effective federation surface."""
from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import audit_validation_coverage as base  # noqa: E402
from federation_surface import (  # noqa: E402
    BASE_GRAPH_PATH,
    BASE_INTERFACES_PATH,
    load_effective_graph,
    load_effective_interfaces,
)

RC_PRODUCER_OVERLAY = ROOT / "diagnostics" / "VALIDATION_PRODUCERS_RC_V0_1.yaml"
_BASE_LOAD_YAML = base.load_yaml


def load_effective_registry() -> dict:
    registry = deepcopy(_BASE_LOAD_YAML(base.REGISTRY_PATH))
    if not RC_PRODUCER_OVERLAY.exists():
        return registry
    overlay = _BASE_LOAD_YAML(RC_PRODUCER_OVERLAY)
    if overlay.get("schema") != "FPDG_VALIDATION_PRODUCER_OVERLAY_V0_1":
        raise base.CoverageError("unsupported validation producer overlay schema")
    extra = overlay.get("producers")
    if not isinstance(extra, dict):
        raise base.CoverageError("validation producer overlay requires producers mapping")
    producers = registry.get("producers")
    if not isinstance(producers, dict):
        raise base.CoverageError("base producer registry requires producers mapping")
    collisions = sorted(set(producers) & set(extra))
    if collisions:
        raise base.CoverageError(f"validation producer overlay collisions: {collisions}")
    producers.update(deepcopy(extra))
    registry["effective_producer_overlays"] = [str(RC_PRODUCER_OVERLAY.relative_to(ROOT))]
    return registry


def _load_yaml(path: Path):
    path = Path(path)
    if path.resolve() == BASE_GRAPH_PATH.resolve():
        return load_effective_graph()
    if path.resolve() == BASE_INTERFACES_PATH.resolve():
        return load_effective_interfaces()
    if path.resolve() == base.REGISTRY_PATH.resolve():
        return load_effective_registry()
    return _BASE_LOAD_YAML(path)


base.load_yaml = _load_yaml

if __name__ == "__main__":
    raise SystemExit(base.main())
