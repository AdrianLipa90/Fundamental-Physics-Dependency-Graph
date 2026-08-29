#!/usr/bin/env python3
"""Finalize drift diagnosis with exact sub-claim evidence coordinates.

The source-drift diagnostic produces claim/interface/signature layers. This finalizer
adds the finest coordinate actually present in the evidence and attaches those
coordinates to the GREMLIN diagnostic packet. It never invents a finer location than
the original evidence supports.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build"
DIAGNOSIS_PATH = BUILD_DIR / "INCONSISTENCY_DIAGNOSIS.json"
EVIDENCE_PATH = BUILD_DIR / "INCONSISTENCY_EVIDENCE.json"
PACKET_PATH = BUILD_DIR / "GREMLIN_PAIN_PACKET.json"

sys.path.insert(0, str(ROOT / "tools"))
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
        if not PACKET_PATH.exists():
            raise FinalizeError("diagnosis exists but GREMLIN diagnostic packet is missing")

        diagnosis = load_json(DIAGNOSIS_PATH)
        evidence = load_json(EVIDENCE_PATH) if EVIDENCE_PATH.exists() else None
        micro = localize(diagnosis, evidence)
        packet = enrich(load_json(PACKET_PATH), micro)

        BUILD_DIR.mkdir(exist_ok=True)
        (BUILD_DIR / "PAIN_MICRO_COORDINATES.json").write_text(
            json.dumps(micro, indent=2) + "\n", encoding="utf-8"
        )
        (BUILD_DIR / "PAIN_MICRO_COORDINATES.md").write_text(
            render_markdown(micro), encoding="utf-8"
        )
        PACKET_PATH.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")

        print(
            "PASS: finalized inconsistency localization "
            f"finest={micro['finest_precision']} "
            f"coordinates={len(micro['coordinates'])} "
            f"integration={len(micro['integration_coordinates'])}"
        )
        return 0
    except (
        OSError,
        json.JSONDecodeError,
        FinalizeError,
        MicroLocalizationError,
        MicroPacketError,
        KeyError,
        TypeError,
    ) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
