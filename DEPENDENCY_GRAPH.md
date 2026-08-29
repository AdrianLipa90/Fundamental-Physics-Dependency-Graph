# Fundamental Physics — Cross-Repository Dependency Graph

Status: `V0_2 / ACTIVE_CLAIM_LEVEL_BASELINE`

The machine-readable authority is `dependency_graph.yaml`. This document is its human-readable projection.

## 1. TIR primitive and spatial spine

```text
TIR.PRIMITIVE.ZERO
 -> TIR.PRIMITIVE.POINT
 -> TIR.PRIMITIVE.FIRST_DISTINCTION
 -> TIR.PRIMITIVE.POLES_NS
 -> TIR.FOUNDATION.HALF
 -> TIR.FOUNDATION.LN2
 -> TIR.FOUNDATION.C2
 -> TIR.SPACE.DENSITY_CARRIER
 -> TIR.SPACE.A2
 -> TIR.SPACE.RELATIONAL_DISTANCE
 -> TIR.SPACE.LOCAL_R3
      |-> TIR.SPACE.PYTHAGOREAN
      +-> TIR.SPACE.TETRAHEDRON
           -> TIR.HOLONOMY.WIJ
                |-> TIR.GLOBAL_GLUING
                |-> TIR.TORSION
                +-> TIR.STANDARD_MODEL
```

The half/ln2 branch also feeds `TIR.KAPPA.NORMALIZATION`. `TIR.FOUNDATION.C2` feeds the sibling temporal interface `TIR.TIME_JOIN`.

## 2. IDT temporal and relativistic spines

```text
TIR.TIME_JOIN
 -> IDT.TEMPORAL.PRIMITIVE
 -> IDT.TEMPORAL.WAVE
 -> IDT.NOW
 -> IDT.BIFURCATION
 -> IDT.TEMPORAL.TRANSPORT
 -> IDT.MEMORY
 -> IDT.ORCHORBITAL
 -> IDT.RETRODICTION
 -> IDT.RETROCAUSAL_TESTS
 -> IDT.EINSTEIN.CLOSURE
```

The parallel relativistic prerequisite begins at the same temporal primitive and crosses RFC at the hardened source bridge:

```text
IDT.TEMPORAL.PRIMITIVE
 -> IDT.NOETHER.GAUGE_COVARIANT_SOURCE
 -> RFC.SOURCE.CONSERVED_CARRIER
 -> IDT.RELATIVISTIC.FIELD_BRIDGE
 -> IDT.EINSTEIN.CLOSURE
```

The cross-repository evidence is the hardened chain

```text
IDT-01AC -> IDT-01AG -> RF-M1 -> RF-E0 -> EINSTEIN_CLOSURE
```

recorded by `RFC/validation/RFM1_RFE0_RELATIVISTIC_BRIDGE_HARDENING_V0_1.json`: RFC reference suite `448/448 PASS`, focused `RF-M1 9/9`, `RF-E0 7/7`, with IDT peer suite `437/437 PASS`.

`IDT.TEMPORAL.WAVE -> IDT.CLOCK.GAMMA_T`, and the promoted material clock calibration separately feeds the later RFC ADM assembly.

## 3. RFC field/action/ADM spine

```text
RFC.SOURCE.CONSERVED_CARRIER
 -> RFC.N1B2K.CURRENT_MEASURE
 -> RFC.N1B2O.MATTER_SOURCE_FACTORIZATION
 -> RFC.N1B2P.MAXWELL_INTERTWINER
 -> RFC.E4.PHASE_STRESS_ENERGY
 -> RFC.E5.CARRIER_ENERGY
 -> RFC.E6.LORENTZIAN_ACTION
 -> RFC.E7.SCALAR_T_DECOMPOSITION
 -> RFC.MATTER.SCALAR_TMN
 -> RFC.L1.LAMBDA_TARGET
 -> RFC.L2.LAMBDA_ACTION_STABILITY
 -> RFC.L3.INFORMATION_SCALAR_POTENTIAL
 -> RFC.L4.INFORMATION_CURVATURE_PULLBACK
 -> RFC.L4A.SHANNON_FISHER_NORMALIZATION
 -> RFC.L5.TEMPORAL_WAVE_KG_BRIDGE
 -> RFC.L5A.PREMETRIC_CALIBRATION
 -> RFC.ADM.E8
 -> RFC.ADM.E9
 -> RFC.ADM.E10
 -> RFC.ADM.E11
 -> RFC.ADM.E12
 -> RFC.ADM.E13
 -> RFC.PHYSICAL_SCALE_COUPLING
```

`RFC.ADM.E8` has two explicit cross-repository prerequisites in the graph:

```text
IDT.CLOCK.GAMMA_T -> RFC.ADM.E8
TIR.SPACE.LOCAL_R3 -> RFC.ADM.E8
```

The second edge records the upstream spatial carrier while preserving the source-side `Gamma_x / cell-width` calibration frontier. The ADM spine remains distinct from the earlier RF-M1/RF-E0 relativistic bridge rather than being used as a substitute for it.

## 4. RFC coupling spine

```text
RFC.COUPLING.YM_BCJ
 -> RFC.COUPLING.FOUR_POINT_DC
 -> RFC.COUPLING.FIVE_POINT_KLT
 -> RFC.COUPLING.RFG29
 -> RFC.COUPLING.RFG30
 -> RFC.COUPLING.RFG31
 -> RFC.COUPLING.RFG32
 -> RFC.COUPLING.RFG33
 -> RFC.COUPLING.RFG34
 -> RFC.COUPLING.RFG35
 -> RFC.COUPLING.PHYSICAL_G
 -> RFC.PHYSICAL_SCALE_COUPLING
```

`RFG35` and physical `G` remain frontier/open states; they are represented as dependencies rather than promoted numerical physical constants.

## 5. SOH candidate overlay

The following edges are isolated from canonical invalidation propagation until their explicit promotion gates pass:

```text
SOH.SU2.DOUBLE_COVER
 - -XFI.03- -> IDT.HALF_SEAM.DOUBLE_COVER_SIGNATURE

SOH.HALF.ZERO_ORDER_DOUBLING
 - -XFI.28.02- -> IDT.HALF_SEAM.RELATIONAL_ZERO

SOH.BLOCH.CENTERED_RAPIDITY
 - -XFI.28.03- -> IDT.NOW.HYPERBOLIC_CHART

TIR.SOH.NEGATIVE_INVERSE
 - -candidate- -> SOH.LI_WEIL.NATIVE_CLOSURE
```

The first two require theorem/validator/receipt promotion. XFI.28.03 requires a domain/inverse/singular-boundary audit. The Li/Weil edge requires native closure to complete positivity.

## 6. Edge authority

`CANONICAL` means promoted intra-repository dependency.

`CANONICAL_CROSS_REPO` means promoted cross-repository dependency supported by a source status/bridge/validation record.

`CANONICAL_FRONTIER` means a promoted dependency into an explicitly open or active frontier.

`CANDIDATE_ONLY` means discovery/relational-isomorphism state with no canon authority and an explicit promotion gate.

## 7. Revalidation propagation

A material upstream change propagates `REVALIDATION_REQUIRED` through every reachable promoted descendant. Candidate-only edges remain excluded until promotion.
