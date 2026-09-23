#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


PATH = Path("diagnostics/RFC_CARRIER_CANDIDATE_REGISTRY_V0_1.json")


def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    if data.get("selected_physical_carrier") is not None:
        raise SystemExit("FAIL: physical RFC carrier must remain unselected")
    candidates = data.get("candidates", [])
    if len(candidates) < 3:
        raise SystemExit("FAIL: candidate representation set unexpectedly collapsed")
    for row in candidates[:3]:
        if row.get("physical_identity") != "OPEN":
            raise SystemExit(
                f"FAIL: {row.get('id')} was promoted without source-owned physical identity"
            )
    bindings = data.get("cross_bindings", {})
    if not bindings or any(value != "OPEN" for value in bindings.values()):
        raise SystemExit("FAIL: carrier cross-binding frontier must remain explicit")
    if data.get("source_claim_status") != "ADMITTED_SOURCE_INTERFACE":
        raise SystemExit("FAIL: conserved carrier claim must remain typed as interface")
    print(
        "PASS: RFC conserved-carrier representations remain separate; "
        "no physical carrier is selected by conservation alone"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
