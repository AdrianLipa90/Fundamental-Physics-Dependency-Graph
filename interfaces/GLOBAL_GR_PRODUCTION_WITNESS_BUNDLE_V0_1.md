# Global GR Production Witness Bundle v0.1

Status: `PROOF_CARRYING_INTEGRATION_CONTRACT / SOURCE_RECEIPT_DIGEST_BINDING / REFERENCE_CONTROL_PROMOTION_FIREWALL / PRODUCTION_WITNESSES_OPEN`

Date: 2026-08-31

Authority: `FPDG_INTEGRATION_ONLY`. TIR, IDT and RFC remain authoritative for their own GSC receipts. This contract has `promotion_authority=false` over source claims.

## 1. Purpose

The GSC-1 through GSC-6 theorem/certifier layer is now explicit and hosted-validated. The remaining global-relativity frontier is the supply of one real, common spacetime realization that passes all six source-owned gates.

This contract defines the proof-carrying bundle used to demonstrate that those production receipts belong to one realization rather than six unrelated successful controls.

It consumes already-produced source receipts. It does not manufacture TIR incidence data, IDT event histories, RFC atlases, global lapse bounds or completeness proofs.

## 2. Required bundle identity

Every bundle carries one

```text
bundle_id
target_domain_id
lineage_id
production
evidence_class
```

The six GSC receipts and the three explicit global witnesses must repeat the same `target_domain_id` and `lineage_id`.

For a production candidate:

```text
production = true
evidence_class = PRODUCTION
```

For the repository reference fixture:

```text
production = false
evidence_class = REFERENCE_CONTROL
```

`SYNTHETIC`, `FIXTURE`, or any untyped evidence class is rejected by the validator.

## 3. Six source-owned gate receipts

The exact required source owners and production verdicts are:

| Gate | Source owner | Required production verdict |
|---|---|---|
| `GSC-1` | TIR | `PASS_PRODUCTION_3_MANIFOLD` |
| `GSC-2` | IDT | `PASS_PRODUCTION_EXACT_EVENT_CLOCK` |
| `GSC-3` | IDT | `PASS_REGULAR_CLOCK_EXTENSION` |
| `GSC-4` | RFC | `PASS_SHARED_SPACETIME_REALIZATION` |
| `GSC-5` | RFC | `PASS_GLOBAL_EINSTEIN_REALIZATION` |
| `GSC-6` | RFC | `PASS_GLOBAL_CAUCHY_HYPERBOLICITY` |

Each entry carries:

- exact source repository;
- exact 40-hex source commit;
- SHA-256 of the source-owned receipt;
- common lineage and target-domain IDs;
- its own production/evidence-class flags;
- required and observed verdicts.

A production bundle passes this layer only when `observed_verdict == required_verdict` for all six gates.

The reference fixture instead uses `REFERENCE_CONTROL_PASS` and is permanently non-promotable.

## 4. Digest-bound dependency holonomy

GSC-5 must bind the exact supplied receipt digests of

```text
GSC-1
GSC-2
GSC-3
GSC-4
```

and GSC-6 must bind the exact supplied receipt digests of

```text
GSC-3
GSC-4
GSC-5
```

Thus a downstream PASS cannot be combined with a different upstream realization by changing labels alone.

The validator also rejects receipt-digest collisions between gates and global witnesses.

## 5. Explicit global witnesses

Three proof objects remain outside the six gate-receipt identities and are therefore carried explicitly:

### 5.1 Target-domain coverage

RF-E26 requires a witness that the supplied atlas covers the declared target domain.

Required coordinate:

```text
covers_target_domain = true
```

### 5.2 Global lapse upper bound

RF-L8 requires one source-owned globally certified finite bound

\[
0<N(x)\le N_{\max}<\infty
\qquad \forall x\in M.
\]

The bundle therefore carries

```text
n_max > 0
globally_certified = true
```

with its own receipt digest.

### 5.3 ADM Wick completeness

RF-L8 additionally requires an analytic/topological witness that

\[
W=dt^2+h_{ij}(dx^i+b^i dt)(dx^j+b^j dt)
\]

is complete on the target domain.

The bundle carries

```text
complete = true
```

with its own production receipt digest.

No finite sample or reference fixture is accepted as a completeness promotion by this integration contract.

## 6. Promotion semantics

The validator returns two separate states.

### Structural pass

`structural_pass=true` means the bundle is internally coherent:

- all six gate coordinates exist;
- source repositories and required verdict labels are exact;
- hashes are well formed and non-colliding;
- lineage/domain IDs agree;
- GSC-5/GSC-6 dependency hashes bind the supplied parents;
- coverage, lapse-bound and Wick-completeness witness fields are structurally valid.

### Production promotion eligibility

`production_promotable=true` is possible only when the entire bundle is explicitly production-class.

The final integration coordinate

```text
global_gr_cauchy_carrier_eligible
```

is equal to that production-promotable state. It is an FPDG admission coordinate only. Source repositories retain claim/promotion authority for the underlying receipts.

## 7. Reference fixture

Reference input:

`fixtures/global_gr_production_witness_bundle_reference_v0_1.json`

It intentionally has

```text
production=false
evidence_class=REFERENCE_CONTROL
```

and therefore must return

```text
structural_pass=true
production_promotable=false
global_gr_cauchy_carrier_eligible=false
```

The fixture validates the contract shape and dependency holonomy. It cannot serve as a production GR realization.

## 8. Fail-closed conditions

The bundle is rejected if any of the following occurs:

1. a GSC coordinate is missing or duplicated by an extra coordinate;
2. a gate names the wrong source repository;
3. a source commit or receipt digest is malformed;
4. two gate/witness receipts reuse the same digest;
5. lineage IDs differ;
6. target-domain IDs differ;
7. production flags are mixed;
8. evidence classes are mixed or untyped;
9. a production observed verdict differs from its required source verdict;
10. a reference-control observed verdict is presented as a production verdict;
11. a GSC-5 or GSC-6 parent digest points to a different supplied receipt;
12. target-domain coverage is absent;
13. the global lapse bound is non-finite/non-positive or lacks global certification;
14. ADM Wick completeness is not certified.

## 9. Validation authority

Implementation:

`tools/validate_global_gr_production_bundle.py`

Reference fixture:

`fixtures/global_gr_production_witness_bundle_reference_v0_1.json`

Tests:

`tests/test_global_gr_production_witness_bundle.py`

Static contract receipt:

`receipts/GLOBAL_GR_PRODUCTION_WITNESS_BUNDLE_CONTRACT_V0_1.json`

Target verdict:

`PASS_GLOBAL_GR_PRODUCTION_WITNESS_BUNDLE_CONTRACT_WITH_PRODUCTION_WITNESSES_OPEN`.
