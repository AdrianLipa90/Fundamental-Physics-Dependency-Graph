# Global Spacetime Closure Ledger v0.1

Status: `LOCAL_EINSTEIN_FORM_PASS / SPATIAL_INPUT_CONTRACT_PASS / TEMPORAL_INPUT_CONTRACT_PASS / REGULAR_CLOCK_EXTENSION_CERTIFIER_PASS / SHARED_ATLAS_CERTIFIER_PASS / PRODUCTION_GLOBAL_SPACETIME_OPEN / GLOBAL_HYPERBOLICITY_OPEN`

Date: 2026-08-31

Authority: `NONCANONICAL_CROSS_REPO_AUDIT`. Source claims remain owned by TIR, IDT and RFC. `promotion_authority=false`.

## 1. Current dependency surface

```text
TIR local tetrahedral geometry
 -> TIR A5 global 3-manifold certifier
 -> TIR GSC-1 spatial input contract
 -> actual production tetrahedral incidence dataset OPEN

IDT 00F prefix occurrences
 -> IDT 05J explicit occurrence-to-event quotient/input contract
 -> IDT 05H exact event-clock certifier
 -> actual production event incidence/quotient dataset OPEN
 -> IDT 05I regular smooth-clock extension certifier
 -> actual production continuum clock witness/coverage OPEN
 -> IDT 05G positive-lapse Frobenius foliation

TIR spatial realization
 + IDT regular clock/foliation
 + RFC ADM coframe
 -> RFC RF-E25 shared atlas/coframe cocycle certifier
 -> actual production shared spacetime atlas OPEN

RFC RF-E24 local Einstein field-equation form
 + production PASS GSC-1..GSC-4
 -> GSC-5 global Lorentzian domain carrying RF-E24

stronger downstream causal/PDE gate
 -> GSC-6 global hyperbolicity / Cauchy foliation
```

GSC-1 and GSC-2 now have executable source-owned input contracts. Their production datasets remain open.

## 2. TIR spatial geometry and GSC-1

Repository: `AdrianLipa90/The-Fundamental-Theory-of-Informational-Relations`.

Current main baseline used for the input contract: `62a13ba92f0db641d6d699a88059aedf33528300`.

A5 global 3-manifold/smooth-realization certifier remains the topology authority for a supplied tetrahedral complex. Its earlier validated research head `2568fb24e0bc91e8f1c75dcfdc5659a57ca382b9` has hosted SUCCESS run `33331003616`.

GSC-1 input-contract branch:
`feat/tir-global-spatial-complex-input-contract-v0.1`.

Exact head:
`5aaf572e9e931525f16bb0fa105afbb0d34c59c9`.

Hosted `TIR global spatial-complex input contract`, run #1, id `33343473631`: `SUCCESS`.

The contract requires explicit dataset provenance, canonical incidence SHA-256, unique vertex identifiers and a closed tetrahedral-complex representation before handing the incidence table to A5. Reference `boundary(Delta^4)=S^3` data are frozen with `production=false`.

Verdict:

`INPUT_CONTRACT_PASS_WITH_PRODUCTION_SPATIAL_COMPLEX_OPEN_INPUT`.

## 3. IDT temporal geometry and GSC-2/GSC-3

Repository: `AdrianLipa90/Informational-Dynamics-of-Time`.

Current main baseline used for 05J: `f186aab6024a592be406684785069edfe2f3d5bf`.

### 3.1 05J — production event-complex input contract

Branch:
`feat/idt-production-event-complex-input-contract-v0.1`.

Exact head:
`44e2da0a7048df387f277f4e93e6970c445d4b67`.

Hosted `IDT 05J production event-complex input`, run #1, id `33343481792`: `SUCCESS`.

05J requires a supplied set of realized occurrence IDs and an explicit partition

\[
q:O\to E
\]

into event classes. Directed event edges carry positive finite elapsed increments and unique source-relation provenance IDs. A canonical SHA-256 binds the occurrences, quotient classes and edge incidence.

After structural/integrity validation, 05J passes the event graph directly to 05H. A temporal-holonomy failure remains an exactness failure rather than being hidden as an input parser failure.

Verdict:

`INPUT_CONTRACT_PASS_WITH_PRODUCTION_EVENT_COMPLEX_OPEN_INPUT`.

### 3.2 05H — exact discrete event clock

05H certifies

\[
\vartheta=\delta t
\quad\Longleftrightarrow\quad
\oint_C\vartheta=0
\]

on the supplied connected event graph. The production event complex remains required through 05J.

### 3.3 05I — regular smooth clock-extension witness

05I is maintained on the parallel research branch `feat/idt-temporal-foliation-v0.1`.

Exact hosted-PASS head:
`fc87c4176dfcc480529ba28bd67042d3ebf02c72`.

Dedicated `IDT 05I regular smooth clock extension`, run #2, id `33339841644`: `SUCCESS`.

It certifies a supplied compatible affine-chart scalar witness

\[
t_p(x)=a_p\cdot x+b_p,\qquad a_p\neq0,
\]

with overlap/cocycle and event-embedding compatibility. Production continuum witness and domain coverage remain open.

Verdict:

`CERTIFIER_PASS_WITH_PRODUCTION_REGULAR_CLOCK_WITNESS_OPEN_INPUT`.

### 3.4 05G — positive-lapse foliation

On a supplied regular clock domain,

\[
\Theta_R=N_Rc\,dt,\qquad N_R>0
\]

gives

\[
\Theta_R\wedge d\Theta_R=0.
\]

05I owns the regular smooth-clock witness gate feeding this theorem.

### 3.5 Independent IDT full-suite blocker

The 05J exact-head repository-wide Reference suite #935, id `33343481782`, fails during collection because the seam stack imports a missing `onsager_dissipation` symbol from `idt.schrodinger_onsager_seam_balance`. The same failure class pre-dates 05J. It is retained as an independent repository-maintenance blocker and does not replace the dedicated 05J or 05I verdicts.

## 4. RFC relativistic geometry

Repository: `AdrianLipa90/Relational-Field-Closure`.

RF-E24 exact head `5e8ca5e5aea4ecb63a3ea5fd005518fa63183d3d`, reference suite #390 id `33330773981`: `SUCCESS`.

On the admitted selected branch,

\[
G_{\mu\nu}+\Lambda g_{\mu\nu}=\kappa_E T_{\mu\nu},
\qquad \kappa_E=\frac{8\pi G}{c^4}.
\]

RF-E25 exact head `4d581ac8d03e637f65fdefa2b9326ffc1effe0e1`, reference suite #392 id `33337181002`: `SUCCESS`.

The shared-atlas gate checks coframe/coordinate compatibility, Lorentz metric preservation, orientation/time orientation, overlap connectedness and coordinate/frame cocycles.

Verdict:

`CERTIFIER_PASS_WITH_PRODUCTION_SHARED_ATLAS_OPEN_INPUT`.

## 5. Closed theorem/certifier/interface surfaces

| Surface | Verdict |
|---|---|
| TIR local Cartan/Levi-Civita geometry | `PASS` |
| TIR global 3-manifold/smooth-realization certifier | `PASS` |
| TIR GSC-1 global spatial input contract | `PASS` |
| IDT event-clock exactness theorem/certifier | `PASS` |
| IDT 05J production event-complex input contract | `PASS` |
| IDT 05I regular smooth clock-extension certifier | `PASS` |
| IDT positive-lapse Frobenius theorem/certifier | `PASS` |
| RFC local Einstein field-equation form | `PASS_ON_DECLARED_SELECTION_RULES` |
| RFC shared-spacetime atlas/coframe cocycle certifier | `PASS` |

## 6. Remaining production frontier

### GSC-1 — production spatial complex

Contract/certifier state:
`INPUT_CONTRACT_PASS_WITH_PRODUCTION_SPATIAL_COMPLEX_OPEN_INPUT`.

Remaining datum: actual source-owned global TIR tetrahedral incidence dataset with provenance/digest, followed by A5 PASS.

### GSC-2 — production temporal event complex

Contract/certifier state:
`INPUT_CONTRACT_PASS_WITH_PRODUCTION_EVENT_COMPLEX_OPEN_INPUT`.

Remaining datum: actual source-owned IDT occurrence set, occurrence-to-event quotient, directed event incidence and elapsed-edge values, followed by 05H PASS.

### GSC-3 — regular smooth clock extension

State:
`CERTIFIER_PASS_WITH_PRODUCTION_REGULAR_CLOCK_WITNESS_OPEN_INPUT`.

### GSC-4 — shared spatial-temporal spacetime realization

State:
`CERTIFIER_PASS_WITH_PRODUCTION_SHARED_ATLAS_OPEN_INPUT`.

### GSC-5 — global carrier for RF-E24

State:
`CONDITIONAL_ON_PRODUCTION_PASS_GSC_1_TO_GSC_4`.

### GSC-6 — global hyperbolicity / Cauchy foliation

State:
`OPEN_SEPARATE_GATE`.

## 7. Minimal remaining closure line

```text
GSC-1 actual spatial incidence      -> TIR input contract -> A5
GSC-2 actual event quotient/data    -> IDT 05J -> 05H
GSC-3 actual smooth clock witness   -> IDT 05I -> 05G
GSC-4 actual shared 4D atlas        -> RFC RF-E25
---------------------------------------------------------
production PASS of GSC-1..4
 -> GSC-5 global domain carrying RF-E24

stronger downstream:
GSC-6 global hyperbolicity / Cauchy foliation
```

The remaining GSC-1..GSC-4 coordinates are now typed production-realization inputs rather than undefined interfaces.

## 8. FPDG authority firewall

This ledger remains noncanonical while it cites draft feature heads. It leaves these canonical surfaces unchanged:

- `dependency_graph.yaml`;
- `claims.jsonl`;
- `source_export_heads.yaml`;
- `source_exports.lock.json`;
- source-owned `DEPENDENCY_EXPORT.json` snapshots.

Canonical promotion requires explicit source-side promotion and freshness procedures. GREMLIN may audit candidates and contradictions with `promotion_authority=false`.

## 9. Overall verdict

\[
\boxed{
\begin{aligned}
&\text{LOCAL EINSTEIN FORM} &&= \text{PASS},\\
&\text{GSC-1 INPUT CONTRACT} &&= \text{PASS; PRODUCTION DATA OPEN},\\
&\text{GSC-2 INPUT CONTRACT} &&= \text{PASS; PRODUCTION DATA OPEN},\\
&\text{GSC-3 CLOCK CERTIFIER} &&= \text{PASS; PRODUCTION WITNESS OPEN},\\
&\text{GSC-4 SHARED ATLAS CERTIFIER} &&= \text{PASS; PRODUCTION ATLAS OPEN},\\
&\text{GSC-5 GLOBAL EINSTEIN DOMAIN} &&= \text{CONDITIONAL},\\
&\text{GSC-6 GLOBAL HYPERBOLICITY} &&= \text{OPEN}.
\end{aligned}
}
\]

Machine-readable companion: `receipts/GLOBAL_SPACETIME_CLOSURE_LEDGER_V0_1.json`.

Fail-closed test: `tests/test_global_spacetime_closure_ledger.py`.
