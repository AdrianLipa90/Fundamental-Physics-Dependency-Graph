# GREMLIN Inconsistency Localization v0.4

Status: `EXACT_COORDINATE_LOCALIZATION + DETERMINISTIC_PROBE_ORDER + REVIEWED_INCIDENT_MEMORY`

The detector now answers two different questions separately:

```text
WHERE is the inconsistency observed?
  -> claim frontier
  -> dependency/interface seam
  -> source/receipt/validator/symbol/equation/line coordinate

WHAT should be inspected first?
  -> deterministic probe plan
```

The second question is deliberately not answered with a causal probability. The planner orders coordinates by evidential specificity and graph position.

## Deterministic probe order

`tools/build_diagnostic_probe_plan.py` emits `FPDG_DIAGNOSTIC_PROBE_PLAN_V0_1`.

For a claim-level zone the default order is:

```text
1. directly observed micro-coordinate
   SOURCE_RANGE > EQUATION > SYMBOL > VALIDATOR/TEST > RECEIPT > INTERFACE > SOURCE_PATH > CLAIM

2. promoted seam entering the localized frontier

3. localized frontier claim source

4. promoted seam carrying the failure toward downstream symptoms

5. GREMLIN historical recurrence hints
   CANDIDATE_ONLY, never promoted above current deterministic evidence
```

An integration-only inconsistency such as a stale FPDG source-head lock remains at the exact integration coordinate and is not projected onto scientific claims.

The emitted `first_probe` is therefore the smallest deterministic inspection coordinate justified by the current evidence. It is not an assertion that the coordinate is the ultimate physical cause.

## Automated source-drift pipeline

The scheduled watcher now runs:

```text
source-head drift
  -> semantic DEPENDENCY_EXPORT diff
  -> minimal promoted claim frontier
  -> exact cross-repository/local seam localization
  -> sub-claim evidence coordinate localization
  -> repository-agnostic structural signature
  -> reviewed incident retrieval
  -> deterministic probe plan
  -> GREMLIN packet enriched with micro-coordinates + probe plan
```

The job summary and artifact bundle contain the exact diagnosis, seam map, sub-claim coordinate map and ordered probe plan.

## Reviewed incident memory hardening

Historical incident signatures are not trusted by filename alone. Before matching, FPDG recomputes:

```text
SHA-256(canonical structural_signature)
feature_tokens(structural_signature)
```

Both must equal the stored values. Any mismatch fails closed.

`tools/record_reviewed_incident.py` is the only supported append-only promotion path for CI output into the durable GREMLIN incident bank. It requires an explicit incident id and reviewer, validates the candidate-only GREMLIN authority boundary, stores the exact packet SHA-256 and refuses overwrite.

## GREMLIN authority

GREMLIN receives:

```text
exact current witness chains
exact interface seams
exact source coordinates
ordered deterministic probes
reviewed structural recurrence candidates
```

It may use those surfaces to search for relational recurrence and candidate repair patterns. It still cannot choose the canonical failing frontier, fabricate KAKU mappings, invent 36D vectors, promote a dependency edge, or write scientific canon.

The PNCS ingress remains:

```text
explicit claim_id -> grammar atom mapping
+ explicit cross-domain positional alignment
+ canonical KAKU resolver
+ one exact 36D basis
-> RelationalIsomorphism
-> RADICAL
-> native PNV OPERATORS
-> READ_ONLY candidate program
```

The PNCS ingress implementation is currently proposed on PR #54. Its code-level contract is wired, but its hosted GitHub Actions runs have so far terminated before any job step was executed, so FPDG does not treat those hosted runs as validator evidence yet.

All GREMLIN-derived explanation candidates remain `CHYBA / CANDIDATE_ONLY` until source-side validation and promotion gates pass.
