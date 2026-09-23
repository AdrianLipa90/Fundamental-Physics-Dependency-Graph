#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


PATH = Path("diagnostics/INDEPENDENT_CARRIER_CHEMISTRY_ADMISSION_FIREWALL_V0_1.json")


def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    if data.get("admission_state") != "BLOCKED_BY_SOURCE_OWNED_OPEN_INPUTS":
        raise SystemExit("FAIL: new-physics chemistry admission must remain blocked")
    groups = data.get("source_owned_open_inputs", {})
    if not groups or any(not values for values in groups.values()):
        raise SystemExit("FAIL: blocker groups must be explicit and nonempty")
    if data.get("remaining_gate") != "INDEPENDENT_RFC_CARRIER_TO_CHEMISTRY_COUPLING":
        raise SystemExit("FAIL: wrong remaining physical gate")
    nogo = data.get("identifiability_nogo_candidate", {})
    if nogo.get("nullspace_dimension") != 2:
        raise SystemExit("FAIL: carrier-scale identifiability nullspace must remain dimension two")
    if "source density alone cannot identify" not in nogo.get("consequence", ""):
        raise SystemExit("FAIL: identifiability consequence missing")

    drift = data.get("rfc_n1b2k_status_drift", {})
    if "PHYSICAL_REALIZATION_INPUT_OPEN" not in drift.get("source_authoritative_status", ""):
        raise SystemExit("FAIL: RFC N1B2K physical-realization firewall missing")
    if drift.get("handling") != (
        "DO_NOT_PROMOTE_CURRENT_MEASURE_AS_REALIZED_PHYSICS_BEFORE_SOURCE_MERGE_AND_RECONCILIATION"
    ):
        raise SystemExit("FAIL: stale RFC current-measure status handling missing")

    forbidden = set(data.get("forbidden_promotions", []))
    required = {
        "no fitted B action from target spectroscopy",
        "no reuse of standard Berry connection as extra interaction",
        "no physical scale claim from dimensionless RF-E20 closure alone",
    }
    if not required.issubset(forbidden):
        raise SystemExit("FAIL: no-double-counting / no-fit firewall incomplete")
    print(
        "PASS: admission firewall blocks new chemistry until independent RFC "
        "carrier, normalization, observable binding and coupling are source-closed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
