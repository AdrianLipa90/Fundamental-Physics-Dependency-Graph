# GREMLIN / FPDG — TIR v12.4 Pending Reconciliation

Status: `STAGED_PENDING_SOURCE_PROMOTION / CANON_ALLOWED_FALSE`

This staging record exists to prevent the global graph from being updated ahead of its source authority.

## What GREMLIN found

The TIR source surface on current `main` contains materially more theorem/validator structure than the locked/global dependency representation exposes. TIR PR #178 packages the reconciliation from 35 to 58 source-owned claims and from 40 to 81 local edges.

The important semantic repairs are:

- hypercharge relative uniqueness: derivationally closed on the declared field content and TIR normalization anchor;
- neutrino absolute-action source repair: derivationally closed, physical absolute mass still open;
- coefficient selector no-go: closed diagnostic, transition-sensitive selector still open;
- local RFC ADM/Einstein derivation: closed, global production realization remains open;
- legacy empirical FAIL receipts: retained for their frozen formulas, not exported as automatic verdicts on replacement constructions;
- 600-cell/McKay-E8: exact representation mathematics where stated, still CANDIDATE_ONLY physically.

## Why the canonical FPDG is not changed yet

FPDG policy makes the source repository authoritative for its own claims and local edges. TIR PR #178 is not on source `main` yet. Changing `dependency_graph.yaml`, `claims.jsonl` or the TIR source lock now would correctly trigger source-export drift/failure.

So this branch intentionally changes only diagnostic/staging material.

## White-Thread ordering

TIR PR #177 is independently green and adds the new White-Thread spin-lift/Lyapunov layer. The lowest-churn promotion order is:

```text
PR #177
  -> refresh PR #178 against the new TIR main
  -> include White-Thread claims/edges in final TIR export
  -> merge PR #178
  -> refresh FPDG lock + global graph
  -> run global GREMLIN impact analysis
```

If #178 is merged before #177, nothing is invalid, but another TIR export refresh is required after #177.

## Global target shape after source promotion

At minimum the global graph should be able to distinguish:

```text
TIR formal closure
  != TIR physical binding
  != frozen empirical verdict

HYPERCHARGE relative theorem       CLOSED
NEUTRINO source repair             CLOSED_DERIVATION
COEFFICIENT selector no-go         CLOSED_DIAGNOSTIC
COEFFICIENT transition selector    OPEN
GAUGE continuum normalization      OPEN
ELECTROWEAK R_EW                   OPEN
HIGGS action binding               OPEN
MESON absolute action              OPEN
STRONG_CP holonomic source         OPEN
COSMOLOGY scale/rho_crit           OPEN
```

Candidate-only Platonic/600-cell/semantic bridges remain excluded from canonical invalidation propagation until their explicit promotion gates pass.
