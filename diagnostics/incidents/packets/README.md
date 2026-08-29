# Reviewed GREMLIN Pain Packets

This directory is the durable append-only companion to the structural signature bank.

A signature answers: **have we seen this failure shape before?**

A reviewed `FPDG_GREMLIN_PAIN_PACKET_V0_1` answers: **what exact witness chains, seams and probe coordinates produced that historical shape?**

The full packet is needed when a recurrence candidate is selected for PNCS GREMLIN cross-incident relation mining. Signature similarity alone is never enough to construct an `ISOMORPHIC_TO` alignment.

Storage rule:

```text
diagnostics/incidents/<incident>.json          # reviewed FPDG_PAIN_SIGNATURE_V0_1
diagnostics/incidents/packets/<incident>.json  # reviewed FPDG_GREMLIN_PAIN_PACKET_V0_1
```

Both files are append-only and must refer to the same reviewed incident. CI-generated `build/GREMLIN_PAIN_PACKET.json` is not copied here automatically.

Before PNCS lowering, the selected historical packet still passes:

```text
explicit witness-chain selection
-> explicit claim_id -> grammar atom binding
-> explicit cross-domain positional alignment
-> canonical KAKU resolver
-> one exact 36D basis
```

Historical storage therefore preserves evidence; it does not promote the historical GREMLIN interpretation.
