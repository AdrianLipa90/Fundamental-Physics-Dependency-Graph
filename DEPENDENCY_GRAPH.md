# Fundamental Physics — Cross-Repository Dependency Graph

Status: `BOOTSTRAP_V0_1 / CANONICAL_CROSS_REPO_BASELINE`

```text
TIR.FOUNDATION.C2
  -> TIR.SPACE.LOCAL_R3
  -> TIR.SPACE.TETRAHEDRON
  -> TIR.HOLONOMY.WIJ
       -> TIR.GLOBAL_GLUING                         GREMLIN_CANDIDATE_SEARCH
       -> TIR.STANDARD_MODEL                       ACTIVE_RECONCILIATION

IDT.CLOCK.GAMMA_T                                  CROSS_REPO_PASS
  -> RFC.ADM.E8                                    PASS
       -> RFC.ADM.E9                               PASS
       -> RFC.ADM.E10                              PASS
       -> RFC.ADM.E11                              PASS
       -> RFC.ADM.E12                              PASS
       -> RFC.ADM.E13                              PASS / MAIN
       -> RFC.PHYSICAL_SCALE_COUPLING              ACTIVE_FRONTIER

TIR.SPACE.LOCAL_R3
  -> RFC.ADM.E8
     [physical spatial Gamma_x / cell-width remains a calibration gate]

SOH.HALF.CROSSLINKS                                CANDIDATE_ONLY
  - - -> TIR.FOUNDATION.C2                         PROMOTION_REQUIRED

SOH.LI_WEIL.NATIVE_CLOSURE                         OPEN_FRONTIER
```

## Source anchors

TIR source status records the foundational spine

```text
0 -> P -> FIRST DISTINCTION -> {N,S} -> 1/2 -> ln2 -> C^2
```

and the local spatial continuation

```text
C^2 -> rho_x -> A_2 -> delta(rho_x,rho_y) -> Herm_0(2) ~= R^3
```

with the Euclidean and tetrahedral branches downstream.

RFC source status records the action-level ADM chain through RF-E13 and keeps physical carrier/scale/coupling promotion as the active downstream frontier. The same source records the promoted IDT temporal calibration

```text
Gamma_t = T_r * a_r
Gamma_tau,x|r = T_r * a_x = N_R * Gamma_t
```

while physical `Gamma_x` remains an upstream calibration gate.

## Edge classes

`CANONICAL` — intra-repository dependency explicitly promoted by the source.

`CANONICAL_CROSS_REPO` — cross-repository dependency stated by a source repository or promoted by an exact cross-repository validation receipt.

`CANONICAL_FRONTIER` — promoted dependency leading into an active frontier.

`CANDIDATE_ONLY` — relational-isomorphism or discovery edge awaiting an explicit promotion gate.

## Revalidation propagation

Promoted edges carry invalidation downstream. If an upstream promoted claim changes materially, every reachable promoted descendant is marked `REVALIDATION_REQUIRED` until its evidence gate passes against the new upstream state.

Candidate-only edges remain isolated from canonical invalidation propagation until promotion.
