# Platonic–Ramanujan Spectral Carrier Cross-Repository Interface v0.1

Status: `CANDIDATE_ONLY / NO_CANONICAL_EDGE_PROMOTION`

Date: 2026-09-11

## Purpose

Register the new TIR ↔ PhaseNav spectral carrier without propagating it into unrelated downstream physical claims before validation.

## Upstream TIR source

Repository: `AdrianLipa90/The-Fundamental-Theory-of-Informational-Relations`

Branch: `feat/platonic-ramanujan-spectral-carrier-20260911`

Source surface:

`TIR/foundations/TIR_PLATONIC_RAMANUJAN_SPECTRAL_CARRIER_V0_1.md`

Validator:

`TIR/validation/tir_platonic_ramanujan_spectral_carrier_v0_1.py`

The exact finite layer establishes:

- all five Platonic skeleton graphs satisfy the finite Ramanujan graph bound;
- the 36-node candidate carrier is `I12 square K3`;
- it is 7-regular with 126 edges;
- its nontrivial spectral radius is `2+sqrt(5)`;
- its normalized Laplacian gap is `(5-sqrt(5))/7`;
- its degree obeys `7 = L3 = L4 + L5 = 5 + 2`.

The identification of this graph as a TIR/PhaseNav carrier is structural/candidate, not a new physical law.

## Downstream PhaseNav candidate

Repository: `AdrianLipa90/PhaseNav-Natural-Coding-System`

Branch: `feat/platonic-ramanujan-stabilizer-v0.1`

Specification:

`spec/PNCS_PLATONIC_RAMANUJAN_STABILIZER_V0_1.md`

Implementation:

`src/phasenav_natural_code/platonic_ramanujan_stabilizer_v01.py`

The candidate preserves the existing ordered 12x3 lane grouping and introduces an optional, non-actuating regularizer

\[
C_i^{PR}=-\frac{\beta}{7}\sum_jA_{ij}\sin(\phi_i-\phi_j).
\]

Its isolated local-linear mean-zero decay bound is

\[
r_{min}=\beta\frac{5-\sqrt5}{7}.
\]

The parent v0.32 runtime is not modified and the candidate is disabled by default.

## Candidate dependency edges

The following edges are registered conceptually but are **not** promoted into `dependency_graph.yaml` by this branch:

```text
TIR.PLATONIC_L_CONSTANTS
    -> TIR.PLATONIC_RAMANUJAN_SPECTRAL_CARRIER

PNCS.36D_BASIS
    -> PNCS.PLATONIC_RAMANUJAN_STABILIZER

PNCS.ORDERED_T36_TO_HTRI_DRIVE_V0_32
    -> PNCS.PLATONIC_RAMANUJAN_STABILIZER

TIR.PLATONIC_RAMANUJAN_SPECTRAL_CARRIER
    -candidate-> PNCS.PLATONIC_RAMANUJAN_STABILIZER

PNCS.SEMANTIC_ORBITAL_HTRI_BRIDGE
    -candidate-> PNCS.PLATONIC_RAMANUJAN_ORBITAL_BENCHMARK
```

## Explicit non-propagation boundary

No new edge is introduced here into:

- IDT temporal primitives;
- RFC Einstein/ADM closure;
- Standard-Model observable claims;
- cosmology;
- physical QPU/H200 claims;
- production NOEMA runtime authority.

Those require separate bridge theorems or empirical gates.

## Promotion gate

Canonical dependency-graph promotion requires all of:

1. TIR validator PASS on the exact committed branch bytes;
2. PNCS repository tests PASS on the exact committed branch bytes;
3. comparative PhaseNav runtime benchmark against baseline v0.32;
4. no regression in ordered-path distinction, target error, Hermiticity or unitarity;
5. orbital benchmark if the orbital edge is promoted;
6. explicit update of `dependency_graph.yaml` and `claims.jsonl` through their repository validators.

Until those gates pass, this document is provenance and dependency planning only.
