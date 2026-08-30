# Global Spacetime Closure Ledger v0.2

Status: `LOCAL_EINSTEIN_FORM_PASS / SPATIAL_3M_CERTIFIER_PASS / TEMPORAL_EXACTNESS_CERTIFIER_PASS / REGULAR_CLOCK_EXTENSION_CERTIFIER_PASS / LOCAL_TEMPORAL_FROBENIUS_PASS / SHARED_ATLAS_CERTIFIER_PASS / GLOBAL_EINSTEIN_CARRIER_CERTIFIER_PASS / PRODUCTION_GLOBAL_SPACETIME_REALIZATION_OPEN / GLOBAL_HYPERBOLICITY_OPEN`

Date: 2026-08-30

Authority: `NONCANONICAL_CROSS_REPO_AUDIT`. Source claims remain owned by TIR, IDT and RFC. `promotion_authority=false`.

This v0.2 ledger is based on FPDG main `1e5e46a214c141bb07aa422740038b10a38f57d8`, after the post-merge v0.4 federation and source-lock refresh. It supersedes the draft-only v0.1 audit line for current cross-repository closure tracking; it does not rewrite canonical claim authority.

## 1. Current closure chain

```text
TIR spatial theorem/certifier layer
  A5 global 3-manifold/smooth-realization certifier
  -> GSC-1 production spatial realization

IDT temporal theorem/certifier layer
  05H event-clock exactness
  -> GSC-2 production event complex
  -> 05I regular smooth-clock extension certifier
  -> GSC-3 production regular clock witness + coverage
  -> 05G positive-lapse Frobenius foliation

TIR + IDT + RFC local ADM geometry
  -> RF-E25 shared Lorentzian atlas/coframe cocycle certifier
  -> GSC-4 production shared spacetime atlas

RF-E24 local Einstein form
  + RF-E25 shared atlas
  + RF-E26 local-to-global tensor gluing certifier
  -> GSC-5 production global Einstein carrier

stronger causal/PDE layer
  RF-L7 local hyperbolicity + Cauchy promotion contract
  -> GSC-6 production global Cauchy/global-hyperbolicity witness
```

The certifier/theorem definitions through GSC-5 are now explicit. The unresolved coordinates GSC-1 through GSC-5 are production-realization inputs and coverage witnesses. GSC-6 remains a distinct global-causality gate.

## 2. Current repository heads

| Repository | Current main observed | Closure witness used here |
|---|---|---|
| TIR | `62a13ba92f0db641d6d699a88059aedf33528300` | A5 head `2568fb24e0bc91e8f1c75dcfdc5659a57ca382b9`; hosted run `33331003616` SUCCESS |
| IDT | `f186aab6024a592be406684785069edfe2f3d5bf` | 05I head `fc87c4176dfcc480529ba28bd67042d3ebf02c72`; dedicated run `33339841644` SUCCESS |
| RFC | `012d4aa790bca7d631caf5c8002bebaa3a07710a` | RF-E26 head `d9779608754aae294e3a37a5e5c9fef63ff37a39`; full RFC run `33341138133` SUCCESS |
| FPDG | `1e5e46a214c141bb07aa422740038b10a38f57d8` | this audit branch only |

The TIR/IDT current-main entries above include refreshed dependency-export work. The theorem/certifier heads are pinned separately because their hosted receipts are the validation witnesses consumed by this audit.

## 3. Closed theorem/certifier surfaces

### TIR spatial layer

A5 certifies the supplied combinatorial 3-manifold/smooth-realization criterion. Hosted workflow id `33331003616`: `SUCCESS`.

State:

`SPATIAL_CERTIFIER_PASS / PRODUCTION_SPATIAL_3_COMPLEX_OPEN_INPUT`.

### IDT temporal layer

05H supplies the exact discrete clock criterion

\[
\vartheta=\delta t
\quad\Longleftrightarrow\quad
\oint_C\vartheta=0.
\]

05I supplies the discrete-to-smooth witness certifier. On each supplied patch,

\[
t_p(x)=a_p\cdot x+b_p,
\qquad a_p\neq0,
\]

with compatible affine overlaps and one global additive clock alignment. Dedicated hosted run #2, id `33339841644`: `SUCCESS`.

05G then gives, on a supplied regular clock domain,

\[
\Theta_R=N_Rc\,dt,
\qquad N_R>0,
\qquad
\Theta_R\wedge d\Theta_R=0.
\]

State:

`TEMPORAL_EXACTNESS_CERTIFIER_PASS / REGULAR_CLOCK_EXTENSION_CERTIFIER_PASS / LOCAL_FROBENIUS_PASS / PRODUCTION_TEMPORAL_INPUTS_OPEN`.

### RFC local Einstein and shared-atlas layer

RF-E24 supplies on its declared local selection premises

\[
G_{\mu\nu}+\Lambda g_{\mu\nu}=\kappa_E T_{\mu\nu},
\qquad
\kappa_E=\frac{8\pi G}{c^4}.
\]

RF-E25 certifies a supplied shared Lorentzian atlas through

\[
E_qJ_{q\leftarrow p}=\Lambda_{q\leftarrow p}E_p,
\qquad
\Lambda^T\eta\Lambda=\eta,
\qquad
J^Tg_qJ=g_p,
\]

plus clock, orientation and cocycle gates.

State:

`LOCAL_EINSTEIN_FORM_PASS / SHARED_ATLAS_CERTIFIER_PASS / PRODUCTION_SHARED_ATLAS_OPEN_INPUT`.

### RFC RF-E26 — global Einstein carrier gluing

RF-E26 defines on each patch

\[
\mathcal R_p
=G_p+\Lambda g_p-\kappa_E T_p.
\]

For the RF-E25 overlap convention `dx_q=J_{q<-p}dx_p`, it certifies

\[
X_p=J^TX_qJ,
\qquad X\in\{g,G,T,\mathcal R\},
\]

common `Lambda` and `kappa_E`, connected overlap incidence, patchwise zero residual, and explicit promotion guards for the RF-E25 parent plus target-domain coverage.

Thus on a supplied covered atlas,

\[
\mathcal R|_{U_p}=0\ \forall p
\quad\Longrightarrow\quad
\boxed{\mathcal R=0}
\]

on the represented domain.

Exact RF-E26 head:

`d9779608754aae294e3a37a5e5c9fef63ff37a39`.

Hosted `RFC reference suite` run #401, id `33341138133`: `SUCCESS`.

The preceding run #400, id `33341085574`, failed during collection on repository import layout before RF-E26 assertions; the repo-native `src.rfc` import was then used and the full suite passed.

Verdict:

`PASS_RFE26_GLOBAL_EINSTEIN_CARRIER_CERTIFIER_WITH_PRODUCTION_INPUT_OPEN`.

## 4. Global frontier

### GSC-1 — production spatial realization

State: `OPEN_INPUT`.

Required: actual TIR spatial incidence/realization input accepted by A5.

### GSC-2 — production temporal event complex

State: `OPEN_INPUT`.

Required: actual IDT event incidence plus positive elapsed-edge weights accepted by 05H.

### GSC-3 — production regular smooth clock witness

Certifier: `IDT 05I`.

State:

`CERTIFIER_PASS_WITH_PRODUCTION_REGULAR_CLOCK_WITNESS_OPEN_INPUT`.

### GSC-4 — production shared spacetime atlas

Certifier: `RFC RF-E25`.

State:

`CERTIFIER_PASS_WITH_PRODUCTION_SHARED_ATLAS_OPEN_INPUT`.

### GSC-5 — global Einstein carrier

Certifier: `RFC RF-E26`.

Certifier state: `PASS`.

Production promotion requires:

- production PASS of the spatial, temporal, regular-clock and shared-atlas realization inputs represented by GSC-1 through GSC-4;
- explicit target-domain coverage;
- RF-E25 parent certification on that same realization;
- RF-E26 patchwise Einstein residual and tensor-overlap checks on that same realization.

Combined state:

`CERTIFIER_PASS_WITH_PRODUCTION_GSC_1_TO_GSC_4_AND_DOMAIN_COVERAGE_OPEN_INPUT`.

### GSC-6 — global hyperbolicity / Cauchy foliation

RF-L7 already closes the local principal-hyperbolicity and Cauchy-data contract and explicitly types the stronger global geometry premise.

State:

`OPEN_SEPARATE_RF_L7_GATE`.

This coordinate is not promoted by RF-E26.

## 5. Minimal remaining line

```text
GSC-1 actual spatial realization
GSC-2 actual event-clock realization
GSC-3 actual regular smooth clock witness
GSC-4 actual shared Lorentzian atlas
             |
             v
RF-E26 certifier + explicit domain coverage
             |
             v
GSC-5 production global Einstein carrier

separate stronger gate:
GSC-6 global Cauchy foliation / global hyperbolicity
```

The theorem/certifier layer through GSC-5 is therefore structurally defined and hosted-validated. The remaining closure is data/realization promotion plus the separate GSC-6 global-causality theorem/witness line.

## 6. Authority and promotion firewall

This audit adds no canonical claim and does not mutate:

- `dependency_graph.yaml`;
- `claims.jsonl`;
- `source_export_heads.yaml`;
- `source_exports.lock.json`;
- source-owned `DEPENDENCY_EXPORT.json` files.

Canonical promotion remains governed by the current FPDG v0.4 source-federation and freshness procedures.

GREMLIN may audit dependency candidates and contradictions with `promotion_authority=false`.

Forbidden overall promotions while production inputs or GSC-6 remain open include:

- `GLOBAL_GR_PASS`;
- `GLOBAL_SPACETIME_REALIZATION_PASS`;
- `GLOBAL_HYPERBOLICITY_PASS`.

## 7. Overall verdict

\[
\boxed{
\begin{aligned}
&\text{LOCAL EINSTEIN FORM} &&= \text{PASS},\\
&\text{SPATIAL CERTIFIER} &&= \text{PASS},\\
&\text{TEMPORAL EXACTNESS CERTIFIER} &&= \text{PASS},\\
&\text{REGULAR CLOCK EXTENSION CERTIFIER} &&= \text{PASS},\\
&\text{LOCAL TEMPORAL FOLIATION} &&= \text{PASS},\\
&\text{SHARED ATLAS CERTIFIER} &&= \text{PASS},\\
&\text{GLOBAL EINSTEIN CARRIER CERTIFIER} &&= \text{PASS},\\
&\text{PRODUCTION GLOBAL SPACETIME REALIZATION} &&= \text{OPEN INPUT},\\
&\text{GLOBAL HYPERBOLICITY} &&= \text{OPEN SEPARATE GATE}.
\end{aligned}
}
\]

Machine-readable companion:
`receipts/GLOBAL_SPACETIME_CLOSURE_LEDGER_V0_2.json`.

Fail-closed test:
`tests/test_global_spacetime_closure_ledger_v0_2.py`.
