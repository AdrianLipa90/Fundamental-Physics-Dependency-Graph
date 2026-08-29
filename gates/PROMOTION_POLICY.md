# Promotion Policy

This repository records cross-repository dependency state. Source repositories remain authoritative for their own claims, equations, proofs, validators and observables.

## Claim states

`CLOSED`, `PASS`, `PASS_MAIN`, `CROSS_REPO_PASS`, `ACTIVE_FRONTIER`, `OPEN_FRONTIER`, `SOURCE_BOUND_CROSSWALK`, `ACTIVE_RECONCILIATION`, `GREMLIN_CANDIDATE_SEARCH`, and `CANDIDATE_ONLY` are preserved from source evidence where available.

## Canonical edge rule

An edge may be marked `CANONICAL` or `CANONICAL_CROSS_REPO` only when its dependency is stated by the authoritative source repository or supported by a promoted cross-repository validation receipt.

`CANDIDATE_ONLY` edges are excluded from canonical invalidation propagation.

## GREMLIN firewall

GREMLIN is a candidate-generation and relational-isomorphism audit layer.

- runtime execution authority: `false`
- canon write authority: `false`
- default promotion state: `CANDIDATE_ONLY`
- default epistemic state: `CHYBA`

Candidate compilation through `RelationalIsomorphism -> KAKU -> RADICAL -> OPERATORS -> READ_ONLY_PNV` does not promote a claim or dependency edge.

Promotion requires source-side evidence appropriate to the claim: theorem, deterministic validator, exact-head workflow receipt, observable validation, or an explicitly promoted interface contract.

## Invalidation

For every promoted edge `A -> B`, a material change to `A` marks `B` and all reachable promoted descendants as `REVALIDATION_REQUIRED` until their source-side gates pass again.

Candidate-only edges never invalidate canonical descendants unless promoted first.
