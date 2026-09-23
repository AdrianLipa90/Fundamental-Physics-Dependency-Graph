# Fundamental Mat–Phys–Chem Critical Path v0.1

Status: `NON_CANONICAL_CANDIDATE_OVERLAY / SOURCE_FIRST / CANON_ALLOWED_FALSE`

This overlay records the shortest currently supported path from the existing mathematical/phase geometry stack to a falsifiable chemical readout. It does not add nodes or edges to the canonical FPDG graph because the new Resonant Chemistry source claims are still on draft PR #35.

## Current reduction

The first-order chemistry operator need not be an arbitrary Hermitian matrix. For a declared phase/holonomy-dependent control Hamiltonian,

[
H(Phi+deltaPhi)
=
H(Phi)
+
sum_a deltaPhi_a,partial_{Phi_a}H
+
O(deltaPhi^2),
]

so the minimal candidate class is

[
oxed{
V_I^{(1)}
=
sum_a deltaPhi_a G_a,
qquad
G_a=partial_{Phi_a}H.
}
]

The control Hamiltonian fixes the response generators (G_a). The unresolved physical problem is therefore reduced to the source and normalization of the real, gauge-invariant cycle displacement (deltaPhi_a).

## Critical path

[
	ext{TIR/RFC phase geometry}
	o
oxed{deltaPhi 	ext{physical source}}
	o
	ext{RC state binding}
	o
V_I^{(1)}
	o
	ext{molecular controls}
	o
	ext{no-refit spectroscopy}.
]

The highlighted (deltaPhi) source is the current narrowest cross-repository physical bottleneck.

## Source-selector firewall

FPDG must not decide whether the physical source of (deltaPhi) is:

- `TIR.HOLONOMY.WIJ`;
- `RFC.F1.GAUGE_RELATIONAL_PHASE`;
- `RFC.F5.PHASE_ENERGY_ONE_FORM`;
- or a later source-owned carrier.

A cross-repository edge becomes admissible only after the owning source repository supplies the derivation, units, normalization, gauge law, carrier map, no-fit declaration and validation receipt.

## H2+ role

The minimal two-centre effective-state graph has

[
eta_1=E-V+C=0.
]

Therefore its graph edge phase is gauge-removable. (H_2^+) is simultaneously:

- a useful positive control for two-centre state/operator binding;
- an exact **negative control** for loop-holonomy spectroscopy.

A positive holonomy channel requires an independently justified cyclic effective-state graph with (eta_1ge1). Molecular geometric cyclicity must not be substituted for an electronic/effective-state cycle by visual analogy.

## Exact nulls

Two nulls are now mandatory:

[
V_I=u_0 I
quadLongrightarrowquad
Deltaomega_{mn}=0,
]

and

[
eta_1=0
quadLongrightarrowquad
	ext{no gauge-invariant loop-holonomy spectral channel}.
]

These nulls provide direct falsification controls before any new positive signal is sought.

## Source status

FPDG PR #24 supplies the updated TIR source surface (67 claims / 94 local edges) and is green, but remains unmerged.

Resonant Chemistry draft PR #35 owns the candidate source claims:

- `RC.MATTER.PHYSICAL_STATE_BINDING`;
- `RC.MATTER.INFORMATIONAL_PERTURBATION_VI`;
- `RC.MOLECULAR.H2PLUS_CONTROL`;
- `RC.SPECTROSCOPY.NO_REFIT_GATE`.

Its dedicated Quantum Matter Bridge reference gate is green. These claims are **not** imported canonically into FPDG before the source PR is merged and reconciled.

## Not on the minimal chemistry path

RH, strong CP, cosmological scale binding and full electroweak/Higgs closure are not blockers for a low-energy no-refit chemical test using established external low-energy constants. They remain necessary only for the stronger programme in which those constants are to be derived endogenously from the fundamental theory.

## Promotion order

1. Keep PR #24 unmerged until explicitly ordered.
2. Complete/review RC PR #35.
3. After RC source merge, refresh the RC source lock/export in FPDG.
4. Import the new RC source-owned local surface.
5. Resolve (deltaPhi) source ownership through a source-repository derivation.
6. Add only then the typed cross-repository candidate interface.
7. Run DAG, source-export, drift and impact gates.
8. Freeze operator, observable and decision rule before opening any holdout data.
