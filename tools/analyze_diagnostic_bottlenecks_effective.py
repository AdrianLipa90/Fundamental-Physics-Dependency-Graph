#!/usr/bin/env python3
"""Run graph-dominance bottleneck analysis on the effective federation surface."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_diagnostic_bottlenecks as base  # noqa: E402
from federation_surface import BASE_GRAPH_PATH, load_effective_graph  # noqa: E402

_BASE_LOAD_GRAPH = base.load_graph


def load_graph(path: Path = BASE_GRAPH_PATH):
    path = Path(path)
    if path.resolve() == BASE_GRAPH_PATH.resolve():
        return load_effective_graph()
    return _BASE_LOAD_GRAPH(path)


base.load_graph = load_graph
BottleneckError = base.BottleneckError
analyze = base.analyze
render_markdown = base.render_markdown

if __name__ == "__main__":
    raise SystemExit(base.main())
