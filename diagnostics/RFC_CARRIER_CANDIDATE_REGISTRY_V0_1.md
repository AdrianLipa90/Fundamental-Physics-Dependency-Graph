# RFC Carrier Candidate Registry v0.1

Status: NON_CANONICAL_DIAGNOSTIC / CONSERVATION_PRESENT / PHYSICAL_CARRIER_SELECTION_OPEN

RFC contains genuine conserved structures, but they must not be collapsed into one physical carrier without the source-owned cross-binding that RFC itself keeps open.

## Candidate representations

### Temporal current

\[
J_\tau^\mu=\rho_\tau u^\mu,
\qquad
\nabla_\mu J_\tau^\mu=0.
\]

This is an admitted continuous conserved temporal carrier. It is not identified with ordinary matter density.

### Euler–Noether–Berry U(1) current

\[
J_\varphi^\mu
=
i(\psi\partial^\mu\psi^*-\psi^*\partial^\mu\psi)
=
2A^2\partial^\mu\vartheta.
\]

This is a conserved continuous U(1) current. Its identity with the temporal current is open.

### Cyclic phase charge

\[
J=I_\phi D_t\chi+J_0,
\qquad
\dot J=0
\]

on the cyclic-\(\chi\) branch.

This supplies a finite conserved phase charge, but its canonical local-current realization is open.

### IDT normalized profile

\[
p_a,\qquad \sum_a p_a=1.
\]

This can match a normalized carrier *shape*, but normalization erases extensive source scale. It is not a physical total-carrier identification by itself.

## Open cross-bindings

RFC source explicitly retains as candidate/open:

\[
J_\varphi^\mu \leftrightarrow J_\tau^\mu,
\]

\[
J \leftrightarrow \int J_\varphi^0\,dV,
\]

\[
p_{\rm IDT}\leftrightarrow p_Q,
\]

as well as carrier quantum \(q_0\), energy-per-charge \(\epsilon_Q\), and carrier-density to ordinary-matter binding.

Therefore

\[
\boxed{
\text{conserved carrier interface exists}
\not\Rightarrow
\text{unique physical carrier selected}.
}
\]

## Chemistry consequence

A new RFC-induced chemistry term cannot be sourced from a generic symbol "RFC carrier".

It must name:

1. which carrier representation is physical;
2. how that representation is realized on the same system;
3. its local current/measure receipt;
4. its independent action/energy normalization;
5. the operator by which it couples to the chemical Hilbert space.

Until then:

\[
\boxed{
\texttt{selected\_physical\_carrier}=\varnothing.
}
\]

The registry therefore strengthens, rather than bypasses, the existing gate

\[
\texttt{INDEPENDENT\_RFC\_CARRIER\_TO\_CHEMISTRY\_COUPLING}.
\]
