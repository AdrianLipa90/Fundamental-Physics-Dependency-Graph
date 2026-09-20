# Candidate Cross-Repository Phase / Orbital / Chemistry / Spectroscopy Graph v0.1

Status: `NON_FEDERATED_CANDIDATE_OVERLAY / SOURCE_PATHS_PINNED_BY_NAME / NO_CANON_PROMOTION`

## Purpose

This document records the dependency graph created by the current phase-mechanics / EB-orbital integration without extending the locked FPDG source federation.

GREMLIN, QHTRI Phase Optics and PhaseNav Telescope are not silently inserted into the existing five-source federation by this file. A later federation change must register them explicitly and refresh the lock/provenance cycle.

## Graph

```text
RFC RF-S16/S20/S22
  Noether current -> occupation -> H_Phi^EB
                 |
                 | E_G = H_Phi^EB   [conditional parent]
                 v
GREMLIN v0.8 source identifiability
  mu_source = C_mu E_Sigma
                 |
                 | E_Sigma = E_G
                 v
GREMLIN v0.9 EB orbital-phase bridge
  mu_source = C_mu H_Phi^EB
  omega^2 =
    C_mu H_Phi^EB eta_G/r^3
    + alpha_I/(m_I r kappa_E) dXi_I/dr
                 ^
                 |
QHTRI informational phase mechanics
  Xi_I -> U_I -> action -> phase
  grad Phi -> steering
  Hess Phi -> lens / caustic
                 |
        +--------+---------+
        |                  |
        v                  v
Resonant-Chemistry      PhaseNav Telescope
Delta E_n(R)            Phi_I(omega)
grad/Hess E             dPhi/domega
Delta omega_mn          d2Phi/domega2
        |                  |
        +--------+---------+
                 v
       cross-domain consistency
```

## Authority split

RFC owns:
- conserved-current / occupation interfaces;
- `H_Phi^EB`;
- conditional integrated source closure.

GREMLIN owns:
- role-separated source/coupling orbit kernel;
- source/coupling identifiability firewall;
- EB orbital-phase candidate composition.

QHTRI phase optics owns:
- informational-potential functional;
- phase mechanics;
- lens Jacobian and standard gravitational-lensing cross-check.

Resonant-Chemistry owns:
- conventional electronic/nuclear Hamiltonian controls;
- energy, force, Hessian and transition-shift response.

PhaseNav Telescope owns:
- instrument forward model;
- spectral receiver/readout and holdout controls.

## Promotion firewalls

The following edges remain CANDIDATE/OPEN:

```text
physical EB condensate -> RFC phase/current state
H_Phi^EB -> physical mu_source
C_mu physical calibration
eta_G physical source/coupling ownership
U_I -> orbital carrier Lagrangian
U_I -> chemistry Hamiltonian perturbation
orbital omega -> emitted/absorbed spectral omega
U_I -> g_mu_nu
```

No edge above is promoted by the existence of algebraically compatible endpoint equations.

## Source paths

RFC:
`formalism/RF_GREMLIN_EB_ORBITAL_PHASE_CROSSWALK_V0_1.md`

GREMLIN:
`spec/GREMLIN_EB_CONDENSATE_ORBITAL_PHASE_BRIDGE_V0_9.md`

QHTRI Phase Optics:
`docs/PHASE_MECHANICS_GREMLIN_ORBITAL_EB_BRIDGE.md`

Resonant-Chemistry:
`docs/INFORMATIONAL_PHASE_EB_ORBITAL_SPECTROSCOPY_CROSSWALK.md`

PhaseNav Telescope:
`docs/INFORMATIONAL_PHASE_EB_ORBITAL_SPECTRAL_CROSSWALK.md`
