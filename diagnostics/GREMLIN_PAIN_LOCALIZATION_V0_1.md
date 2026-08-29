# GREMLIN Pain Localization v0.1

Status: `DETERMINISTIC_LOCALIZATION_IMPLEMENTED / GREMLIN_PATTERN_MINING_CANDIDATE_ONLY`

The purpose of this layer is to answer a stricter question than blast-radius analysis:

```text
The system is inconsistent.
        ↓
Where is the first observed place at which consistency breaks?
        ↓
Which exact claim / edge / interface / source path is implicated?
        ↓
Which downstream claims hurt because of it?
        ↓
Has GREMLIN seen the same relational failure shape elsewhere?
```

## 1. Separation of authority

FPDG performs deterministic localization. GREMLIN performs candidate relation mining.

```text
structured failure evidence
    -> exact claim / edge / path anchoring
    -> promoted-DAG minimal failing frontier
    -> witness paths + boundary seams
    -> downstream REVALIDATION_REQUIRED projection
    -> GREMLIN pain packet
    -> candidate relational-isomorphism search
```

GREMLIN does not select the canonical failing frontier and does not rewrite the FPDG graph.

## 2. Evidence atoms

`tools/diagnose_inconsistency.py` accepts `FPDG_INCONSISTENCY_EVIDENCE_V0_1` observations such as:

```text
STATUS_DRIFT
MISSING_CLAIM
EXTRA_CLAIM
MISSING_EDGE
EXTRA_EDGE
SOURCE_PATH_DRIFT
VALIDATOR_FAILURE
RECEIPT_FAILURE
CROSS_REPO_CONTRACT_FAILURE
SOURCE_HEAD_DRIFT
```

An observation should provide the most exact available anchor:

```text
claim_id
edge {from,to}
source_path + repository
repository only            # last-resort coarse fallback
```

The detector reports the anchoring method and precision. Repository-only fallback is never reported as exact localization.

## 3. Minimal failing frontier

Let `O` be the set of claims directly anchored by the observed failures and let `G+` be the promoted dependency DAG (`CANONICAL`, `CANONICAL_CROSS_REPO`, `CANONICAL_FRONTIER`).

The minimal observed failing frontier is

```text
F = { x in O | there is no y in O, y != x, with a promoted path y ->* x }.
```

Thus, if both an upstream claim and one of its descendants fail, the upstream observed claim is the frontier root and the descendant becomes a witness symptom. Independent failures remain separate frontier roots.

This is an observed diagnostic frontier, not an assertion of ultimate physical causation.

`CANDIDATE_ONLY` edges are excluded from this computation.

## 4. Pain zone

For every frontier claim the localizer emits:

```text
frontier_claim
repository
source
observation_ids
symptom_anchors
witness_paths
witness_nodes
immediate_promoted_parents
immediate_promoted_children
incoming_boundary_edges
outgoing_boundary_edges
downstream_revalidation[]
```

The incoming boundary edges are especially important. They identify the exact promoted seams through which a healthy/upstream region enters the observed failing region. For cross-repository failures this is the interface at which contract testing should start.

## 5. GREMLIN role

`tools/build_gremlin_pain_packet.py` converts the deterministic diagnosis into `FPDG_GREMLIN_PAIN_PACKET_V0_1`.

The packet deliberately contains raw claim witness chains rather than fabricated KAKU objects. The PNCS GREMLIN relation-mining contract requires explicit alignment and an explicit canonical `atom -> Kaku` resolution before compilation. Therefore:

```text
FPDG witness chains
    -> GREMLIN relation mining
    -> explicit cross-domain alignment
    -> canonical KAKU resolver
    -> RelationalIsomorphism
    -> RADICAL
    -> native PNV OPERATORS
    -> PNV candidate program
```

The packet carries:

```text
EPISTEMIC CHYBA
promotion_state = CANDIDATE_ONLY
runtime_execution_authority = false
canon_write_authority = false
vector_guessing_allowed = false
```

This matches the new PNCS GREMLIN compiler boundary: relational candidates can be made machine-checkable, but shared recurrence alone does not establish an isomorphism and missing KAKU/36D mappings fail closed.

## 6. Intended next layer: incident memory

Once diagnosis receipts accumulate, GREMLIN can compare the current pain zone against prior incidents by relational shape rather than filename or repository name. Useful invariants include:

```text
upstream status drift -> cross-repo interface -> downstream validator cascade
missing source claim -> stale export -> canonical-local mismatch
scale gate unresolved -> downstream normalization failures
candidate edge mistakenly admitted -> false canonical invalidation
clock/interface mismatch -> ADM/relativistic descendant cascade
```

Any such match remains a candidate explanation until its explicit evidence and promotion gates pass.

## 7. Operational commands

```bash
python tools/diagnose_inconsistency.py incident.json --json
python tools/build_gremlin_pain_packet.py build/INCONSISTENCY_DIAGNOSIS.json --json
```

The first command answers `where does it hurt?`. The second prepares the local failure geometry for GREMLIN to ask `have we seen this relational shape before, and what candidate repair pattern fits it?`.
