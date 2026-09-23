#!/usr/bin/env python3
"""Validate the candidate RFC↔RC edge/path gauge-sign crosswalk.

This checks convention compatibility only. It does not validate a physical
edge/path realization or promote a cross-repository dependency.
"""
from __future__ import annotations

import cmath
import math


def close(a: float, b: float, atol: float = 1e-12) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=atol)


def main() -> int:
    edges = ((0, 1), (1, 2), (2, 0))
    rfc_integrals = (0.2, -0.4, 0.9)
    lambdas = (0.7, -0.2, 1.3)

    # Candidate convention: theta_RC = - integral A_minus.
    theta = tuple(-value for value in rfc_integrals)

    transformed_integrals = tuple(
        value - (lambdas[j] - lambdas[i])
        for value, (i, j) in zip(rfc_integrals, edges)
    )
    transformed_theta_from_rfc = tuple(-value for value in transformed_integrals)
    transformed_theta_from_rc = tuple(
        value + lambdas[j] - lambdas[i]
        for value, (i, j) in zip(theta, edges)
    )

    for left, right in zip(transformed_theta_from_rfc, transformed_theta_from_rc):
        if not close(left, right):
            raise SystemExit("FAIL: RFC/RC edge gauge transformations do not match")

    gamma_rfc = sum(rfc_integrals)
    phi_rc = sum(theta)
    if not close(phi_rc, -gamma_rfc):
        raise SystemExit("FAIL: cycle sign relation Phi_RC = -Gamma_RFC")

    perturbed_integrals = (0.23, -0.31, 1.04)
    gamma_rfc_1 = sum(perturbed_integrals)
    theta_1 = tuple(-value for value in perturbed_integrals)
    phi_rc_1 = sum(theta_1)

    delta_gamma_rfc = gamma_rfc_1 - gamma_rfc
    delta_phi_rc = phi_rc_1 - phi_rc
    if not close(delta_phi_rc, -delta_gamma_rfc):
        raise SystemExit("FAIL: displacement sign relation")

    forward = cmath.exp(1j * theta[0])
    reverse_integral = -rfc_integrals[0]
    reverse_theta = -reverse_integral
    reverse = cmath.exp(1j * reverse_theta)
    if abs(reverse - forward.conjugate()) > 1e-12:
        raise SystemExit("FAIL: reverse path does not give conjugate link phase")

    # E-V+C for the triangle = 3-3+1 = 1.
    beta1_triangle = len(edges) - 3 + 1
    if beta1_triangle != 1:
        raise SystemExit("FAIL: cyclic positive-control graph rank")

    # E-V+C for a two-vertex/one-edge H2+ minimal graph = 1-2+1 = 0.
    beta1_h2plus = 1 - 2 + 1
    if beta1_h2plus != 0:
        raise SystemExit("FAIL: H2+ null-control graph rank")

    print("PASS: RFC↔RC gauge-sign, cycle, displacement, reversal, and beta1 controls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
