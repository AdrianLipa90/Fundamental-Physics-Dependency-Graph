# RFC ↔ Resonant Chemistry Edge/Path Phase Crosswalk v0.1

Status: NON_CANONICAL_CANDIDATE_CROSS_REPO_INTERFACE / EXACT_GAUGE_SIGN_CROSSWALK / PHYSICAL_EDGE_PATH_REALIZATION_OPEN

## 1. Existing endpoint conventions

Resonant Chemistry uses an oriented graph edge phase with local basis rephasing

\[
\theta_{ij}^{RC}
\mapsto
\theta_{ij}^{RC}+\chi_j-\chi_i.
\]

RFC F1 uses the minus-sign connection convention

\[
\mathcal A_-
\mapsto
\mathcal A_- - d\lambda.
\]

For an oriented RFC path \(\gamma_e:x_i\to x_j\),

\[
I_e:=\int_{\gamma_e}\mathcal A_-
\]

therefore transforms as

\[
I_e\mapsto I_e-(\lambda_j-\lambda_i).
\]

Hence the sign-compatible graph phase is

\[
\boxed{
\theta_e^{RC}
=
- I_e
=
-\int_{\gamma_e}\mathcal A_-,
}
\]

with \(\chi_i=\lambda_i\). Then exactly

\[
\theta_e^{RC}
\mapsto
\theta_e^{RC}+\chi_j-\chi_i.
\]

This is a convention/type theorem, not a physical binding.

## 2. Chain-map requirement

Let \(G_{RC}=(V,E)\) be the declared effective-state graph. A physical binding must supply a realization map

\[
\iota:
V\to\mathcal B_{RFC},
\qquad
e=(i,j)\mapsto\gamma_e:\iota(i)\to\iota(j),
\]

that preserves edge orientation and boundaries.

Equivalently, on oriented one-chains it must satisfy

\[
\boxed{
\partial\,\iota_\#(e)
=
\iota(j)-\iota(i).
}
\]

A graph cycle

\[
C_a=\sum_e s_{ae}e,
\qquad
\partial C_a=0,
\]

is then mapped to a closed RFC path

\[
\Gamma_a:=\iota_\#(C_a).
\]

## 3. Exact cycle-holonomy crosswalk

The RC cycle phase is

\[
\Phi_a^{RC}
=
\sum_e s_{ae}\theta_e^{RC}.
\]

Using the sign bridge,

\[
\Phi_a^{RC}
=
-\sum_e s_{ae}\int_{\gamma_e}\mathcal A_-
=
-\oint_{\Gamma_a}\mathcal A_-.
\]

RFC F1 identifies the lifted closed-loop phase

\[
\Gamma_a^{RFC}
=
\oint_{\Gamma_a}\mathcal A_-.
\]

Therefore, once the same physical cycle realization is admitted,

\[
\boxed{
\Phi_a^{RC}
=
-\Gamma_a^{RFC}.
}
\]

For reference and perturbed realizations that preserve the declared cycle identity,

\[
\boxed{
\delta\Phi_a^{RC}
=
-\delta\Gamma_a^{RFC}.
}
\]

No fitted coefficient is introduced by this sign/holonomy map.

## 4. Hamiltonian handoff

For a declared RC baseline hopping \(t_e^{(0)}\), the candidate RFC phase factor may be written

\[
t_e^{eff}
=
t_e^{(0)}
\exp\!\left(
-i\int_{\gamma_e}\mathcal A_-
\right).
\]

Hermiticity requires reverse-edge transport to use the inverse/conjugate phase, which follows from path reversal.

The RC first-order operator then remains

\[
V_I^{(1)}
=
\sum_a
\delta\Phi_a^{RC}
\frac{\partial H_{RC}}{\partial\Phi_a}
=
-
\sum_a
\delta\Gamma_a^{RFC}
\frac{\partial H_{RC}}{\partial\Phi_a}.
\]

The operator shape is fixed by the RC control Hamiltonian. The RFC contribution supplies only the gauge-invariant cycle displacement after physical binding.

## 5. Remaining physical gate

The exact mathematics above does not establish the realization map \(\iota\).

The remaining gate is

COMMON_PHYSICAL_EDGE_PATH_REALIZATION

and must provide:

1. RC effective-state vertex ↔ RFC endpoint identity;
2. RC edge ↔ oriented RFC physical path identity;
3. one common physical carrier;
4. stable cycle identity between reference and perturbed states;
5. baseline hopping-phase convention, avoiding double counting of intrinsic phases;
6. orientation/sign convention;
7. no target spectroscopy residuals used to define the map;
8. an independent source-side validation receipt.

Until that gate passes,

\[
\Phi_a^{RC}=-\Gamma_a^{RFC}
\]

is CANDIDATE_ONLY as a physical identification even though the gauge-sign crosswalk is exact.

## 6. Consequences for the critical path

The previous broad bottleneck DELTA_PHI_SOURCE_BINDING is reduced to

\[
\boxed{
\text{COMMON_PHYSICAL_EDGE_PATH_REALIZATION}.
}
\]

TIR semantic U(1) holonomy is not used as a direct chemistry source at its current status; its own source firewall keeps physical gauge binding open. RFC F1 is the appropriate exact gauge-kinematic parent, while RFC F5 may supply a conditional energy slope after physical B-action realization.

For the minimal H2+ two-vertex/one-edge graph,

\[
\beta_1=0,
\]

so there is no graph cycle to bind and loop-holonomy spectroscopy remains an exact null control.

A positive test requires a source-justified RC effective-state graph with \(\beta_1\ge1\) and an admitted \(\iota\) realization.
