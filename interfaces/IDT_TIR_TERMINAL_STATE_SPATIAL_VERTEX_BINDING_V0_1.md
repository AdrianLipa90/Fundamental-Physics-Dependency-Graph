# IDT × TIR Terminal-State / Spatial-Vertex Binding v0.1

Status: `CROSS_REPO_INPUT_CONTRACT_DEFINED / EXPLICIT_STATE_TO_VERTEX_FUNCTION / PRODUCTION_BINDING_OPEN`

## Purpose

IDT 00F defines realized occurrence records

\[
\nu_k=(P_k,x_k),
\]

with terminal relational-state label `x_k`. IDT 00G exports the machine-readable occurrence map

\[
x:O\to S.
\]

TIR GSC-1 exports the vertex carrier of one supplied tetrahedral spatial complex,

\[
V(\Sigma).
\]

This FPDG interface owns the cross-repository physical binding input

\[
\boxed{b:S_{\rm used}\to V(\Sigma)}.
\]

The current source surfaces use independent identifier coordinates. The binding is therefore explicit and provenance-bound.

## Source coordinates

The contract freezes four independent coordinates:

1. IDT source commit or immutable digest;
2. IDT 00G occurrence/state-table SHA-256;
3. TIR source commit or immutable digest;
4. TIR GSC-1 spatial-complex incidence SHA-256.

The validator receives the exact terminal-state domain exported by 00G and the exact TIR spatial-vertex domain exported by GSC-1. Every binding target must belong to that TIR vertex domain.

## Functional binding

For each terminal state in the supplied 00G domain there is exactly one row

```text
terminal_state_id -> spatial_vertex_id
binding_evidence_id
```

so the map is total and single-valued on the declared state domain.

Injectivity and surjectivity are reported separately. They are downstream sector properties rather than prerequisites of the quotient-descended event-placement theorem. In particular, multiple terminal states may share one spatial anchor when the production binding supports that realization.

## Composition with IDT and RFC

The complete typed line is

```text
IDT 00F relational occurrence
 -> IDT 00G occurrence -> terminal_state
 -> FPDG terminal_state -> TIR spatial_vertex binding
 -> RFC GSC3B occurrence -> spatial_vertex
 + IDT 05J occurrence -> event quotient
 -> quotient-fibre constancy
 -> unique event spatial anchor
 + IDT 05H exact event clock
 -> RF-GSC3A event placement
```

State recurrence is preserved because distinct occurrences may carry the same `terminal_state_id` before this binding is applied.

## Digest and provenance

The canonical `binding_sha256` covers the immutable source coordinates together with sorted binding rows. Each row has a unique `binding_evidence_id`. Drift in either source coordinate or in any mapping row invalidates the receipt.

## Promotion firewall

Reference controls use `production=false`. A validated production dataset can become `promotion_review_eligible`; this interface always emits `canon_allowed=false`. Canonical promotion requires independent source-owned evidence for the physical state-to-vertex identification and downstream FPDG review.

GREMLIN × PhaseNav × Terminal36D may audit candidate correspondences. Their authority remains `CANDIDATE_ONLY`; deterministic source/provenance validation is the executable authority for this contract.

## Falsification rules

The certifier fails closed on:

- IDT or TIR source-coordinate drift;
- incomplete or extra terminal-state bindings relative to the supplied 00G domain;
- duplicate/conflicting state mappings;
- target vertices outside the supplied GSC-1 vertex domain;
- duplicated binding-evidence identifiers;
- binding digest mismatch.

## Current upstream candidate coordinates

- IDT 00G stacked source head: `740e03a4fc2c20eae3bb8eb0cf11dbe7d94ae160` (PR #88; hosted source gate evaluated independently);
- TIR GSC-1 source head: `5cc9f1e1a33972cf89369a3b97716e04901324ba` (PR #117).

## Validation authority

Implementation: `tools/certify_idt_tir_state_vertex_binding.py`

Reference tests: `tests/test_idt_tir_state_vertex_binding_v0_1.py`

Live candidate audit: `receipts/IDT_TIR_STATE_VERTEX_GREMLIN_PHASE36D_AUDIT_V0_1.json`

Verdict target: `PASS_FPDG_IDT_TIR_STATE_VERTEX_BINDING_CONTRACT_WITH_PRODUCTION_BINDING_OPEN`.
