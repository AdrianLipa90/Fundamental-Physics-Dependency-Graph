# Fundamental-Physics-Dependency-Graph

Canonical cross-repository dependency surface for the fundamental physics stack.

This repository tracks dependency holonomy across four source repositories:

- `TIR` — `AdrianLipa90/The-Fundamental-Theory-of-Informational-Relations`
- `IDT` — `AdrianLipa90/Informational-Dynamics-of-Time`
- `RFC` — `AdrianLipa90/Relational-Field-Closure`
- `SOH` — `AdrianLipa90/secret-of-a-half`

Each source repository remains authoritative for its own equations, proofs, validators, observables, claim status and local dependency edges. This repository is authoritative for cross-repository dependency edges, interface contracts, promotion state and downstream revalidation propagation.

## Current baseline

`v0.2` expands the bootstrap graph to a claim-level executable dependency kernel:

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
  -> RFC conserved source / RF-M1/RF-E0 bridge surface
       |-> IDT relativistic bridge -> Einstein Closure
       +-> RFC matter / Lorentzian / information-curvature spine
            -> RFC L5/L5A
            -> [IDT Gamma_t + TIR spatial carrier]
            -> RFC E8 -> E9 -> E10 -> E11 -> E12 -> E13
                                             |
                                             +-> physical scale/coupling frontier

RFC parallel coupling spine
YM/BCJ -> 4pt DC -> 5pt KLT -> RFG29 -> ... -> RFG34
       -> RFG35 frontier -> physical G -> physical scale/coupling frontier

SOH candidate surfaces
XFI.03 / XFI.28.02 / XFI.28.03 --CANDIDATE_ONLY--> IDT half/NOW interfaces
TIR negative-inverse bridge --CANDIDATE_ONLY--> SOH Li/Weil native closure
```

The relativistic IDT↔RFC bridge is anchored to the hardened `IDT-01AC -> IDT-01AG -> RF-M1 -> RF-E0 -> EINSTEIN_CLOSURE` chain. It is kept distinct from the later RFC ADM `E8 -> ... -> E13` action-level spine.

## Canonical files

- `repos.yaml` — repository registry and authority policy
- `dependency_graph.yaml` — machine-readable canonical DAG
- `claims.jsonl` — claim registry with source/evidence provenance
- `interfaces/cross_repo_interfaces.yaml` — typed cross-repository contracts
- `source_exports.lock.json` — exact immutable source-export snapshot lock
- `gates/PROMOTION_POLICY.md` — promotion, GREMLIN and invalidation rules
- `tools/validate_dag.py` — fail-closed structural validator
- `tools/impact.py` — downstream revalidation impact calculator
- `tools/bootstrap_export.py` — migration/bootstrap source export generator
- `tools/import_exports.py` — source-local surface reconciler
- `tools/fetch_locked_exports.py` — exact commit-addressed export fetcher
- `tools/check_upstream_heads.py` — upstream source freshness gate
- `schemas/dependency_export.schema.json` — source-repository export contract
- `tests/test_impact.py` — executable propagation invariants
- `.github/workflows/validate-dag.yml` — canonical DAG CI gate
- `.github/workflows/validate-source-exports.yml` — federated source freshness/reconciliation gate
- `receipts/` — immutable integration and validation receipts

## Operational impact analysis

A changed claim can be projected through all promoted downstream dependencies:

```bash
python tools/impact.py IDT.CLOCK.GAMMA_T
python tools/impact.py TIR.TIME_JOIN --json
```

By default `CANDIDATE_ONLY` edges are excluded. They can be inspected explicitly without promoting them:

```bash
python tools/impact.py SOH.SU2.DOUBLE_COVER --include-candidates
```

This makes `REVALIDATION_REQUIRED` propagation executable instead of merely documentary.

## Federated source exports

`schemas/dependency_export.schema.json` defines `DEPENDENCY_EXPORT.json` for TIR, IDT, RFC and SOH. Each export identifies its repository, exact source commit, claim statuses, evidence classes and local dependency edges.

The first source-owned exports are staged on dedicated PRs:

```text
TIR  PR #107
IDT  PR #69
RFC  PR #64
SOH  PR #69
```

`source_exports.lock.json` pins the exact export commit and the exact source commit represented by that export. FPDG CI then performs three independent gates:

```text
source main head == locked source_commit
          ↓
fetch exact DEPENDENCY_EXPORT.json at export_commit
          ↓
reconcile source claims + local edges against canonical FPDG local surface
```

A source-main advance therefore fails the freshness gate until its export, FPDG lock and affected downstream dependency surface are reconciled. This is the fail-closed cross-repository holonomy rule.

## Dependency invariant

For every promoted dependency edge `A -> B`, a material change to `A` places `B` and all reachable promoted descendants into `REVALIDATION_REQUIRED` until the appropriate source-side gates pass again.

`CANDIDATE_ONLY` edges do not propagate canonical invalidation. GREMLIN remains a candidate-generation and audit layer; candidate compilation does not itself promote a claim.

## Validation

The canonical validator checks repository membership, node/claim parity, edge authority typing, candidate promotion gates, cross-repository edge typing, duplicate/self edges, evidence fields and acyclicity of the promoted graph.

The federated gate additionally checks current upstream main heads, fetches immutable source exports, verifies repository/source identity and reconciles all four source-local surfaces exactly against the FPDG graph.
