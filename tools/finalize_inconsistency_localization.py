#!/usr/bin/env python3
"""Finalize drift diagnosis with exact sub-claim coordinates and probe ordering.

The source-drift diagnostic produces claim/interface/signature layers. This finalizer
adds the finest coordinate actually present in the evidence, builds a deterministic
inspection order, and attaches both to the GREMLIN diagnostic packet. It never invents
a finer location than the original evidence supports and never converts recurrence
hints into causal authority.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build"
DIAGNOSIS_PATH = BUILD_DIR / "INCONSISTENCY_DIAGNOSIS.json"
EVIDENCE_PATH = BUILD_DIR / "INCONSISTENCY_EVIDENCE.json"
SEAM_PATH = BUILD_DIR / "PAIN_SEAM_REPORT.json"
MATCHES_PATH = BUILD_DIR / "PAIN_SIGNATURE_MATCHES.json"
PACKET_PATH = BUILD_DIR / "GREMLIN_PAIN_PACKET.json"

sys.path.insert(0, str(ROOT / "tools"))
from build_diagnostic_probe_plan import ProbePlanError, build_plan, render_markdown as render_probe_plan  # noqa: E402
from enrich_gremlin_pain_packet_with_micro import MicroPacketError, enrich  # noqa: E402
from localize_micro_coordinates import MicroLocalizationError, localize, render_markdown  # noqa: E402


class FinalizeError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise FinalizeError(f"{path}: expected JSON object")
    return value


def main() -> int:
    try:
        if not DIAGNOSIS_PATH.exists():
            print("FRESH: no diagnosis to finalize")
            return 0
        for required in (PACKET_PATH, SEAM_PATH):
            if not required.exists():
                raise FinalizeError(f"diagnosis exists but required file is missing: {required.name}")

        diagnosis = load_json(DIAGNOSIS_PATH)
        evidence = load_json(EVIDENCE_PATH) if EVIDENCE_PATH.exists() else None
        micro = localize(diagnosis, evidence)
        matches = load_json(MATCHES_PATH) if MATCHES_PATH.exists() else None
        plan = build_plan(load_json(SEAM_PATH), micro, matches)

        packet = enrich(load_json(PACKET_PATH), micro)
        packet["diagnostic_probe_plan"] = plan

        BUILD_DIR.mkdir(exist_ok=True)
        (BUILD_DIR / "PAIN_MICRO_COORDINATES.json").write_text(
            json.dumps(micro, indent=2) + "\n", encoding="utf-8"
        )
        (BUILD_DIR / "PAIN_MICRO_COORDINATES.md").write_text(
            render_markdown(micro), encoding="utf-8"
        )
        (BUILD_DIR / "DIAGNOSTIC_PROBE_PLAN.json").write_text(
            json.dumps(plan, indent=2) + "\n", encoding="utf-8"
        )
        (BUILD_DIR / "DIAGNOSTIC_PROBE_PLAN.md").write_text(
            render_probe_plan(plan), encoding="utf-8"
        )
        PACKET_PATH.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")

        first_probes = [
            zone["first_probe"]["probe_id"]
            for zone in plan.get("zones", [])
            if isinstance(zone.get("first_probe"), dict)
        ]
        print(
            "PASS: finalized inconsistency localization "
            f"finest={micro['finest_precision']} "
            f"coordinates={len(micro['coordinates'])} "
            f"integration={len(micro['integration_coordinates'])} "
            f"first_probes={first_probes}"
        )
        return 0
    except (
        OSError,
        json.JSONDecodeError,
        FinalizeError,
        MicroLocalizationError,
        MicroPacketError,
        ProbePlanError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
