# Validation Failure Nerve Endings v0.1

Status: `SOURCE_VALIDATOR -> EXACT_FPDG_PAIN_COORDINATE -> GREMLIN_CANDIDATE_CONTEXT`

The dependency graph can only answer **where exactly does it hurt?** at the precision supplied by evidence. Therefore every source-side validator may emit a small machine-readable failure receipt:

```text
FPDG_VALIDATION_FAILURE_RECEIPT_V0_1
```

The receipt is the theory equivalent of a nerve ending: it tells the integration layer which claim failed and, when known, the exact source coordinate at which the failure was observed.

```text
source validator/test
   -> failure receipt
   -> claim_id
   -> path
   -> receipt / interface
   -> validator / test
   -> symbol / equation
   -> line range
   -> FPDG minimal failing frontier
   -> exact entry/exit dependency seam
   -> downstream REVALIDATION_REQUIRED
   -> incident signature
   -> GREMLIN candidate recurrence search
```

## Receipt contract

A failure row must contain at least one of:

```text
claim_id
source_locator
```

`source_locator` may contain only explicit coordinates supplied by the source validator:

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

The FPDG adapter never infers a line, symbol or equation from a claim name. A validator that knows only the claim produces claim-level localization. A validator that records an equation and line range permits source-range localization.

## End-to-end command

```text
python tools/diagnose_validation_failure.py failure_receipt.json --json
```

This produces:

```text
VALIDATION_INCONSISTENCY_EVIDENCE.json
INCONSISTENCY_DIAGNOSIS.json
PAIN_SEAM_REPORT.json
PAIN_MICRO_COORDINATES.json
PAIN_SIGNATURE.json
PAIN_SIGNATURE_MATCHES.json
GREMLIN_PAIN_PACKET.json
GREMLIN_PAIN_PACKET_MICRO.json
VALIDATION_PAIN_SUMMARY.json
```

The resulting GREMLIN packet contains deterministic evidence coordinates and recurrence candidates only. It remains `CHYBA / CANDIDATE_ONLY`, with no runtime or canon-write authority. Canonical KAKU resolution, explicit cross-domain alignment and one exact 36D basis remain mandatory before PNCS lowering.

## Example

```json
{
  "schema": "FPDG_VALIDATION_FAILURE_RECEIPT_V0_1",
  "repository_id": "RFC",
  "repository": "AdrianLipa90/Relational-Field-Closure",
  "source_commit": "0123456789abcdef0123456789abcdef01234567",
  "workflow": "RFC exact validation",
  "job": "rf-e20",
  "status": "FAIL",
  "failures": [
    {
      "failure_id": "RF_E20_MASS_SCALE",
      "kind": "EQUATION_CHECK_FAILURE",
      "claim_id": "RFC.E20.TETRA_CLOCK_MASS_SCALE",
      "source_locator": {
        "path": "closure/einstein/RF_E20_TETRA_CLOCK_MASS_SCALE_CLOSURE.md",
        "equation_id": "RF-E20.17",
        "line_start": 412,
        "line_end": 419,
        "validator_id": "test_rf_e20_mass_scale",
        "receipt_ref": "RF_E20_SCALE_RECEIPT.json"
      }
    }
  ]
}
```

The exact source coordinate is an observed inspection coordinate. Promotion of a physical explanation remains the responsibility of the source repository's proof/validator/receipt gates.
