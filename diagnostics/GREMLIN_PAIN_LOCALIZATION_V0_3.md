# GREMLIN Pain Localization v0.3

Status: `CLAIM_FRONTIER + INTERFACE_SEAM + SUB_CLAIM_COORDINATE + INCIDENT_MEMORY + PNCS_GREMLIN_INGRESS`

The localization stack now has three deterministic spatial scales before GREMLIN receives a candidate-mining request:

```text
DAG scale
  minimal failing claim frontier

interface scale
  exact promoted entry/exit seam + cross-repo contract

source scale
  exact path / receipt / validator / test / symbol / equation / line range
```

The full pipeline is:

```text
observed inconsistency
  -> structured evidence
  -> semantic export diff when source drift is involved
  -> minimal promoted-DAG frontier
  -> exact dependency/interface seams
  -> sub-claim micro-coordinate localization
  -> repository-agnostic pain signature
  -> reviewed incident retrieval
  -> GREMLIN pain packet
  -> explicit PNCS claim->grammar binding
  -> canonical KAKU resolution
  -> RelationalIsomorphism -> RADICAL -> native PNV candidate
```

## Sub-claim coordinate contract

`FPDG_INCONSISTENCY_EVIDENCE_V0_1` may now carry a `source_locator`:

```json
{
  "path": "closure/einstein/RF_E20.md",
  "equation_id": "RF-E20.17",
  "line_start": 412,
  "line_end": 419,
  "validator_id": "test_rf_e20_mass_scale",
  "receipt_ref": "RF_E20_SCALE_RECEIPT.json"
}
```

Supported coordinate fields are:

```text
path
symbol
equation_id
line_start / line_end
validator_id
test_id
receipt_ref
interface_id
```

`tools/localize_micro_coordinates.py` emits `FPDG_PAIN_MICRO_COORDINATES_V0_1` and preserves the finest coordinate explicitly supported by the evidence:

```text
CLAIM
SOURCE_PATH
RECEIPT
INTERFACE_CONTRACT
VALIDATOR_OR_TEST
SYMBOL
EQUATION
SOURCE_RANGE
INTEGRATION_METADATA_LOCATION
```

A `line_end` without `line_start`, an inverted line range, or disagreement between `source_path` and `source_locator.path` fails closed.

The micro-localizer does not infer a line, equation or symbol from a claim name. If the validator only tells us the claim, the coordinate remains claim-level.

## Meaning of “exact”

Exact localization means the report identifies the smallest coordinate justified by the supplied evidence. It does not mean that coordinate has automatically been proven to be the ultimate physical cause.

For example:

```text
validator fails at RF-E20.17 lines 412-419
```

is a stronger inspection coordinate than:

```text
RFC.E20 is downstream-revalidation-required
```

but causal promotion still requires the appropriate source-side validator/proof/receipt.

## GREMLIN boundary

GREMLIN receives exact coordinates as evidence context, not authority.

The downstream PNCS bridge is `PNCS_FPDG_GREMLIN_PAIN_INGRESS_V0_1`. It explicitly refuses to reinterpret FPDG claim IDs as KAKU atoms. A selected historical recurrence requires:

```text
reviewed current + historical witness packets
-> explicit claim_id -> grammar atom mapping
-> explicit positional cross-domain alignment
-> canonical KAKU resolver
-> one exact 36D basis
```

Only then can the existing PNCS GREMLIN relation-mining adapter compile a candidate relational isomorphism.

All candidate output remains `CHYBA / CANDIDATE_ONLY` with no runtime or canon-write authority.
