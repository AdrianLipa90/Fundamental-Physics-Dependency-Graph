# GREMLIN Pain Localization v0.2

Status: `EXACT_FRONTIER + EXACT_SEAM_COORDINATES + INCIDENT_SHAPE_MEMORY / GREMLIN_CANDIDATE_ONLY`

The diagnostic pipeline now distinguishes four different meanings of “something changed” before GREMLIN is allowed to search for a relational explanation:

```text
repository movement
    -> semantic dependency-export diff
        -> exact claim/edge observation
            -> minimal observed failing frontier
                -> exact entry/exit seam coordinates
                    -> repository-agnostic pain signature
                        -> prior-incident retrieval
                            -> GREMLIN candidate relation mining
```

## 1. Exact seam coordinates

`tools/localize_interface_seams.py` resolves each frontier claim to deterministic probe coordinates.

For the frontier claim itself it emits the exact source path. For every promoted incoming and outgoing edge it emits:

```text
seam_id
role
from / to
authority
from_repository / to_repository
scope = LOCAL_REPOSITORY | CROSS_REPOSITORY
registration_status
from_source / to_source
interface_id              # when registered
contract                  # exact interface contract
```

The primary seam roles are:

```text
ENTRY_TO_FRONTIER
EXIT_FROM_FRONTIER
ZONE_ENTRY_BOUNDARY
ZONE_EXIT_BOUNDARY
```

A promoted cross-repository edge without a matching entry in `interfaces/cross_repo_interfaces.yaml` is reported explicitly as:

```text
MISSING_CROSS_REPO_INTERFACE_CONTRACT
```

It is never guessed or silently treated as an existing interface.

## 2. Probe targets

Every pain zone includes a deterministic probe order:

```text
CLAIM_SOURCE
DEPENDENCY_SEAM
    -> interface contract status
    -> relation / quantity
    -> validation receipt
    -> remaining gate
    -> executable interface / bridge
```

This answers “where exactly do we inspect first?” without claiming that the first inspected seam is automatically the ultimate physical cause.

## 3. Scientific drift versus integration drift

Source-main movement is split into two independent coordinates:

```text
repository_head   = repository freshness
source_commit     = scientific state represented by DEPENDENCY_EXPORT.json
```

The current and locked exports are semantically diffed before any scientific invalidation is propagated.

If the dependency surface is identical, the pain is localized to:

```text
FPDG.SOURCE_HEAD_LOCK.<repo>
```

rather than to every claim in that repository.

If the export changes, the exact status/claim/local-edge differences become structured evidence and enter the claim-level frontier localizer.

## 4. Incident shape signature

`tools/build_pain_signature.py` creates `FPDG_PAIN_SIGNATURE_V0_1`.

The hash deliberately excludes repository-specific names from its structural basis. It uses relational features such as:

```text
localization mode
frontier status class
symptom count
witness-path lengths
downstream blast-radius size
seam roles
seam scopes
edge authority classes
interface registration states
interface-contract feature presence
integration-failure kinds
```

Exact claim IDs, seam IDs and integration locations remain in `exact_coordinates` outside the structural hash.

Thus two incidents in different repositories can have the same structural signature while retaining separate exact repair coordinates.

## 5. Incident memory retrieval

`tools/match_pain_signatures.py` compares the current signature with reviewed incident receipts in `diagnostics/incidents/`.

Two retrieval levels exist:

```text
SHA-256 structural signature equality -> exact structural recurrence
feature-token Jaccard similarity      -> candidate retrieval neighbor
```

Invalid historical incident files fail closed. The matcher does not silently skip malformed memory.

The incident bank is append-only. CI-generated signatures are not automatically committed into it; historical memory requires an explicit reviewed receipt.

## 6. GREMLIN packet

`FPDG_GREMLIN_PAIN_PACKET_V0_1` now carries:

```text
exact frontier witness chains
exact seam coordinates
exact probe targets
integration pain coordinates
repository-agnostic incident signature
prior incident recurrence candidates
```

GREMLIN receives these as search context only. Its output remains:

```text
EPISTEMIC CHYBA
promotion_state = CANDIDATE_ONLY
runtime_execution_authority = false
canon_write_authority = false
vector_guessing_allowed = false
```

Before any lowering to PNCS the existing gates still apply:

```text
explicit cross-domain alignment
    -> canonical KAKU resolution
        -> one exact 36D basis
            -> RelationalIsomorphism
                -> RADICAL
                    -> native PNV OPERATORS
```

## 7. Generated diagnostic receipts

A drift incident can now produce:

```text
SOURCE_DRIFT_REPORT.json
DEPENDENCY_EXPORT_SEMANTIC_DIFF.json
INCONSISTENCY_EVIDENCE.json
INCONSISTENCY_DIAGNOSIS.json
PAIN_SEAM_REPORT.json
PAIN_SIGNATURE.json
PAIN_SIGNATURE_MATCHES.json
GREMLIN_PAIN_PACKET.json
```

This gives a complete chain from observed inconsistency to exact inspection coordinates and then to GREMLIN’s candidate pattern search, while keeping deterministic diagnosis and candidate generation separate.
