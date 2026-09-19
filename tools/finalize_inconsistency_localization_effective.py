#!/usr/bin/env python3
"""Finalize inconsistency localization using effective-federation bottleneck geometry."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import finalize_inconsistency_localization as base  # noqa: E402
from analyze_diagnostic_bottlenecks_effective import load_graph  # noqa: E402

base.load_bottleneck_graph = load_graph

if __name__ == "__main__":
    raise SystemExit(base.main())
