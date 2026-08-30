# Global Spacetime Closure Ledger v0.1

Status: `LOCAL_EINSTEIN_FORM_PASS / SPATIAL_3M_CERTIFIER_PASS / TEMPORAL_EXACTNESS_CERTIFIER_PASS / LOCAL_TEMPORAL_FROBENIUS_PASS / SHARED_ATLAS_CERTIFIER_PASS / GLOBAL_SPACETIME_REALIZATION_INPUT_OPEN / GLOBAL_HYPERBOLICITY_OPEN`

Date: 2026-08-30

Authority: `NONCANONICAL_CROSS_REPO_AUDIT`. Source claims remain owned by TIR, IDT and RFC. `promotion_authority=false`.

## 1. Composed dependency surface

```text
TIR A2/A3/A4
 -> TIR A5 3-manifold/smooth-realization certifier
 -> GSC-1 PRODUCTION_SPATIAL_3_COMPLEX

IDT 00E/00F
 -> IDT 05H event-clock exactness certifier
 -> GSC-2 PRODUCTION_TEMPORAL_EVENT_COMPLEX
 -> GSC-3 REGULAR_SMOOTH_CLOCK_EXTENSION
 -> IDT 05G positive-lapse Frobenius foliation

RFC RF-E8 local ADM coframes
 + certified TIR spatial realization
 + certified IDT clock/foliation
 -> RFC RF-E25 shared atlas/coframe cocycle certifier
 -> GSC-4 PRODUCTION_SHARED_SPACETIME_ATLAS

RFC RF-E24 local Einstein field-equation form
 + production PASS GSC-1..GSC-4
 -> GSC-5 GLOBAL_DOMAIN_FOR_RF_E24

stronger causal/PDE promotion
 -> GSC-6 GLOBAL_HYPERBOLICITY_CAUCHY_FOLIATION
```

## 2. Exact source heads and hosted receipts

### TIR spatial branch

Repository: `AdrianLipa90/The-Fundamental-Theory-of-Informational-Relations`

Main baseline: `3f5a08ef04ec53c1a155263d23e8b10a96404370`

Draft branch: `feat/tir-cartan-refinement-v0.1`

Exact A5 head: `2568fb24e0bc91e8f1c75dcfdc5659a57ca382b9`

Hosted workflow `TIR global 3-manifold smooth certificate`, run #1, id `33331003616`: `SUCCESS`.

Verdict:
`SPATIAL_CERTIFIER_PASS / PRODUCTION_SPATIAL_3_COMPLEX_OPEN_INPUT`.

### IDT temporal branch

Repository: `AdrianLipa90/Informational-Dynamics-of-Time`

Main baseline: `84ce1886175af872ae4a56ba36f7e106d8e23635`

Draft branch: `feat/idt-temporal-foliation-v0.1`

Current exact hosted-PASS head: `a36cdb7bffa3789bef154c2b987ebab68ccfb2d5`.

05G substantive head `ef80f706c79bc4fbd15266c0608d2ec09674508b`, hosted reference suite #913, id `33333216909`: `SUCCESS`.

05H substantive commit `8eda524ad9a3ba1e1876915a4724db12e0a95bd1`, current hosted reference suite #916, id `33336267608`: `SUCCESS`.

05H certifies the discrete exactness condition

\[
\vartheta=\delta t
\quad\Longleftrightarrow\quad
\oint_C\vartheta=0
\]

for every event-cycle `C`.

05G certifies on an admitted regular smooth clock domain

\[
\Theta_R=N_Rc\,dt,
\qquad N_R>0,
\qquad
\Theta_R\wedge d\Theta_R=0.
\]

Verdict:
`TEMPORAL_EXACTNESS_CERTIFIER_PASS / LOCAL_FROBENIUS_PASS / PRODUCTION_EVENT_COMPLEX_OPEN_INPUT / REGULAR_SMOOTH_CLOCK_EXTENSION_OPEN_INTERFACE`.

### RFC local and shared-spacetime branch

Repository: `AdrianLipa90/Relational-Field-Closure`

Main baseline: `63418a88d686021c2a6fe6ab159d6152db303c19`

Draft branch: `feat/rfe21-einstein-uniqueness-selection-v0.1`

RF-E24 exact head: `5e8ca5e5aea4ecb63a3ea5fd005518fa63183d3d`; RFC reference suite #390, id `33330773981`: `SUCCESS`.

RF-E24 gives on the admitted nondegenerate branch

\[
G_{\mu\nu}+\Lambda g_{\mu\nu}=\kappa_E T_{\mu\nu},
\qquad
\kappa_E=\frac{8\pi G}{c^4}
\]

with the declared RFC/TIR selection premises and RF-E3 normalization transfer.

RF-E25 substantive commit: `15e7eed8bbe0c75ba4ac30517f86cb2b70b7dbf8`.

RF-E25 exact hosted-PASS head: `4d581ac8d03e637f65fdefa2b9326ffc1effe0e1`.

Hosted RFC reference suite #392, id `33337181002`: `SUCCESS`.

The preceding #391 run, id `33337107285`, failed at test collection on an import-layout mismatch before mathematical assertions executed; commit `4d581ac8...` aligned the reference import with the repository-root `src.rfc` convention.

RF-E25 certifies a supplied ADM-adapted overlap atlas through

\[
E_qJ_{q\leftarrow p}=\Lambda_{q\leftarrow p}E_p,
\]

\[
\Lambda^T\eta\Lambda=\eta,
\qquad
J^Tg_qJ=g_p,
\]

shared-clock preservation, orientation/time-orientation gates and coordinate/frame cocycles on declared triple overlaps.

Verdict:
`SHARED_SPACETIME_ATLAS_CERTIFIER_PASS / PRODUCTION_SHARED_ATLAS_OPEN_INPUT`.

## 3. Closed certifier/theorem surfaces

| Surface | Verdict |
|---|---|
| TIR local Cartan curvature/torsion refinement | `PASS` |
| TIR torsion-free metric-compatible Levi-Civita sector | `PASS` |
| TIR leading second-order metric-jet selection under LRR | `PASS_ON_DECLARED_RULE` |
| TIR combinatorial 3-manifold/smooth-realization certifier | `PASS` |
| IDT global discrete event-clock exactness certifier | `PASS` |
| IDT positive-lapse local Frobenius foliation certifier | `PASS` |
| RFC local Einstein field-equation form | `PASS_ON_DECLARED_SELECTION_RULES` |
| RFC ADM parent roundtrip | `PASS` |
| RFC shared-spacetime atlas/coframe cocycle certifier | `PASS` |

## 4. Global realization frontier

### GSC-1 — production spatial 3-complex

Run TIR A5 on the actual global tetrahedral incidence data.

State: `OPEN_INPUT`.

### GSC-2 — production temporal event complex

Run IDT 05H on the actual event incidence plus positive elapsed-edge weights.

State: `OPEN_INPUT`.

### GSC-3 — regular smooth clock extension

Extend the certified discrete clock to the target smooth domain with

\[
dt\neq0
\]

and retain the positive IDT lapse binding.

State: `OPEN_INTERFACE`.

### GSC-4 — shared spatial-temporal realization

RFC RF-E25 now owns the executable compatibility certificate. On production data it requires:

- common patch/event lineage;
- positive lapse and invertible spatial triad per patch;
- shared IDT clock differential on overlaps;
- orientation-preserving overlap Jacobians;
- proper time-oriented Lorentz frame transitions;
- `E_q J = Lambda E_p`;
- metric pullback consistency;
- connected patch incidence;
- coordinate and frame cocycles on declared triple overlaps.

Certifier state:
`PASS`.

Production realization state:
`OPEN_INPUT`.

Combined ledger state:
`CERTIFIER_PASS_WITH_PRODUCTION_SHARED_ATLAS_OPEN_INPUT`.

Required production verdict:
`PASS_SHARED_SPACETIME_REALIZATION`.

### GSC-5 — global domain for RF-E24

RF-E24's local equation can be carried over the assembled smooth Lorentzian domain after production PASS of GSC-1 through GSC-4.

State:
`CONDITIONAL_ON_PRODUCTION_PASS_GSC_1_TO_GSC_4`.

### GSC-6 — Cauchy/global-hyperbolicity layer

Global hyperbolicity and Cauchy foliation remain the stronger downstream causal/PDE gate.

State:
`OPEN_SEPARATE_GATE`.

## 5. Minimal remaining frontier

```text
GSC-1 actual TIR spatial complex
GSC-2 actual IDT event complex
GSC-3 regular smooth clock extension
GSC-4 actual shared patch/overlap atlas -> RF-E25 certifier
----------------------------------------------------------
=> GSC-5 global Lorentzian domain carrying RF-E24

stronger downstream:
GSC-6 global hyperbolicity / Cauchy foliation
```

The broad compatibility question at GSC-4 now has an executable certifier. The remaining GSC-1..GSC-4 coordinates are production realization data/interfaces.

## 6. FPDG authority firewall

This ledger remains noncanonical while its cited source heads are draft feature heads.

It leaves these canonical surfaces unchanged:

- `dependency_graph.yaml`;
- `claims.jsonl`;
- `source_export_heads.yaml`;
- `source_exports.lock.json`;
- source-owned `DEPENDENCY_EXPORT.json` snapshots.

Canonical promotion requires the source-side promotion/freshness procedure after an explicit source-repository decision.

GREMLIN may audit dependency candidates and contradictions with `promotion_authority=false`.

## 7. Overall verdict

\[
\boxed{
\begin{aligned}
&\text{LOCAL EINSTEIN FORM} &&= \text{PASS},\\
&\text{SPATIAL 3-MANIFOLD CERTIFIER} &&= \text{PASS},\\
&\text{TEMPORAL EXACTNESS CERTIFIER} &&= \text{PASS},\\
&\text{LOCAL TEMPORAL FOLIATION} &&= \text{PASS},\\
&\text{SHARED ATLAS CERTIFIER} &&= \text{PASS},\\
&\text{PRODUCTION GLOBAL SPACETIME REALIZATION} &&= \text{OPEN INPUT/INTERFACE},\\
&\text{GLOBAL HYPERBOLICITY} &&= \text{OPEN SEPARATE GATE}.
\end{aligned}
}
\]

Machine-readable companion:
`receipts/GLOBAL_SPACETIME_CLOSURE_LEDGER_V0_1.json`.

Fail-closed test:
`tests/test_global_spacetime_closure_ledger.py`.
