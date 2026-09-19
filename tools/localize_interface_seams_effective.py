#!/usr/bin/env python3
"""CLI adapter for seam localization on the effective federation surface."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import localize_interface_seams as base  # noqa: E402
from federation_surface import (  # noqa: E402
    BASE_GRAPH_PATH,
    BASE_INTERFACES_PATH,
    load_effective_graph,
    load_effective_interfaces,
)


def _yaml(path):
    path = Path(path)
    if path.resolve() == BASE_GRAPH_PATH.resolve():
        return load_effective_graph()
    if path.resolve() == BASE_INTERFACES_PATH.resolve():
        return load_effective_interfaces()
    return base.load_yaml(path)


base.load_yaml = _yaml

if __name__ == "__main__":
    raise SystemExit(base.main())
