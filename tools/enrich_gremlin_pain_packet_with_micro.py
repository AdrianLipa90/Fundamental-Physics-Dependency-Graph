#!/usr/bin/env python3
"""Attach deterministic sub-claim evidence coordinates to an FPDG GREMLIN pain packet."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build"


class MicroPacketError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise MicroPacketError(f"{path}: expected JSON object")
    return value


def enrich(packet: dict[str, Any], micro: dict[str, Any]) -> dict[str, Any]:
    if packet.get("schema") != "FPDG_GREMLIN_PAIN_PACKET_V0_1":
        raise MicroPacketError(f"unsupported packet schema {packet.get('schema')!r}")
    if micro.get("schema") != "FPDG_PAIN_MICRO_COORDINATES_V0_1":
        raise MicroPacketError(f"unsupported micro schema {micro.get('schema')!r}")
    if micro.get("causal_inference_performed") is not False:
        raise MicroPacketError("micro-coordinate input must remain non-causal evidence localization")
    if micro.get("candidate_edges_included") is not False:
        raise MicroPacketError("micro-coordinate input must exclude candidate dependency edges")

    result = copy.deepcopy(packet)
    coords_by_id = {
        row["coordinate_id"]: row
        for row in micro.get("coordinates", [])
        if isinstance(row, dict) and isinstance(row.get("coordinate_id"), str)
    }
    micro_zone_by_frontier = {
        row["frontier_claim"]: row
        for row in micro.get("zones", [])
        if isinstance(row, dict) and isinstance(row.get("frontier_claim"), str)
    }

    for zone in result.get("zones", []):
        frontier = zone.get("frontier_claim")
        micro_zone = micro_zone_by_frontier.get(frontier, {})
        coordinate_ids = micro_zone.get("coordinate_ids", [])
        missing = [value for value in coordinate_ids if value not in coords_by_id]
        if missing:
            raise MicroPacketError(f"micro zone {frontier} references missing coordinates: {missing}")
        zone["micro_coordinates"] = [coords_by_id[value] for value in coordinate_ids]
        zone["finest_micro_precision"] = micro_zone.get("finest_precision", "UNSPECIFIED")

    integration_by_location = {
        row.get("location"): row
        for row in micro.get("integration_coordinates", [])
        if isinstance(row, dict) and isinstance(row.get("location"), str)
    }
    for zone in result.get("integration_zones", []):
        location = zone.get("frontier_location")
        if location in integration_by_location:
            zone["micro_coordinate"] = integration_by_location[location]

    result["source_micro_schema"] = micro.get("schema")
    result["micro_coordinate_status"] = micro.get("status")
    result["finest_micro_precision"] = micro.get("finest_precision")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("micro", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        output = enrich(load_json(args.packet), load_json(args.micro))
        BUILD_DIR.mkdir(exist_ok=True)
        target = BUILD_DIR / "GREMLIN_PAIN_PACKET_MICRO.json"
        target.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(output, indent=2))
        else:
            print(
                f"PASS: GREMLIN pain packet enriched with micro coordinates; "
                f"finest={output.get('finest_micro_precision')}"
            )
        return 0
    except (OSError, json.JSONDecodeError, MicroPacketError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
