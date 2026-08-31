# Fundamental-Physics-Dependency-Graph

Canonical cross-repository dependency surface for the fundamental physics stack.

The active federation is registry-driven through `repos.yaml` and currently spans five source repositories:

- `TIR` — `AdrianLipa90/The-Fundamental-Theory-of-Informational-Relations`
- `IDT` — `AdrianLipa90/Informational-Dynamics-of-Time`
- `RFC` — `AdrianLipa90/Relational-Field-Closure`
- `SOH` — `AdrianLipa90/secret-of-a-half`
- `RC` — `AdrianLipa90/Resonant-Chemistry`

Each source repository remains authoritative for its own equations, derivations, validators, observables, claim status and local dependency edges. FPDG is authoritative for cross-repository dependency edges, typed interface contracts, federation state and downstream revalidation propagation.

## Current baseline

The current baseline is the `v0.4` graph plus effective federation overlays. The executable surface is assembled deterministically as

```text
dependency_graph.yaml
+ federation_overlays/*.graph.yaml
+ claims.jsonl
+ federation_overlays/*.claims.jsonl
+ interfaces/cross_repo_interfaces.yaml
+ federation_overlays/*.interfaces.yaml
```

`tools/federation_surface.py` is the common loader for this effective surface. `tools/validate_dag.py` validates the assembled graph fail-closed, and CI reports the live node/edge/claim counts so the README carries no stale hard-coded topology counts.

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

RFC parallel coupling spine
YM/BCJ -> 4pt DC -> 5pt KLT -> RFG29 -> ... -> RFG34
       -> RFG35 frontier -> physical G -> physical scale/coupling frontier

SOH candidate surfaces
XFI.03 / XFI.28.02 / XFI.28.03 --CANDIDATE_ONLY--> IDT half/NOW interfaces
TIR negative-inverse bridge --CANDIDATE_ONLY--> SOH Li/Weil native closure

Resonant Chemistry nuclear entry
RC.NUCLEON_BOUNDARY --CANONICAL_FRONTIER--> RC.ATOM_FORMALISM
TIR.STANDARD_MODEL --CANDIDATE_ONLY--> RC.NUCLEON_BOUNDARY
                                      promotion gate:
                                      ENDOGENOUS_NUCLEON_PACKET_DERIVATION_AND_VALIDATION
```

The RC nucleon boundary accepts source-bound low-energy proton/neutron packets under explicit provenance and provides the common entry surface for the two-nucleon and nuclear layers. The future endogenous TIR/Standard-Model handoff is represented as a candidate edge and enters promoted propagation only after its named gate passes.

## Canonical files

- `repos.yaml` — registry-driven source repository and authority policy
- `dependency_graph.yaml` — base machine-readable DAG
- `claims.jsonl` — base claim registry
- `interfaces/cross_repo_interfaces.yaml` — base typed cross-repository contracts
- `federation_overlays/` — deterministic first-class federation extensions
- `tools/federation_surface.py` — effective graph/claim/interface loader
- `source_heads.yaml` — scientific source state represented by each export
- `source_exports.lock.json` — exact export commits plus current-main freshness heads
- `gates/PROMOTION_POLICY.md` — promotion, GREMLIN and invalidation rules
- `tools/validate_dag.py` — effective-surface fail-closed validator
- `tools/impact.py` — downstream revalidation impact calculator
- `tools/bootstrap_export.py` — registry-driven source export generator
- `tools/import_exports.py` — source-local surface reconciler
- `tools/fetch_locked_exports.py` — exact commit-addressed export fetcher
- `tools/check_upstream_heads.py` — registered-source main-head freshness gate
- `tools/watch_source_drift.py` — source-main drift and promoted blast-radius projector
- `tools/audit_validation_coverage_effective.py` — effective source-validator nerve-ending audit
- `tools/diagnose_source_drift_effective.py` — effective inconsistency localization entrypoint
- `tools/finalize_inconsistency_localization_effective.py` — effective bottleneck/probe finalizer
- `schemas/dependency_export.schema.json` — source-repository export contract
- `tests/test_federation_surface.py` — federation and candidate propagation invariants
- `tests/test_effective_audit_surface.py` — regression tests for overlay visibility in audit/finalization
- `.github/workflows/validate-dag.yml` — effective DAG/test/coverage/roundtrip gate
- `.github/workflows/validate-source-exports.yml` — registered-source freshness and reconciliation gate
- `.github/workflows/watch-source-drift.yml` — scheduled drift watch and GREMLIN diagnostic receipt pipeline
- `receipts/` — immutable integration and validation receipts

## Operational impact analysis

A changed claim can be projected through promoted downstream dependencies:

```bash
python tools/impact.py IDT.CLOCK.GAMMA_T
python tools/impact.py TIR.TIME_JOIN --json
```

`CANDIDATE_ONLY` edges form an inspection surface and can be included explicitly:

```bash
python tools/impact.py TIR.STANDARD_MODEL --include-candidates
```

Promoted propagation therefore remains distinct from candidate exploration.

## Federated source exports

`schemas/dependency_export.schema.json` defines the source-owned `DEPENDENCY_EXPORT.json` contract for every repository registered in `repos.yaml`. The current federation covers TIR, IDT, RFC, SOH and RC.

The lock records two separate identities per source:

```text
repository_head  = source main HEAD used for freshness
source_commit    = scientific state represented by DEPENDENCY_EXPORT.json
export_commit    = immutable commit containing that exact export
```

The federated gate executes:

```text
current source main == locked repository_head
          ↓
fetch exact DEPENDENCY_EXPORT.json at export_commit
          ↓
verify repository identity + represented source_commit
          ↓
reconcile source claims + local edges against the effective FPDG surface
```

A source-main advance places the federation in drift until semantic export reconciliation, lock refresh and affected downstream validation are complete.

## Source drift watch

The scheduled watcher resolves every repository from `repos.yaml`, checks all registered source `main` heads and calculates promoted downstream blast radius on the effective graph.

Changed source paths are mapped to source-owned claims. Unmapped changes receive the conservative all-owned-claims mapping for that repository. `CANDIDATE_ONLY` edges remain outside promoted invalidation propagation and remain available to explicit candidate inspection.

Drift diagnosis then traverses the same effective federation through the GREMLIN-assisted localization pipeline. GREMLIN contributes bounded candidate/pattern localization; canonical edge authority remains in FPDG and source claim authority remains in the source repositories.

## Nuclear boundary state

The active RC federation extension introduces:

```text
RC.NUCLEON_BOUNDARY
  status: SOURCE_BOUND_EFFECTIVE_INPUT_CONTRACT
  source: THEORY/01_NUCLEON_BOUNDARY_V0_1.md
  source-owned structural/provenance gate: RC PR #20

RC.ATOM_FORMALISM
  status: CANDIDATE_FOUNDATION
```

The direct validation-nerve registry currently binds the RC structural/provenance producer to `RC.NUCLEON_BOUNDARY`. `RC.ATOM_FORMALISM` remains explicitly visible in the validation coverage report as the next direct source-binding target.

The first physical nuclear validation frontier after federation admission is the controlled deuteron path:

```text
freeze proton/neutron provenance packet
-> select one declared NN interaction provider
-> solve p+n -> 2H
-> validate binding energy first
-> validate radius / magnetic / quadrupole observables
-> open A=3 after the deuteron gate
```

## Dependency invariant

For every promoted dependency edge `A -> B`, a material change to `A` places `B` and reachable promoted descendants into `REVALIDATION_REQUIRED` until the appropriate source-side gates pass again.

Candidate edges carry explicit promotion gates and candidate authority. GREMLIN remains a bounded candidate-generation and audit layer.

## Validation

The effective validator checks repository membership, node/claim parity, edge authority typing, candidate promotion gates, cross-repository edge typing, duplicate/self edges, evidence fields and promoted-graph acyclicity.

The source gate independently checks registered main-head freshness, immutable export fetch identity and exact source-local reconciliation. The validation-coverage audit then verifies source-validator bindings against the effective graph, and the drift pipeline performs effective-surface localization through final bottleneck/probe receipts.
