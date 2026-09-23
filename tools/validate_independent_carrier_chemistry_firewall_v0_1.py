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
