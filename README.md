# Fundamental-Physics-Dependency-Graph

Canonical cross-repository dependency surface for the fundamental physics stack.

This repository tracks dependency holonomy across four source repositories:

- `TIR` — `AdrianLipa90/The-Fundamental-Theory-of-Informational-Relations`
- `IDT` — `AdrianLipa90/Informational-Dynamics-of-Time`
- `RFC` — `AdrianLipa90/Relational-Field-Closure`
- `SOH` — `AdrianLipa90/secret-of-a-half`

Each source repository remains authoritative for its own equations, proofs, validators, observables, claim status and local dependency edges. This repository is authoritative for cross-repository dependency edges, interface contracts, promotion state and downstream revalidation propagation.

## Current baseline

`v0.3` is a claim-level executable federated dependency kernel:

```text
82 claims / 91 dependency edges
11 cross-repository edges
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
  |-> gauge-covariant Noether source
  |    -> RFC conserved source / RF-M1/RF-E0 bridge surface
  |         -> IDT relativistic bridge -> Einstein Closure
  |
  +-> IDT 05D local-clock relative entropy
       -> RFC E14 directional relative-information potential
            -> E15 Legendre audit -> E17 scalar-action potential
                                      -> E18 physical-velocity firewall
                                           -> E19 Noether material congruence
                                                -> E20 tetra-clock mass-scale closure

RFC ADM action spine
RFC matter / Lorentzian / information-curvature
  -> L5/L5A
  -> [IDT Gamma_t + TIR spatial carrier]
  -> E8 -> E9 -> E10 -> E11 -> E12 -> E13
                                  |
                                  +-> physical scale/coupling frontier

RFC post-E13 information/clock branch
E8 + IDT 05D -> E14 -> E15 -> E17
E8 + current carrier -> E16 -> E18
E17 + E16 + E8 -> E18 -> E19
current/measure carrier -> E19
E17 + E19 + TIR tetrahedron -> E20 -> physical scale/coupling frontier

RFC parallel coupling spine
YM/BCJ -> 4pt DC -> 5pt KLT -> RFG29 -> ... -> RFG34
       -> RFG35 frontier -> physical G -> physical scale/coupling frontier

SOH candidate surfaces
XFI.03 / XFI.28.02 / XFI.28.03 --CANDIDATE_ONLY--> IDT half/NOW interfaces
TIR negative-inverse bridge --CANDIDATE_ONLY--> SOH Li/Weil native closure
```

The relativistic IDT↔RFC bridge is anchored to the hardened `IDT-01AC -> IDT-01AG -> RF-M1 -> RF-E0 -> EINSTEIN_CLOSURE` chain. It remains distinct from the RFC ADM `E8 -> ... -> E13` action-level spine and from the later E14–E20 information/clock branch.

RF-E20 keeps its physical SI edge scale and dimensionless tetrahedral selector explicit. The TIR tetrahedron edge supplies the geometric carrier dependency; it does not by itself promote the physical scale/coupling frontier.

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
- `tools/watch_source_drift.py` — source-main drift and promoted blast-radius projector
- `schemas/dependency_export.schema.json` — source-repository export contract
- `tests/test_impact.py` — executable propagation invariants
- `tests/test_source_drift.py` — fail-closed source-drift mapping tests
- `.github/workflows/validate-dag.yml` — canonical DAG CI gate
- `.github/workflows/validate-source-exports.yml` — federated source freshness/reconciliation gate
- `.github/workflows/watch-source-drift.yml` — scheduled source-drift watch and receipt generation
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

The source-owned export PRs currently used by the lock are:

```text
TIR  PR #107
IDT  PR #69
RFC  PR #67   post-E13 RF-E14–RF-E20 sync
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

## Source drift watch

The scheduled watcher checks the four source `main` heads every 30 minutes and can also be run manually. When a source has advanced, changed source paths are mapped to owned claims and the promoted downstream blast radius is calculated.

If changed paths cannot be mapped to known claims, the watcher falls back conservatively to every claim owned by the changed repository. `CANDIDATE_ONLY` edges remain excluded from canonical invalidation.

Every watch produces JSON and Markdown receipts. A drifted source fails the watch until the source export, lock and dependency surface are reconciled.

## Dependency invariant

For every promoted dependency edge `A -> B`, a material change to `A` places `B` and all reachable promoted descendants into `REVALIDATION_REQUIRED` until the appropriate source-side gates pass again.

`CANDIDATE_ONLY` edges do not propagate canonical invalidation. GREMLIN remains a candidate-generation and audit layer; candidate compilation does not itself promote a claim.

## Validation

The canonical validator checks repository membership, node/claim parity, edge authority typing, candidate promotion gates, cross-repository edge typing, duplicate/self edges, evidence fields and acyclicity of the promoted graph.

The federated gate additionally checks current upstream main heads, fetches immutable source exports, verifies repository/source identity and reconciles all four source-local surfaces exactly against the FPDG graph.
