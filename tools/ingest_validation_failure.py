#!/usr/bin/env python3
"""Convert source-side validation failure receipts into exact FPDG inconsistency evidence.

The source repository remains authoritative for the failure coordinate. This adapter
preserves claim/test/receipt/equation/line metadata verbatim and refuses to invent a
finer coordinate than the receipt supplies.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build"


class ReceiptError(RuntimeError):
    pass


ALLOWED_REPOSITORIES = {"TIR", "IDT", "RFC", "SOH", "FPDG"}
ALLOWED_KINDS = {
    "VALIDATOR_FAILURE",
    "TEST_FAILURE",
    "RECEIPT_FAILURE",
    "CROSS_REPO_CONTRACT_FAILURE",
    "EQUATION_CHECK_FAILURE",
    "SYMBOL_CHECK_FAILURE",
    "SOURCE_ASSERTION_FAILURE",
}
LOCATOR_FIELDS = {
    "path",
    "symbol",
    "equation_id",
    "line_start",
    "line_end",
    "validator_id",
    "test_id",
    "receipt_ref",
    "interface_id",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        value = json.load(fh)
    if not isinstance(value, dict):
        raise ReceiptError(f"{path}: expected JSON object")
    return value


def validate_locator(locator: Any, failure_id: str) -> dict[str, Any]:
    if locator is None:
        return {}
    if not isinstance(locator, dict):
        raise ReceiptError(f"{failure_id}: source_locator must be an object")
    unknown = sorted(set(locator) - LOCATOR_FIELDS)
    if unknown:
        raise ReceiptError(f"{failure_id}: unsupported source_locator fields: {unknown}")
    out = dict(locator)
    for key in ("path", "symbol", "equation_id", "validator_id", "test_id", "receipt_ref", "interface_id"):
        if key in out and (not isinstance(out[key], str) or not out[key].strip()):
            raise ReceiptError(f"{failure_id}: source_locator.{key} must be non-empty string")
    start = out.get("line_start")
    end = out.get("line_end")
    for key, value in (("line_start", start), ("line_end", end)):
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 1):
            raise ReceiptError(f"{failure_id}: source_locator.{key} must be positive integer")
    if end is not None and start is None:
        raise ReceiptError(f"{failure_id}: line_end requires line_start")
    if start is not None and end is not None and end < start:
        raise ReceiptError(f"{failure_id}: line_end precedes line_start")
    return out


def validate_receipt(receipt: dict[str, Any]) -> None:
    if receipt.get("schema") != "FPDG_VALIDATION_FAILURE_RECEIPT_V0_1":
        raise ReceiptError(f"unsupported receipt schema {receipt.get('schema')!r}")
    repo_id = receipt.get("repository_id")
    if repo_id not in ALLOWED_REPOSITORIES:
        raise ReceiptError(f"unsupported repository_id {repo_id!r}")
    source_commit = receipt.get("source_commit")
    if not isinstance(source_commit, str) or len(source_commit) != 40 or any(ch not in "0123456789abcdefABCDEF" for ch in source_commit):
        raise ReceiptError("source_commit must be a 40-character hex SHA")
    if receipt.get("status") != "FAIL":
        raise ReceiptError("validation failure receipt status must be FAIL")
    failures = receipt.get("failures")
    if not isinstance(failures, list) or not failures:
        raise ReceiptError("receipt failures must be non-empty list")
    seen = set()
    for row in failures:
        if not isinstance(row, dict):
            raise ReceiptError("failure row must be an object")
        failure_id = row.get("failure_id")
        if not isinstance(failure_id, str) or not failure_id:
            raise ReceiptError("failure_id must be non-empty string")
        if failure_id in seen:
            raise ReceiptError(f"duplicate failure_id {failure_id}")
        seen.add(failure_id)
        if row.get("kind") not in ALLOWED_KINDS:
            raise ReceiptError(f"{failure_id}: unsupported kind {row.get('kind')!r}")
        claim_id = row.get("claim_id")
        if claim_id is not None and (not isinstance(claim_id, str) or not claim_id):
            raise ReceiptError(f"{failure_id}: claim_id must be non-empty string")
        locator = validate_locator(row.get("source_locator"), failure_id)
        if not claim_id and not locator:
            raise ReceiptError(f"{failure_id}: claim_id or source_locator required")


def receipt_to_evidence(receipt: dict[str, Any]) -> dict[str, Any]:
    validate_receipt(receipt)
    repo_id = receipt["repository_id"]
    repository = receipt.get("repository")
    source_commit = receipt["source_commit"]
    workflow = receipt.get("workflow")
    job = receipt.get("job")
    run_id = receipt.get("run_id")
    observations = []
    for index, row in enumerate(receipt["failures"], 1):
        locator = validate_locator(row.get("source_locator"), row["failure_id"])
        refs = [str(ref) for ref in row.get("evidence_refs", []) if isinstance(ref, str) and ref]
        refs.append(f"source-commit:{repo_id}:{source_commit}")
        if workflow:
            refs.append(f"workflow:{workflow}")
        if job:
            refs.append(f"job:{job}")
        if run_id is not None:
            refs.append(f"run:{run_id}")
        observation: dict[str, Any] = {
            "observation_id": f"VALIDATION.{repo_id}.{index:03d}.{row['failure_id']}",
            "kind": row["kind"],
            "repository": repo_id,
            "expected": row.get("expected"),
            "observed": row.get("observed"),
            "evidence_refs": sorted(set(refs)),
            "message": row.get("message"),
        }
        claim_id = row.get("claim_id")
        if isinstance(claim_id, str):
            observation["claim_id"] = claim_id
        if locator:
            observation["source_locator"] = locator
            if isinstance(locator.get("path"), str):
                observation["source_path"] = locator["path"]
        if repository:
            observation["repository_full_name"] = repository
        observations.append(observation)
    return {
        "schema": "FPDG_INCONSISTENCY_EVIDENCE_V0_1",
        "incident_id": f"VALIDATION_FAILURE.{repo_id}.{source_commit[:12]}",
        "observations": observations,
        "source_receipt": {
            "schema": receipt["schema"],
            "repository_id": repo_id,
            "source_commit": source_commit,
            "workflow": workflow,
            "job": job,
            "run_id": run_id,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        evidence = receipt_to_evidence(load_json(args.receipt))
        BUILD_DIR.mkdir(exist_ok=True)
        target = BUILD_DIR / "VALIDATION_INCONSISTENCY_EVIDENCE.json"
        target.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        if args.json:
            print(json.dumps(evidence, indent=2))
        else:
            print(f"PASS: validation failure observations={len(evidence['observations'])}")
        return 0
    except (OSError, json.JSONDecodeError, ReceiptError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
