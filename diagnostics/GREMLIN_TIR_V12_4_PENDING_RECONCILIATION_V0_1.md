# GREMLIN / FPDG — TIR v12.4 Reconciliation

Status: `SOURCE_PROMOTED_RECONCILIATION_APPLIED_TO_PR_BRANCH / CANON_ALLOWED_FALSE`

TIR PR #177 and #178 are merged. This branch now consumes the authoritative TIR `DEPENDENCY_EXPORT.json` from current source main rather than staging a hypothetical delta.

## Reconciled source surface

- TIR repository head: `6bb61fdc8b3f77deba406fe2cb8b154723269e0e`
- represented scientific source commit: `8c781742b656871529a4783ce977c8c1b8d51de2`
- source-owned claims: **67**
- source-owned local edges: **94**
- White-Thread spin-lift and Lyapunov claims are present in the export.

## Authority repair

The old FPDG base classified

`TIR.FOUNDATION.HALF -> TIR.SPACETIME.SP3_DELTA_HERM2_HALF_LIFT_V01`

as `CANONICAL`. The authoritative TIR export classifies it as `CANDIDATE_ONLY` behind `GLOBAL_PHYSICAL_SPATIAL_CARRIER_BINDING_REQUIRED`. This branch now follows the source authority.

## Schema repair

`RC` is already the fifth registered federation source and is accepted dynamically by `tools/import_exports.py`. The static JSON export schema was stale and is synchronized to include `RC`.

## Promotion discipline

This PR branch remains unmerged. Validation must pass for DAG structure, locked source export reconciliation, upstream-head freshness and source-drift impact before any merge decision.
