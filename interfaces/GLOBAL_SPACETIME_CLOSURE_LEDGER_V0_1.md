# Global Spacetime Closure Ledger v0.1

Status: `LOCAL_EINSTEIN_FORM_PASS / SPATIAL_3M_CERTIFIER_PASS / TEMPORAL_EXACTNESS_CERTIFIER_PASS / REGULAR_CLOCK_EXTENSION_CERTIFIER_PASS / LOCAL_TEMPORAL_FROBENIUS_PASS / SHARED_ATLAS_CERTIFIER_PASS / GLOBAL_SPACETIME_REALIZATION_INPUT_OPEN / GLOBAL_HYPERBOLICITY_OPEN`

Date: 2026-08-30

Authority: `NONCANONICAL_CROSS_REPO_AUDIT`. Source claims remain owned by TIR, IDT and RFC. `promotion_authority=false`.

## 1. Current dependency surface

```text
TIR A5 spatial 3-manifold/smooth-realization certifier
 -> GSC-1 actual production spatial complex

IDT 05H exact event-clock certifier
 -> GSC-2 actual production event complex
 -> IDT 05I regular smooth-clock extension witness certifier
 -> GSC-3 actual production continuum clock witness + coverage
 -> IDT 05G positive-lapse Frobenius foliation

TIR spatial realization
 + IDT regular clock/foliation
 + RFC RF-E8 ADM coframe
 -> RFC RF-E25 shared atlas/coframe cocycle certifier
 -> GSC-4 actual production shared spacetime atlas

RFC RF-E24 local Einstein field-equation form
 + production PASS GSC-1..GSC-4
 -> GSC-5 global Lorentzian domain carrying RF-E24

stronger downstream causal/PDE gate
 -> GSC-6 global hyperbolicity / Cauchy foliation
```

The certifier layer for GSC-3 and GSC-4 is now explicit. Their production realizations remain open inputs.

## 2. TIR spatial geometry

Repository: `AdrianLipa90/The-Fundamental-Theory-of-Informational-Relations`.

Main baseline: `3f5a08ef04ec53c1a155263d23e8b10a96404370`.

Draft branch: `feat/tir-cartan-refinement-v0.1`.

A5 exact head: `2568fb24e0bc91e8f1c75dcfdc5659a57ca382b9`.

Hosted `TIR global 3-manifold smooth certificate`, run #1, id `33331003616`: `SUCCESS`.

Verdict:

`SPATIAL_CERTIFIER_PASS / PRODUCTION_SPATIAL_3_COMPLEX_OPEN_INPUT`.

## 3. IDT temporal geometry

Repository: `AdrianLipa90/Informational-Dynamics-of-Time`.

Current main baseline at 05I validation: `ceb3d74b581fc2445c3fad2474a7506a76b588fa`.

Draft branch: `feat/idt-temporal-foliation-v0.1`.

Current 05I exact head: `fc87c4176dfcc480529ba28bd67042d3ebf02c72`.

### 3.1 05H — exact discrete event clock

05H substantive commit: `8eda524ad9a3ba1e1876915a4724db12e0a95bd1`.

Hosted reference suite #916, id `33336267608`: `SUCCESS`.

The exactness criterion is

\[
\vartheta=\delta t
\quad\Longleftrightarrow\quad
\oint_C\vartheta=0
\]

for every event cycle, with positive elapsed weights and one additive-constant freedom in the reconstructed scalar.

### 3.2 05I — regular smooth clock-extension witness

05I substantive commit: `10049d5de3819d2654f19ce5158af5dd85f5198f`.

Exact hosted-PASS head: `fc87c4176dfcc480529ba28bd67042d3ebf02c72`.

Dedicated workflow `IDT 05I regular smooth clock extension`, run #2, id `33339841644`: `SUCCESS`.

The supplied patch witness uses

\[
t_p(x)=a_p\cdot x+b_p,
\qquad a_p\neq0,
\]

and affine overlaps

\[
x_q=A_{q\leftarrow p}x_p+s_{q\leftarrow p},
\qquad \det A_{q\leftarrow p}\neq0.
\]

A single scalar clock on overlaps requires

\[
a_qA_{q\leftarrow p}=a_p,
\qquad
a_q\cdot s_{q\leftarrow p}+b_q=b_p.
\]

The discrete-to-continuum event binding preserves the 05H additive symmetry by requiring one global constant `C`:

\[
t_p(X_{p,v})=t_V(v)+C.
\]

Declared triple overlaps satisfy

\[
A_{r\leftarrow p}=A_{r\leftarrow q}A_{q\leftarrow p},
\]

\[
s_{r\leftarrow p}=A_{r\leftarrow q}s_{q\leftarrow p}+s_{r\leftarrow q}.
\]

Because each affine patch has `a_p != 0`, its local witness is smooth and regular. Full target-domain promotion additionally requires the production witness and an explicit coverage witness.

Verdict:

`REGULAR_SMOOTH_CLOCK_EXTENSION_CERTIFIER_PASS / PRODUCTION_REGULAR_CLOCK_WITNESS_OPEN_INPUT`.

Diagnostic history: dedicated run #1, id `33339745130`, failed before 05I assertions because the workflow installed only `pytest` while the existing IDT package initialization requires NumPy. The environment was aligned to `requirements.txt`; the subsequent exact-head run passed.

### 3.3 05G — temporal foliation

05G substantive head: `ef80f706c79bc4fbd15266c0608d2ec09674508b`.

Hosted reference suite #913, id `33333216909`: `SUCCESS`.

On a supplied regular clock domain,

\[
\Theta_R=N_Rc\,dt,
\qquad N_R>0,
\]

implies

\[
\Theta_R\wedge d\Theta_R=0.
\]

05I therefore supplies an executable witness gate for the smooth-clock input required by 05G.

### 3.4 Independent IDT full-suite blocker

The current IDT main reference suite is already red at main `ceb3d74b581fc2445c3fad2474a7506a76b588fa`: run #925, id `33339429528`.

The 05I exact-head full suite #928, id `33339841677`, fails at the same collection layer because the seam stack imports a missing `onsager_dissipation` symbol. This is recorded as an independent repository-maintenance blocker and does not replace the dedicated 05I verdict.

## 4. RFC relativistic geometry

Repository: `AdrianLipa90/Relational-Field-Closure`.

Main baseline: `63418a88d686021c2a6fe6ab159d6152db303c19`.

Draft branch: `feat/rfe21-einstein-uniqueness-selection-v0.1`.

### RF-E24

Exact head: `5e8ca5e5aea4ecb63a3ea5fd005518fa63183d3d`.

RFC reference suite #390, id `33330773981`: `SUCCESS`.

On the admitted nondegenerate branch,

\[
G_{\mu\nu}+\Lambda g_{\mu\nu}=\kappa_E T_{\mu\nu},
\qquad
\kappa_E=\frac{8\pi G}{c^4},
\]

with the declared selection premises and RF-E3 normalization transfer.

### RF-E25

Current exact head: `4d581ac8d03e637f65fdefa2b9326ffc1effe0e1`.

RFC reference suite #392, id `33337181002`: `SUCCESS`.

The shared atlas gate checks

\[
E_qJ_{q\leftarrow p}=\Lambda_{q\leftarrow p}E_p,
\qquad
\Lambda^T\eta\Lambda=\eta,
\qquad
J^Tg_qJ=g_p,
\]

plus shared-clock preservation, orientation/time orientation, connected overlap incidence and coordinate/frame cocycles.

Verdict:

`SHARED_SPACETIME_ATLAS_CERTIFIER_PASS / PRODUCTION_SHARED_ATLAS_OPEN_INPUT`.

## 5. Closed theorem/certifier surfaces

| Surface | Verdict |
|---|---|
| TIR local Cartan refinement | `PASS` |
| TIR torsion-free Levi-Civita sector | `PASS` |
| TIR leading second-order metric-jet rule under LRR | `PASS_ON_DECLARED_RULE` |
| TIR global 3-manifold/smooth-realization certifier | `PASS` |
| IDT event-clock exactness certifier | `PASS` |
| IDT regular smooth clock-extension witness certifier | `PASS` |
| IDT positive-lapse Frobenius foliation theorem/certifier | `PASS` |
| RFC local Einstein field-equation form | `PASS_ON_DECLARED_SELECTION_RULES` |
| RFC ADM parent roundtrip | `PASS` |
| RFC shared-spacetime atlas/coframe cocycle certifier | `PASS` |

## 6. Remaining production frontier

### GSC-1 — production spatial complex

Input: actual global TIR tetrahedral incidence complex.

State: `OPEN_INPUT`.

### GSC-2 — production temporal event complex

Input: actual IDT event incidence plus positive elapsed weights.

State: `OPEN_INPUT`.

### GSC-3 — regular smooth clock extension

Certifier: `IDT 05I`.

Certifier state: `PASS`.

Production inputs still required:

- production 05H event scalar;
- production continuum chart witness;
- event embeddings;
- overlap maps/cocycles;
- target-domain coverage witness.

Combined state:

`CERTIFIER_PASS_WITH_PRODUCTION_REGULAR_CLOCK_WITNESS_OPEN_INPUT`.

### GSC-4 — shared spatial-temporal realization

Certifier: `RFC RF-E25`.

Certifier state: `PASS`.

Production shared patch/overlap atlas remains required.

Combined state:

`CERTIFIER_PASS_WITH_PRODUCTION_SHARED_ATLAS_OPEN_INPUT`.

### GSC-5 — global carrier for RF-E24

State:

`CONDITIONAL_ON_PRODUCTION_PASS_GSC_1_TO_GSC_4`.

### GSC-6 — global hyperbolicity / Cauchy foliation

State:

`OPEN_SEPARATE_GATE`.

## 7. Minimal remaining closure line

```text
GSC-1 actual spatial complex       -> A5
GSC-2 actual temporal event data   -> 05H
GSC-3 actual smooth clock witness  -> 05I -> 05G
GSC-4 actual shared 4D atlas       -> RF-E25
------------------------------------------------
production PASS of GSC-1..4
 -> GSC-5 global domain carrying RF-E24

stronger downstream:
GSC-6 global hyperbolicity / Cauchy foliation
```

At this point the unresolved GSC-1..GSC-4 coordinates are production realization inputs rather than missing certifier definitions.

## 8. FPDG authority firewall

This ledger remains noncanonical while its cited source heads are draft research heads.

It leaves these canonical surfaces unchanged:

- `dependency_graph.yaml`;
- `claims.jsonl`;
- `source_export_heads.yaml`;
- `source_exports.lock.json`;
- source-owned `DEPENDENCY_EXPORT.json` snapshots.

Canonical promotion requires explicit source-side promotion and freshness procedures.

GREMLIN may audit candidates and contradictions with `promotion_authority=false`.

## 9. Overall verdict

\[
\boxed{
\begin{aligned}
&\text{LOCAL EINSTEIN FORM} &&= \text{PASS},\\
&\text{SPATIAL CERTIFIER} &&= \text{PASS},\\
&\text{TEMPORAL EXACTNESS CERTIFIER} &&= \text{PASS},\\
&\text{REGULAR CLOCK EXTENSION CERTIFIER} &&= \text{PASS},\\
&\text{TEMPORAL FOLIATION THEOREM} &&= \text{PASS},\\
&\text{SHARED ATLAS CERTIFIER} &&= \text{PASS},\\
&\text{PRODUCTION GLOBAL SPACETIME REALIZATION} &&= \text{OPEN INPUT},\\
&\text{GLOBAL HYPERBOLICITY} &&= \text{OPEN SEPARATE GATE}.
\end{aligned}
}
\]

Machine-readable companion: `receipts/GLOBAL_SPACETIME_CLOSURE_LEDGER_V0_1.json`.

Fail-closed test: `tests/test_global_spacetime_closure_ledger.py`.
