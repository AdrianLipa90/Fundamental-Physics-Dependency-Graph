# Standard-QM Berry Baseline and No-Double-Counting Gate v0.1

Status: NON_CANONICAL_DIAGNOSTIC / STANDARD_QM_BINDING_CLOSED / INDEPENDENT_NEW_CARRIER_OPEN

## 1. Same-state-family identity

RFC F1 defines the minus-sign connection

\[
\mathcal A_-^{RFC}
=
+i\langle u|du\rangle.
\]

For a normalized chemical eigenstate family

\[
H_{\rm chem}(\lambda)|\Psi_n(\lambda)\rangle
=
E_n(\lambda)|\Psi_n(\lambda)\rangle,
\]

set

\[
u(\lambda)=\Psi_n(\lambda).
\]

Then identically

\[
\boxed{
\mathcal A_-^{RFC}
=
\mathcal A_{\rm Berry}^{chem}
=
+i\langle\Psi_n|d\Psi_n\rangle.
}
\]

This is a type/identity closure inside standard quantum mechanics.

It is not an extra interaction.

## 2. Molecular positive control

Resonant Chemistry PR #37 preregistered and executed an H3+ FCI/STO-3G molecular Berry loop.

Observed standard-QM control:

\[
W_{\rm enc}=-1,
\qquad
\Gamma_{\rm enc}=\pi,
\]

with minimum sampled excited-state gap

\[
7.835550301640293\times10^{-3}\ {\rm Ha}.
\]

The shifted non-encircling control gave

\[
W_{\rm ctl}=+1,
\qquad
\Gamma_{\rm ctl}=0,
\]

with minimum gap

\[
2.1359799604451668\times10^{-2}\ {\rm Ha}.
\]

State tracking remained on excited root 1 throughout both 24-point loops.

This closes a molecule-level STANDARD_QM_MOLECULAR_BERRY_BINDING control.

## 3. No-double-counting theorem

If RFC uses the same state family as the chemical Berry baseline,

\[
\mathcal A_-^{RFC}
=
\mathcal A_{\rm Berry}^{chem},
\]

then the RFC loop phase is already contained in the standard-QM adiabatic/geometric structure.

Therefore it cannot be reintroduced as an additional independent perturbation

\[
V_I^{new}
\]

without double counting the same phase degree of freedom.

A useful residual ledger is

\[
\boxed{
\mathcal A_{\rm residual}
=
\mathcal A_{\rm candidate}
-
\mathcal A_{\rm Berry}^{chem}.
}
\]

On the same-state-family branch,

\[
\boxed{
\mathcal A_{\rm residual}=0
}
\]

identically.

At the Wilson-link level,

\[
U_k^{RFC}=U_k^{Berry}
\quad\Longrightarrow\quad
U_k^{res}=U_k^{RFC}(U_k^{Berry})^{-1}=1,
\]

and hence

\[
\boxed{
W_{\rm residual}=1.
}
\]

Any nontrivial incremental phase requires an independently sourced connection/carrier.

## 4. Two branches must now be separated

### Branch A — standard-QM control

\[
u_{RFC}=\Psi_{\rm chem}.
\]

Then:

- RFC F1 connection = chemical Berry connection;
- RFC loop phase = standard molecular geometric phase;
- RC QGT/Berry controls own the physical baseline;
- incremental new-physics phase = zero.

Status:

\[
\boxed{\texttt{STANDARD\_QM\_BERRY\_BRANCH = CLOSED\ CONTROL}}
\]

### Branch B — new physical carrier

A genuinely new chemistry contribution requires a distinct physical source

\[
u_{RFC}^{new}\neq\Psi_{\rm chem}
\]

or an independently defined field/connection

\[
\mathcal A_{\rm new}
\]

plus an explicit coupling to the chemical Hilbert space.

The remaining gate is therefore

\[
\boxed{
\texttt{INDEPENDENT\_RFC\_CARRIER\_TO\_CHEMISTRY\_COUPLING}
}
\]

rather than the previous broad edge/path realization gate.

## 5. Requirements for the remaining gate

A candidate new carrier must provide:

1. independent physical state/field identity;
2. its own normalization and units;
3. gauge/transformation law;
4. a coupling operator into the chemical Hilbert space;
5. proof that the term is not already contained in the standard electronic Hamiltonian, derivative couplings, Berry connection or QGT;
6. a zero-coupling limit recovering the standard-QM control exactly;
7. preregistered observable and decision rule;
8. held-out validation without target fitting.

## 6. H2+ and H3+ now form a paired control ladder

H2+ minimal graph:

\[
\beta_1=0
\]

so loop holonomy is a null control.

H3+ conical-intersection loop:

\[
W=-1
\]

so standard-QM Berry holonomy is a positive molecular control.

Together they bracket the phase layer before any new carrier is admitted.

## 7. Source status

- FPDG PR #24: TIR reconciliation GREEN, unmerged.
- RFC PR #170: loop-phase interface reference suite GREEN, unmerged.
- RC PR #35: QMB/H2+ controls GREEN, unmerged.
- RC PR #36: synthetic Berry-loop positive control GREEN, unmerged.
- RC PR #37: preregistered molecular H3+ FCI Berry control GREEN, unmerged.
- This document remains diagnostic-only and does not import those unmerged source claims into canonical FPDG.
