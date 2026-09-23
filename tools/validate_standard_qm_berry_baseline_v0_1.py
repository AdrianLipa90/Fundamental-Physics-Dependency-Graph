#!/usr/bin/env python3
"""Validate the same-state Berry no-double-counting bookkeeping."""

from __future__ import annotations

import cmath
import math


def main() -> int:
    # A nontrivial standard Berry loop with total phase pi.
    berry_links = tuple(cmath.exp(1j * math.pi / 3.0) for _ in range(3))
    berry_wilson = 1.0 + 0.0j
    for link in berry_links:
        berry_wilson *= link

    if abs(berry_wilson + 1.0) > 1e-12:
        raise SystemExit("FAIL: baseline Berry Wilson control")

    # Same-state RFC identification means identical links.
    rfc_links = berry_links

    residual = 1.0 + 0.0j
    naive_double_counted = 1.0 + 0.0j
    for berry, rfc in zip(berry_links, rfc_links):
        residual *= rfc * berry.conjugate()
        naive_double_counted *= rfc * berry

    if abs(residual - 1.0) > 1e-12:
        raise SystemExit("FAIL: same-state residual must be trivial")

    if abs(naive_double_counted - 1.0) > 1e-12:
        raise SystemExit("FAIL: expected doubled pi phase to close projectively")

    # Doubling the same connection changes the phase ledger: pi -> 2pi.
    if abs(cmath.phase(berry_wilson) - math.pi) > 1e-12:
        raise SystemExit("FAIL: baseline phase")
    if abs(cmath.phase(naive_double_counted)) > 1e-12:
        raise SystemExit("FAIL: doubled phase should wrap to zero")

    print(
        "PASS: same-state RFC connection equals Berry baseline; "
        "residual Wilson is unity; reusing it as an extra term double-counts phase"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
