# Fundamental-Physics-Dependency-Graph

Canonical cross-repository dependency surface for the fundamental physics stack.

The active federation is registry-driven through `repos.yaml` and currently spans five source repositories:

- `TIR` — `AdrianLipa90/The-Fundamental-Theory-of-Informational-Relations`
- `IDT` — `AdrianLipa90/Informational-Dynamics-of-Time`
- `RFC` — `AdrianLipa90/Relational-Field-Closure`
- `SOH` — `AdrianLipa90/secret-of-a-half`
- `RC` — `AdrianLipa90/Resonant-Chemistry`

Each source repository remains authoritative for its own equations, proofs, validators, observables, claim status and local dependency edges. This repository is authoritative for cross-repository dependency edges, interface contracts, promotion state and downstream revalidation propagation.

## Current baseline

The current baseline is the canonical graph plus deterministic effective federation overlays:

```text
dependency_graph.yaml
+ federation_overlays/*.graph.yaml
+ claims.jsonl
+ federation_overlays/*.claims.jsonl
+ interfaces/cross_repo_interfaces.yaml
+ federation_overlays/*.interfaces.yaml
```

`tools/federation_surface.py` is the common loader for this effective surface. `tools/validate_dag.py` validates the assembled graph fail-closed; CI reports live topology counts rather than relying on hard-coded README counts.

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

Resonant Chemistry nuclear entry
RC.NUCLEON_BOUNDARY --CANONICAL_FRONTIER--> RC.ATOM_FORMALISM
TIR.STANDARD_MODEL --CANDIDATE_ONLY--> RC.NUCLEON_BOUNDARY
                                      promotion gate:
                                      ENDOGENOUS_NUCLEON_PACKET_DERIVATION_AND_VALIDATION
```

The relativistic IDT↔RFC bridge is anchored to the hardened `IDT-01AC -> IDT-01AG -> RF-M1 -> RF-E0 -> EINSTEIN_CLOSURE` chain. It remains distinct from the RFC ADM `E8 -> ... -> E13` action-level spine and from the later E14–E20 information/clock branch.

RF-E20 keeps its physical SI edge scale and dimensionless tetrahedral selector explicit. The TIR tetrahedron edge supplies the geometric carrier dependency; it does not by itself promote the physical scale/coupling frontier.

## Canonical files

- `repos.yaml` — repository registry and authority policy
- `dependency_graph.yaml` — machine-readable canonical DAG
- `claims.jsonl` — claim registry with source/evidence provenance
- `interfaces/cross_repo_interfaces.yaml` — typed cross-repository contracts
- `federation_overlays/` — deterministic first-class federation extensions
- `tools/federation_surface.py` — effective graph/claim/interface loader
- `source_heads.yaml` — scientific source state represented by each export
- `source_exports.lock.json` — exact immutable source-export snapshot lock plus repository-head freshness state
- `gates/PROMOTION_POLICY.md` — promotion, GREMLIN and invalidation rules
- `tools/validate_dag.py` — fail-closed structural validator
- `tools/impact.py` — downstream revalidation impact calculator
- `tools/bootstrap_export.py` — migration/bootstrap source export generator
- `tools/import_exports.py` — source-local surface reconciler
- `tools/fetch_locked_exports.py` — exact commit-addressed export fetcher
- `tools/check_upstream_heads.py` — upstream source freshness gate
- `tools/watch_source_drift.py` — source-main drift and promoted blast-radius projector
- `tools/audit_validation_coverage_effective.py` — effective source-validator nerve-ending audit
- `tools/diagnose_source_drift_effective.py` — effective inconsistency localization entrypoint
- `tools/finalize_inconsistency_localization_effective.py` — effective bottleneck/probe finalizer
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

`schemas/dependency_export.schema.json` defines the source-owned `DEPENDENCY_EXPORT.json` contract for every repository registered in `repos.yaml`. The active federation covers TIR, IDT, RFC, SOH and RC. Each export identifies its repository, exact source commit, claim statuses, evidence classes and local dependency edges.

`source_exports.lock.json` deliberately separates three coordinates for each source: `repository_head` is the repository-level freshness coordinate, `export_commit` is the immutable commit from which `DEPENDENCY_EXPORT.json` is fetched, and `source_commit` is the scientific source state represented by that export. FPDG CI therefore performs independent freshness and scientific-surface gates:

```text
source main head == locked repository_head
          ↓
fetch exact DEPENDENCY_EXPORT.json at export_commit
          ↓
verify the export's represented scientific source_commit
          ↓
reconcile source claims + local edges against canonical FPDG local surface
```

A source-main advance always fails the freshness gate first. After semantic export-diff review, a repository-only advance with an identical represented dependency surface is repaired by refreshing `repository_head` and revalidating the locked export. If the scientific dependency surface changed, the source export, represented `source_commit`, FPDG lock and affected downstream dependency surface must instead be reconciled together. This is the fail-closed cross-repository holonomy rule.

## 2026-09-19 reconciliation snapshot

The current reconciliation branch locks exact source-owned dependency exports representing these source-main scientific states:

```text
TIR  source bc22bf7dc9e02b912656e2f229a8efee39c2bbc9  export 1b7bad9c04e0046a130a2bf041e43f1d189d97ec
IDT  source 58f453a4725bf0304417a5d07730f2dc1765dea5  export 7d3899780da5cec5356b9ba0a61844732955c758
RFC  source ce4af9ddd480ea40dfb5a3ee26ed396a58cb0e54  export 9e7c35dbeec6c0e51ff85ed9a4dcbb298a88b30d
SOH  source d99545aa447ef86bc253d8241a3fee9adb8a42c1  export e84eff6988f333154995caf20de3e824029d377d
RC   source 48414e0e76777d82974dd12d581b5d9598f80c27  export 71d7e75f2ae9c050b0e7d57fcafd715a0c11a719
```

The graph now includes the TIR representation/flavour frontier, IDT 05I/GSC2/05K clock-globalization surfaces, RFC E26/E27 and GSC3--GSC6 globalization routes, and the SOH G024/G025 research frontier. Physical flavour binding, production global spacetime inputs, physical scale/coupling, and RH-level positivity remain explicitly open.

## Physical-realization source-bundle frontier — 2026-09-19

TIR already contains an executable v0.2 source-bundle certifier that composes the global spatial capture and inter-leaf matching capture only when both identify the same source-declared physical realization and receipt. FPDG now routes the production GSC3A handoff through this bundle gate rather than treating the abstract matching-input contract alone as sufficient.

The assembler is closed. The remaining source evidence is open: a production spatial capture and a production matching capture for one physical realization are not present in the source repository.

## Source drift watch

The scheduled watcher resolves every repository from `repos.yaml`, checks all registered source `main` heads every 30 minutes and can also be run manually. When a source has advanced, changed source paths are mapped to owned claims and the promoted downstream blast radius is calculated.

If changed paths cannot be mapped to known claims, the watcher falls back conservatively to every claim owned by the changed repository. `CANDIDATE_ONLY` edges remain excluded from canonical invalidation.

Every watch produces JSON and Markdown receipts. A drifted source fails the watch until the source export, lock and dependency surface are reconciled.

## Nuclear boundary state

The active RC federation extension introduces:

```text
RC.NUCLEON_BOUNDARY
  status: SOURCE_BOUND_EFFECTIVE_INPUT_CONTRACT
  source: THEORY/01_NUCLEON_BOUNDARY_V0_1.md

RC.ATOM_FORMALISM
  status: CANDIDATE_FOUNDATION
```

The direct validation-nerve registry binds the RC structural/provenance producer to `RC.NUCLEON_BOUNDARY`. `RC.ATOM_FORMALISM` remains visible as the next direct source-binding target.

The first nuclear validation frontier after federation admission is the controlled deuteron path:

```text
freeze proton/neutron provenance packet
-> select one declared NN interaction provider
-> solve p+n -> 2H
-> validate binding energy first
-> validate radius / magnetic / quadrupole observables
-> open A=3 after the deuteron gate
```

## Dependency invariant

For every promoted dependency edge `A -> B`, a material change to `A` places `B` and all reachable promoted descendants into `REVALIDATION_REQUIRED` until the appropriate source-side gates pass again.

`CANDIDATE_ONLY` edges do not propagate canonical invalidation. GREMLIN remains a candidate-generation and audit layer; candidate compilation does not itself promote a claim.

## Validation

The canonical validator checks repository membership, node/claim parity, edge authority typing, candidate promotion gates, cross-repository edge typing, duplicate/self edges, evidence fields and acyclicity of the promoted graph.

The federated gate additionally checks current upstream main heads, fetches immutable source exports, verifies repository/source identity and reconciles all registered source-local surfaces exactly against the effective FPDG graph.


## Resonant Chemistry federation

The effective federation includes `RC.NUCLEON_BOUNDARY` and `RC.ATOM_FORMALISM` through first-class federation overlays. The source-bound nucleon boundary is the canonical RC entry surface. The future `TIR.STANDARD_MODEL -> RC.NUCLEON_BOUNDARY` handoff remains `CANDIDATE_ONLY` behind `ENDOGENOUS_NUCLEON_PACKET_DERIVATION_AND_VALIDATION`.

The RC dependency export represents scientific source commit `48414e0e76777d82974dd12d581b5d9598f80c27`; repository freshness is tracked independently against current RC `main`.
