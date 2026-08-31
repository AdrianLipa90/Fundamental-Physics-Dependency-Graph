# GSC-1 / GSC-2 Production-Input Contract Audit v0.1

Status: `INPUT_CONTRACT_LAYER_PASS / PRODUCTION_WITNESSES_OPEN`

Authority: `NONCANONICAL_CROSS_REPO_AUDIT`. Source ownership remains with TIR and IDT. This document does not promote reference controls or runtime diagnostics into production witnesses.

## GSC-1 — global spatial-complex input

Source owner: TIR.

Source PR: `AdrianLipa90/The-Fundamental-Theory-of-Informational-Relations#117`.

Exact head:

`5aaf572e9e931525f16bb0fa105afbb0d34c59c9`

Dedicated workflow:

- `TIR global spatial-complex input contract`
- run id `33343473631`
- conclusion `SUCCESS`

The source-owned contract freezes explicit provenance, unique vertex identifiers, tetrahedral incidence, canonical incidence SHA-256 and a production flag before handing the candidate complex to the existing TIR A5 global 3-manifold certifier.

The boundary-of-the-4-simplex reference control remains `production=false`. A structurally valid open-face negative control is accepted by the input layer and rejected by A5 manifold certification, so the parser does not hide topology failure.

FPDG state:

`GSC1_INPUT_CONTRACT_PASS / GSC1_PRODUCTION_TETRAHEDRAL_INCIDENCE_WITNESS_OPEN`.

## GSC-2 — production event-complex input

Source owner: IDT.

Source PR: `AdrianLipa90/Informational-Dynamics-of-Time#82`.

Exact head:

`44e2da0a7048df387f277f4e93e6970c445d4b67`

Dedicated workflow:

- `IDT 05J production event-complex input`
- run id `33343481792`
- conclusion `SUCCESS`

The source-owned 05J contract freezes occurrence identifiers, an explicit event-class quotient, directed positive elapsed edges, unique source-relation provenance, canonical incidence SHA-256 and a production flag before invoking the existing 05H exact-clock certifier.

A structurally valid event complex with non-zero temporal holonomy remains a valid parsed input with `exact_clock_certified=false`; the input contract therefore does not convert a 05H failure into an input-parser failure.

The repository-wide Reference-suite failure observed on the 05J exact head is retained as an independent baseline event and is not used as 05J promotion evidence. Dedicated 05J validation remains the typed source gate.

FPDG state:

`GSC2_INPUT_CONTRACT_PASS / GSC2_PRODUCTION_EVENT_INCIDENCE_QUOTIENT_WITNESS_OPEN`.

## 05I downstream smooth-clock gate

Current source PR: `AdrianLipa90/Informational-Dynamics-of-Time#81`.

Current exact head:

`c5f256c1435c4174c4ac531e40be2902aa32651b`

Repository-wide `Reference suite` run #939, id `33343691489`: `SUCCESS`.

Thus the current temporal source chain is typed as

```text
05J INPUT CONTRACT PASS
  -> production event-complex witness OPEN
  -> 05H exact event-clock certifier
  -> 05I regular smooth-clock extension certifier PASS
  -> production regular continuum witness OPEN
  -> 05G temporal foliation gate
```

## Cross-repository conclusion

The production bottleneck is now narrower than `OPEN_INPUT` alone suggests. Both GSC-1 and GSC-2 have deterministic, fail-closed source-owned data contracts. The remaining missing objects are the actual production witnesses satisfying those contracts.

```text
GSC-1: contract PASS -> production tetrahedral incidence witness OPEN
GSC-2: contract PASS -> production event incidence/quotient witness OPEN
```

No PhaseNav distance, GREMLIN candidate relation, reference fixture or synthetic control can substitute for these production witnesses. GREMLIN remains candidate/audit only, and PhaseNav 36D state may prioritize investigation but has no dependency-promotion authority.
