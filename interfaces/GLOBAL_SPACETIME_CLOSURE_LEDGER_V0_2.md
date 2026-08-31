# Global Spacetime Closure Ledger v0.2

Status: `LOCAL_EINSTEIN_FORM_PASS / SPATIAL_3M_CERTIFIER_PASS / TEMPORAL_EXACTNESS_CERTIFIER_PASS / REGULAR_CLOCK_EXTENSION_CERTIFIER_PASS / LOCAL_TEMPORAL_FROBENIUS_PASS / SHARED_ATLAS_CERTIFIER_PASS / GLOBAL_EINSTEIN_CARRIER_CERTIFIER_PASS / GLOBAL_HYPERBOLICITY_CERTIFIER_PASS / PRODUCTION_GLOBAL_SPACETIME_REALIZATION_OPEN / PRODUCTION_GLOBAL_CAUSALITY_WITNESSES_OPEN`

Date: 2026-08-30

Authority: `NONCANONICAL_CROSS_REPO_AUDIT`. Source claims remain owned by TIR, IDT and RFC. `promotion_authority=false`.

This v0.2 ledger is based on FPDG main `1e5e46a214c141bb07aa422740038b10a38f57d8`, after the post-merge v0.4 federation and source-lock refresh. It records the currently hosted-validated theorem/certifier layer through all six global-spacetime gates while retaining production inputs as explicit promotion requirements.

## 1. Current closure chain

```text
TIR spatial theorem/certifier layer
  A5 global 3-manifold/smooth-realization certifier
  -> GSC-1 production spatial realization

IDT temporal theorem/certifier layer
  05H event-clock exactness
  -> GSC-2 production event complex
  -> 05I regular smooth-clock extension certifier
  -> GSC-3 production regular clock witness
  -> 05G positive-lapse Frobenius foliation

TIR + IDT + RFC local ADM geometry
  -> RF-E25 shared Lorentzian atlas/coframe cocycle certifier
  -> GSC-4 production shared spacetime atlas

RF-E24 local Einstein form
  + RF-E25 shared atlas
  + RF-E26 local-to-global tensor gluing certifier
  -> GSC-5 production global Einstein carrier

RF-E25/IDT global clock geometry
  + global finite lapse upper bound
  + complete ADM Wick metric
  -> RF-L8 completely-uniform-temporal certifier
  -> GSC-6 production global hyperbolicity / Cauchy foliation

full GR composition:
  production GSC-5 + production GSC-6
  -> global GR Cauchy carrier
```

The theorem/certifier definitions GSC-1 through GSC-6 are now explicit and hosted-validated at their cited source heads. The unresolved frontier is production realization and global analytic/topological witness supply.

## 2. Current repository heads

| Repository | Current main observed | Closure witness used here |
|---|---|---|
| TIR | `62a13ba92f0db641d6d699a88059aedf33528300` | A5 head `2568fb24e0bc91e8f1c75dcfdc5659a57ca382b9`; hosted run `33331003616` SUCCESS |
| IDT | `f186aab6024a592be406684785069edfe2f3d5bf` | 05I head `fc87c4176dfcc480529ba28bd67042d3ebf02c72`; dedicated run `33339841644` SUCCESS |
| RFC | `012d4aa790bca7d631caf5c8002bebaa3a07710a` | RF-E26 head `d9779608754aae294e3a37a5e5c9fef63ff37a39`, run `33341138133` SUCCESS; stacked RF-L8 head `329bdcf981245189b52cea81509bf983c0396668`, run `33341545793` SUCCESS |
| FPDG | `1e5e46a214c141bb07aa422740038b10a38f57d8` | this audit branch only |

The current-main entries and hosted theorem heads are intentionally separate. Current mains carry the federated source-export state; theorem heads freeze the exact validation witnesses consumed by this audit.

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

### RFC RF-E24 / RF-E25

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

plus shared-clock, orientation and cocycle gates.

State:

`LOCAL_EINSTEIN_FORM_PASS / SHARED_ATLAS_CERTIFIER_PASS / PRODUCTION_SHARED_ATLAS_OPEN_INPUT`.

### RFC RF-E26 — global Einstein carrier gluing

RF-E26 defines

\[
\mathcal R_p=G_p+\Lambda g_p-\kappa_E T_p
\]

and, under the RF-E25 overlap convention, checks

\[
X_p=J^TX_qJ,
\qquad X\in\{g,G,T,\mathcal R\},
\]

common `Lambda` and `kappa_E`, connected overlap incidence, patchwise zero residual, RF-E25 parent certification and explicit target-domain coverage.

Hence on a supplied covered atlas,

\[
\mathcal R|_{U_p}=0\ \forall p
\quad\Longrightarrow\quad
\boxed{\mathcal R=0}
\]

on the represented domain.

Exact head `d9779608754aae294e3a37a5e5c9fef63ff37a39`; full RFC reference suite #401, id `33341138133`: `SUCCESS`.

Verdict:

`PASS_RFE26_GLOBAL_EINSTEIN_CARRIER_CERTIFIER_WITH_PRODUCTION_INPUT_OPEN`.

### RFC RF-L8 — completely uniform relational clock

RF-L8 closes the GSC-6 theorem/certifier definition without inferring global geometry from local samples.

For the ADM metric

\[
g=-N^2dt^2+h_{ij}(dx^i+b^i dt)(dx^j+b^j dt),
\]

a future causal vector `v` with

\[
a=dt(v)>0,
\qquad
Y=X+ba
\]

obeys

\[
h(Y,Y)\le N^2a^2.
\]

Define the ADM Wick metric

\[
W=dt^2+h_{ij}(dx^i+b^i dt)(dx^j+b^j dt).
\]

If one certified global finite lapse bound exists,

\[
0<N\le N_{\max}<\infty,
\]

then

\[
W(v,v)\le(1+N_{\max}^2)a^2.
\]

With

\[
\varepsilon=(1+N_{\max}^2)^{-1/2},
\qquad
H=\varepsilon^2W,
\]

RF-L8 proves

\[
\boxed{dt(v)\ge\|v\|_H}
\]

for every future causal vector.

If the supplied `W` is complete, the constant rescaling `H` is complete. RF-L8 then invokes its typed external completely-uniform-temporal characterization to promote the supplied Lorentzian domain to global hyperbolicity and Cauchy foliation.

The external theorem is imported only after RFC/IDT certify the global premises. It does not supply the global lapse bound or Wick completeness.

Exact stacked head:

`329bdcf981245189b52cea81509bf983c0396668`.

Full RFC reference suite #402, id `33341545793`: `SUCCESS`.

Verdict:

`PASS_RF_L8_UNIFORM_TEMPORAL_GLOBAL_HYPERBOLICITY_CERTIFIER_WITH_COMPLETENESS_INPUT_OPEN`.

## 4. Global frontier

### GSC-1 — production spatial realization

Certifier: `TIR A5`.

State: `OPEN_INPUT`.

### GSC-2 — production temporal event complex

Certifier: `IDT 05H`.

State: `OPEN_INPUT`.

### GSC-3 — production regular smooth clock witness

Certifier: `IDT 05I`.

State:

`CERTIFIER_PASS_WITH_PRODUCTION_REGULAR_CLOCK_WITNESS_OPEN_INPUT`.

### GSC-4 — production shared spacetime atlas

Certifier: `RFC RF-E25`.

State:

`CERTIFIER_PASS_WITH_PRODUCTION_SHARED_ATLAS_OPEN_INPUT`.

### GSC-5 — production global Einstein carrier

Certifier: `RFC RF-E26`.

State:

`CERTIFIER_PASS_WITH_PRODUCTION_GSC_1_TO_GSC_4_AND_DOMAIN_COVERAGE_OPEN_INPUT`.

Production promotion requires GSC-1 through GSC-4 on one common realization, explicit target-domain coverage, and RF-E26 tensor/residual checks on that realization.

### GSC-6 — production global hyperbolicity / Cauchy foliation

Certifier: `RFC RF-L8`.

Certifier state: `PASS`.

Production promotion requires:

- production global Lorentzian carrier from the shared-atlas line;
- production global regular temporal clock;
- a certified global finite lapse upper bound `N_max`;
- an analytic/topological certificate that the ADM Wick metric `W` is complete.

Combined state:

`CERTIFIER_PASS_WITH_PRODUCTION_GLOBAL_LAPSE_BOUND_AND_WICK_COMPLETENESS_OPEN_INPUT`.

RF-L8 keeps nonlinear global stability separate.

## 5. Final composition and minimal remaining frontier

```text
GSC-1 actual spatial realization
GSC-2 actual event-clock realization
GSC-3 actual regular smooth clock witness
GSC-4 actual shared Lorentzian atlas
       |
       +--> RF-E26 + domain coverage
       |      -> GSC-5 production global Einstein carrier
       |
       +--> RF-L8 + global N_max + complete W
              -> GSC-6 production global hyperbolicity / Cauchy foliation

production GSC-5 + production GSC-6
       -> GLOBAL_GR_CAUCHY_CARRIER
```

The **certifier/theorem layer through all six GSC coordinates is structurally defined and hosted-validated**. The remaining global closure is now a production-witness problem:

1. actual spatial realization;
2. actual temporal event realization;
3. actual regular smooth clock witness;
4. actual shared spacetime atlas;
5. actual global domain coverage / Einstein carrier;
6. actual global finite lapse bound and Wick-metric completeness.

No reference control is promoted as a substitute for those production witnesses.

## 6. Authority and promotion firewall

This audit adds no canonical claim and does not mutate:

- `dependency_graph.yaml`;
- `claims.jsonl`;
- `source_export_heads.yaml`;
- `source_exports.lock.json`;
- source-owned `DEPENDENCY_EXPORT.json` files.

Canonical promotion remains governed by the current FPDG v0.4 source-federation and freshness procedures.

GREMLIN may audit dependency candidates and contradictions with `promotion_authority=false`.

Forbidden overall promotions while production inputs remain open include:

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
&\text{GLOBAL HYPERBOLICITY CERTIFIER} &&= \text{PASS},\\
&\text{PRODUCTION GLOBAL SPACETIME / CAUSAL WITNESSES} &&= \text{OPEN INPUT}.
\end{aligned}
}
\]

Machine-readable companion:
`receipts/GLOBAL_SPACETIME_CLOSURE_LEDGER_V0_2.json`.

Fail-closed test:
`tests/test_global_spacetime_closure_ledger_v0_2.py`.
