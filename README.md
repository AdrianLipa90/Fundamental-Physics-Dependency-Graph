# Fundamental-Physics-Dependency-Graph

Canonical cross-repository dependency surface for the fundamental physics stack.

This repository tracks dependency holonomy across four source repositories:

- `TIR` — `AdrianLipa90/The-Fundamental-Theory-of-Informational-Relations`
- `IDT` — `AdrianLipa90/Informational-Dynamics-of-Time`
- `RFC` — `AdrianLipa90/Relational-Field-Closure`
- `SOH` — `AdrianLipa90/secret-of-a-half`

Each source repository remains authoritative for its own equations, proofs, validators, observables and claim status. This repository is authoritative for cross-repository dependency edges, interface contracts, promotion state and downstream revalidation propagation.

## Current baseline

`v0.2` expands the bootstrap graph to a claim-level baseline:

```text
74 claims / 74 dependency edges
9 cross-repository edges
4 CANDIDATE_ONLY edges
```

The promoted graph is acyclic and validated fail-closed by `tools/validate_dag.py`.

## Top-level dependency structure

```text
TIR primitive spine
0 -> P -> FIRST DISTINCTION -> {N,S} -> 1/2 -> ln2 -> C^2
                                   |
                                   +-> kappa
                                   |
                                   +-> local spatial geometry -> R^3
                                                        |       |
                                                        |       +-> Pythagorean branch
                                                        +-> tetrahedron -> W_ij
                                                                          |-> gluing/torsion frontier
                                                                          +-> Standard Model

TIR.TIME_JOIN
  -> IDT Temporal Primitive
      -> Temporal Wave -> NOW -> Bifurcation -> Transport
      -> Memory -> ORCHORBITAL -> Retrodiction -> Retrocausal Tests
      -> Einstein Closure

IDT Temporal Primitive
  -> gauge-covariant Noether source
  -> RFC conserved source / matter / Lorentzian / information-curvature spine
  -> RFC L5/L5A
  -> [IDT Gamma_t + TIR spatial carrier]
  -> RFC E8 -> E9 -> E10 -> E11 -> E12 -> E13
       |                                  |
       |                                  +-> physical scale/coupling frontier
       +------------------------------------> IDT relativistic bridge -> Einstein Closure

RFC parallel coupling spine
YM/BCJ -> 4pt DC -> 5pt KLT -> RFG29 -> ... -> RFG34
       -> RFG35 frontier -> physical G -> physical scale/coupling frontier

SOH candidate surfaces
XFI.03 / XFI.28.02 / XFI.28.03 --CANDIDATE_ONLY--> IDT half/NOW interfaces
TIR negative-inverse bridge --CANDIDATE_ONLY--> SOH Li/Weil native closure
```

## Canonical files

- `repos.yaml` — repository registry and authority policy
- `dependency_graph.yaml` — machine-readable canonical DAG
- `claims.jsonl` — claim registry with source/evidence provenance
- `interfaces/cross_repo_interfaces.yaml` — typed cross-repository contracts
- `gates/PROMOTION_POLICY.md` — promotion, GREMLIN and invalidation rules
- `tools/validate_dag.py` — fail-closed structural validator
- `.github/workflows/validate-dag.yml` — CI gate
- `receipts/` — immutable integration and validation receipts

## Dependency invariant

For every promoted dependency edge `A -> B`, a material change to `A` places `B` and all reachable promoted descendants into `REVALIDATION_REQUIRED` until the appropriate source-side gates pass again.

`CANDIDATE_ONLY` edges do not propagate canonical invalidation. GREMLIN remains a candidate-generation and audit layer; candidate compilation does not itself promote a claim.

## Validation

The validator checks repository membership, node/claim parity, edge authority typing, candidate promotion gates, cross-repository edge typing, duplicate/self edges, evidence fields and acyclicity of the promoted graph.
