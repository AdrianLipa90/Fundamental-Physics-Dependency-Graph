# FPDG Pain Incident Memory

This directory is the durable, append-only bank of reviewed structural incident signatures used for GREMLIN retrieval.

Each stored incident is a JSON receipt with schema `FPDG_PAIN_SIGNATURE_V0_1` and a unique immutable filename. Existing incident receipts are not rewritten to fit a later failure. Corrections are recorded as a new incident/correction receipt with explicit provenance.

The structural signature is repository-agnostic: it hashes failure topology, seam roles, authority classes, witness-path lengths, contract-feature presence and integration-failure kinds. Exact claim IDs and seam IDs remain outside the hash in `exact_coordinates`.

Matching has two levels:

```text
signature_hash equality  -> exact structural recurrence
feature-token Jaccard    -> retrieval candidate only
```

Before any stored incident is admitted for matching, the reader recomputes the SHA-256 structural hash and regenerates the feature tokens from `structural_signature`. A historical receipt whose stored hash or feature tokens disagree with its structure fails closed.

Neither matching level promotes an explanation. GREMLIN may use matches to search for relational isomorphisms, but explicit cross-domain alignment, canonical KAKU resolution and the exact 36D basis remain required before any PNCS lowering. Candidate output remains `CHYBA / CANDIDATE_ONLY`.

CI-generated `build/PAIN_SIGNATURE.json` is not automatically committed here. Promotion into incident memory requires an explicit reviewed receipt so transient CI failures do not become historical truth.

The append-only recorder is:

```text
python tools/record_reviewed_incident.py \
  build/PAIN_SIGNATURE.json \
  build/GREMLIN_PAIN_PACKET.json \
  --incident-id INCIDENT-YYYYMMDD-NNN \
  --reviewed-by <reviewer> \
  --evidence-ref <receipt-or-validation-ref>
```

It verifies the signature integrity and the GREMLIN safety boundary, writes the signature under `diagnostics/incidents/`, stores the exact companion packet under `diagnostics/incidents/packets/`, records a canonical packet SHA-256, and refuses to overwrite an existing incident id.
