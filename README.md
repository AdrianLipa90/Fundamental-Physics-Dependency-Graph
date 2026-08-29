# Fundamental-Physics-Dependency-Graph

Canonical cross-repository dependency surface for the fundamental physics stack.

This repository tracks dependency holonomy across four source repositories:

- `TIR` — `AdrianLipa90/The-Fundamental-Theory-of-Informational-Relations`
- `IDT` — `AdrianLipa90/Informational-Dynamics-of-Time`
- `RFC` — `AdrianLipa90/Relational-Field-Closure`
- `SOH` — `AdrianLipa90/secret-of-a-half`

Each source repository remains authoritative for its own equations, proofs, validators, observables and claim status. This repository is authoritative for the cross-repository dependency graph, interface contracts and downstream revalidation propagation.

## Current top-level DAG

```text
TIR foundational / spatial spine
        |
        | spatial carrier
        v
IDT temporal / clock spine -----> RFC ADM / field spine -----> physical scale + coupling frontier
        |                              |
        |                              +----> GR closure path
        |
        +---- Gamma_t -----------------+

TIR W_ij / gauge spine ----------> Standard-Model reconciliation / RG frontier

SOH half / analytic branch --candidate crosslinks--> TIR / IDT interfaces
```

The current RFC action-level ADM spine is represented through `RF-E8 -> RF-E9 -> RF-E10 -> RF-E11 -> RF-E12 -> RF-E13`, with the physical carrier/scale/coupling layer downstream.

## Canonical files

- `repos.yaml` — repository registry and authority policy
- `dependency_graph.yaml` — machine-readable canonical DAG
- `claims.jsonl` — claim registry with source/evidence provenance
- `interfaces/cross_repo_interfaces.yaml` — typed cross-repository contracts
- `gates/PROMOTION_POLICY.md` — promotion, GREMLIN and invalidation rules
- `tools/validate_dag.py` — fail-closed structural validator
- `.github/workflows/validate-dag.yml` — CI gate

## Dependency invariant

For every promoted dependency edge

```text
A -> B
```

a material change to `A` places `B` and all reachable promoted descendants into `REVALIDATION_REQUIRED` until the appropriate source-side gates pass again.

GREMLIN candidate edges remain `CANDIDATE_ONLY / CHYBA` until their explicit promotion gates are satisfied.

## Bootstrap state

Version `v0.1` establishes the four-repository registry, the first canonical cross-repository DAG, exact RFC ADM validation provenance through RF-E13, the promoted IDT temporal-clock interface, candidate isolation for SOH/GREMLIN crosslinks, and CI structural validation.
