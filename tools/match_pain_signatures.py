#!/usr/bin/env python3
"""Match a current FPDG structural incident signature against reviewed history.

Matching is deterministic retrieval support for GREMLIN. Exact signature equality is a
strong structural recurrence. Non-exact similarity is Jaccard overlap over explicit
feature tokens and remains a candidate retrieval hint, never a claim of isomorphism.

Historical receipts fail closed when their stored hash or feature-token set disagrees
with the stored structural signature.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INCIDENT_DIR = ROOT / "diagnostics" / "incidents"
BUILD_DIR = ROOT / "build"

sys.path.insert(0, str(ROOT / "tools"))
from build_pain_signature import feature_tokens  # noqa: E402


class MatchError(RuntimeError):
    pass


def canonical_structure_hash(structure: dict[str, Any]) -> str:
    canonical = json.dumps(structure, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_signature(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict) or value.get("schema") != "FPDG_PAIN_SIGNATURE_V0_1":
        raise MatchError(f"{path}: expected FPDG_PAIN_SIGNATURE_V0_1")
    if value.get("candidate_edges_included") is not False:
        raise MatchError(f"{path}: incident signature must exclude candidate edges")
    if value.get("promotion_state") != "CANDIDATE_ONLY":
        raise MatchError(f"{path}: incident signature must remain CANDIDATE_ONLY")

    stored_hash = value.get("signature_hash")
    if not isinstance(stored_hash, str) or len(stored_hash) != 64:
        raise MatchError(f"{path}: missing/invalid signature_hash")
    structure = value.get("structural_signature")
    if not isinstance(structure, dict):
        raise MatchError(f"{path}: structural_signature must be an object")
    actual_hash = canonical_structure_hash(structure)
    if actual_hash != stored_hash:
        raise MatchError(
            f"{path}: signature hash mismatch stored={stored_hash} recomputed={actual_hash}"
        )

    tokens = value.get("feature_tokens")
    if not isinstance(tokens, list) or not all(isinstance(token, str) for token in tokens):
        raise MatchError(f"{path}: feature_tokens must be string array")
    expected_tokens = feature_tokens(structure)
    if tokens != expected_tokens:
        raise MatchError(f"{path}: feature_tokens disagree with structural_signature")
    return value


def jaccard(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def match_signature(
    current: dict[str, Any], historical: list[tuple[Path, dict[str, Any]]], threshold: float
) -> dict[str, Any]:
    current_tokens = set(current["feature_tokens"])
    rows = []
    for path, other in historical:
        other_tokens = set(other["feature_tokens"])
        exact = other["signature_hash"] == current["signature_hash"]
        score = 1.0 if exact else jaccard(current_tokens, other_tokens)
        if exact or score >= threshold:
            rows.append(
                {
                    "incident_path": str(path),
                    "signature_hash": other["signature_hash"],
                    "exact_structural_match": exact,
                    "feature_jaccard": score,
                    "shared_feature_count": len(current_tokens & other_tokens),
                    "current_feature_count": len(current_tokens),
                    "historical_feature_count": len(other_tokens),
                    "exact_coordinates": other.get("exact_coordinates", {}),
                    "incident_review": other.get("incident_review"),
                }
            )
    rows.sort(
        key=lambda row: (
            not row["exact_structural_match"],
            -row["feature_jaccard"],
            row["incident_path"],
        )
    )
    return {
        "schema": "FPDG_PAIN_SIGNATURE_MATCHES_V0_1",
        "current_signature_hash": current["signature_hash"],
        "threshold": threshold,
        "matches": rows,
        "match_count": len(rows),
        "interpretation": "RETRIEVAL_CANDIDATES_ONLY",
        "gremlin_promotion_authority": False,
    }


def collect_incidents(directory: Path, current_path: Path) -> list[tuple[Path, dict[str, Any]]]:
    if not directory.exists():
        return []
    rows = []
    current_resolved = current_path.resolve()
    for path in sorted(directory.glob("*.json")):
        if path.resolve() == current_resolved:
            continue
        try:
            rows.append((path, load_signature(path)))
        except (OSError, json.JSONDecodeError, MatchError) as exc:
            raise MatchError(f"invalid incident signature {path}: {exc}") from exc
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("signature", type=Path)
    parser.add_argument("--incident-dir", type=Path, default=DEFAULT_INCIDENT_DIR)
    parser.add_argument("--threshold", type=float, default=0.55)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not 0.0 <= args.threshold <= 1.0:
        print("FAIL: threshold must be in [0,1]", file=sys.stderr)
        return 1

    try:
        current = load_signature(args.signature)
        report = match_signature(
            current,
            collect_incidents(args.incident_dir, args.signature),
            args.threshold,
        )
        BUILD_DIR.mkdir(exist_ok=True)
        output = BUILD_DIR / "PAIN_SIGNATURE_MATCHES.json"
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(
                f"PASS: signature matches={report['match_count']} "
                f"threshold={report['threshold']}"
            )
        return 0
    except (OSError, json.JSONDecodeError, MatchError, KeyError, TypeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
