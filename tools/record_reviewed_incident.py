#!/usr/bin/env python3
"""Append a reviewed FPDG structural incident to GREMLIN incident memory.

CI output is deliberately not auto-promoted into history. This tool requires an explicit
incident id and reviewer, validates the structural signature, validates the candidate-only
GREMLIN packet safety boundary, and refuses to overwrite any existing incident receipt.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INCIDENT_DIR = ROOT / "diagnostics" / "incidents"
DEFAULT_PACKET_DIR = DEFAULT_INCIDENT_DIR / "packets"

sys.path.insert(0, str(ROOT / "tools"))
from match_pain_signatures import MatchError, load_signature  # noqa: E402


class IncidentRecordError(RuntimeError):
    pass


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def safe_incident_id(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise IncidentRecordError("incident_id is required")
    value = value.strip()
    if not re.fullmatch(r"[A-Za-z0-9._-]+", value):
        raise IncidentRecordError("incident_id may contain only A-Z a-z 0-9 . _ -")
    return value


def validate_packet(packet: dict[str, Any]) -> None:
    if packet.get("schema") != "FPDG_GREMLIN_PAIN_PACKET_V0_1":
        raise IncidentRecordError("unsupported GREMLIN packet schema")
    required = {
        "epistemic": "CHYBA",
        "promotion_state": "CANDIDATE_ONLY",
        "runtime_execution_authority": False,
        "canon_write_authority": False,
        "vector_guessing_allowed": False,
        "candidate_edges_enter_canon": False,
    }
    for key, expected in required.items():
        if packet.get(key) != expected:
            raise IncidentRecordError(
                f"unsafe GREMLIN packet field {key}: expected {expected!r}, got {packet.get(key)!r}"
            )


def record_incident(
    signature: dict[str, Any],
    packet: dict[str, Any],
    *,
    incident_id: str,
    reviewed_by: str,
    evidence_refs: list[str],
    incident_dir: Path = DEFAULT_INCIDENT_DIR,
    packet_dir: Path = DEFAULT_PACKET_DIR,
) -> tuple[Path, Path]:
    incident_id = safe_incident_id(incident_id)
    if not isinstance(reviewed_by, str) or not reviewed_by.strip():
        raise IncidentRecordError("reviewed_by is required")
    if any(not isinstance(ref, str) or not ref.strip() for ref in evidence_refs):
        raise IncidentRecordError("evidence refs must be non-empty strings")
    validate_packet(packet)

    signature_path = incident_dir / f"{incident_id}.json"
    packet_path = packet_dir / f"{incident_id}.json"
    if signature_path.exists() or packet_path.exists():
        raise IncidentRecordError(f"incident id already exists: {incident_id}")

    packet_hash = canonical_sha256(packet)
    review = {
        "incident_id": incident_id,
        "reviewed_by": reviewed_by.strip(),
        "evidence_refs": sorted(set(ref.strip() for ref in evidence_refs)),
        "packet_sha256": packet_hash,
        "append_only": True,
        "auto_promoted_from_ci": False,
    }

    stored_signature = copy.deepcopy(signature)
    stored_signature["incident_review"] = review
    stored_packet = copy.deepcopy(packet)
    stored_packet["incident_review"] = review

    incident_dir.mkdir(parents=True, exist_ok=True)
    packet_dir.mkdir(parents=True, exist_ok=True)
    signature_path.write_text(json.dumps(stored_signature, indent=2) + "\n", encoding="utf-8")
    packet_path.write_text(json.dumps(stored_packet, indent=2) + "\n", encoding="utf-8")
    return signature_path, packet_path


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise IncidentRecordError(f"{path}: expected JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("signature", type=Path)
    parser.add_argument("packet", type=Path)
    parser.add_argument("--incident-id", required=True)
    parser.add_argument("--reviewed-by", required=True)
    parser.add_argument("--evidence-ref", action="append", default=[])
    parser.add_argument("--incident-dir", type=Path, default=DEFAULT_INCIDENT_DIR)
    parser.add_argument("--packet-dir", type=Path, default=DEFAULT_PACKET_DIR)
    args = parser.parse_args()

    try:
        signature = load_signature(args.signature)
        packet = load_json(args.packet)
        signature_path, packet_path = record_incident(
            signature,
            packet,
            incident_id=args.incident_id,
            reviewed_by=args.reviewed_by,
            evidence_refs=args.evidence_ref,
            incident_dir=args.incident_dir,
            packet_dir=args.packet_dir,
        )
        print(f"PASS: recorded reviewed incident {signature_path} + {packet_path}")
        return 0
    except (
        OSError,
        json.JSONDecodeError,
        MatchError,
        IncidentRecordError,
        TypeError,
        ValueError,
    ) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
