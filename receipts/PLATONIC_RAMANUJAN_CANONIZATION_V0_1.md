# Platonic–Ramanujan canonization receipt v0.1

Date: 2026-09-11

Verdict: `STRUCTURAL_CANONICAL / REGISTRY_SYNC_PENDING / RUNTIME_ACTIVATION_REJECTED_V0_1`.

Validated upstream facts: finite `G36 = I12 square K3`, degree 7, 126 edges, finite Ramanujan bound PASS, normalized gap `(5-sqrt(5))/7`, isolated Lyapunov derivative non-positive.

Validated PNCS repository gate: `10/10 PASS`.

Fresh live-derived benchmark: exact target residual remains at roundoff; QHTRI Hermiticity/unitarity gates remain at numerical roundoff; sparse isolated kernel is cheaper in the measured host microbenchmark; paired perturbation recovery worsens for every tested positive beta. Therefore additive runtime activation is rejected in v0.1.

No downstream physical claim is promoted. `dependency_graph.yaml` / `claims.jsonl` synchronization remains a separate deterministic registry gate.