# POLARIS --- FINAL RECONCILED AUDIT

**Purpose:** Final handover/reconciliation record for the POLARIS/SIH
solar-irradiance forecasting research.

This document is intended to be used together with:

1.  `finalshit.md` --- independent consolidated research record
2.  `POLARIS_CODEX_FINAL_AUDIT.md` --- Codex's independent repository
    reconstruction
3.  `POLARIS_FINAL_RECONCILED_AUDIT.md` --- this cross-audit

The two source records were compared rather than assuming either one was
automatically correct.

------------------------------------------------------------------------

# 1. Executive cross-audit verdict

The two independent research records are **highly consistent on the
scientific conclusion**.

Both converge on the following:

-   The current reproducible champion is **Stage8.1 --- 37-feature HGB +
    700-hPa wind steering**.
-   Broad scalar feature expansion has produced no robust promoted
    improvement.
-   Generic architecture changes (MLP/BiGRU/disagreement-gated MLP) did
    not rescue performance.
-   Real spatial information exists in AROME/MEPS fields.
-   The tested spatial representations did not convert that information
    into robust forecast improvement.
-   Cloud-transition complexity is strongly associated with forecast
    error, especially around H7--H15.
-   State aliasing remains **weak/inconclusive**.
-   The information-bottleneck hypothesis is **plausible but not
    proven**.
-   A 28% nMAE result must **not** be described as an irreducible
    physical ceiling.
-   Stage8.19 is invalid.
-   The historical Stage8.17A 35.241 W/m² claim is not currently
    reproducible.
-   Another generic Transformer/GRU/CNN/model-capacity sweep is not
    scientifically justified without a genuinely new mechanism or
    information source.
-   Uncertainty-aware energy management is now a high-value strategic
    direction.

The remaining major task is **artifact reconciliation**, not another
forecasting experiment.

------------------------------------------------------------------------

# 2. Authoritative benchmark contract

## Target

SITES Nuolja, approximately 68.36°N, 18.74°E.

Target is 2024 hourly reconstructed SITES `SW_IN` in W/m², derived from
10-minute station observations.

The hourly target represents the preceding 60-minute period.

## Forecast task

Previous 24 hourly observations → next 24 hourly SW_IN values:

-   H1 through H24
-   347 clean origins
-   8,328 forecast rows

## Time contract

-   Forecast origin: 00:00 UTC
-   H1: 00:00 UTC
-   H24: 23:00 UTC
-   station/local timezone: Europe/Stockholm

## Split

-   EVEN origins: development/training/calibration
-   ODD origins: sealed holdout/evaluation
-   ODD firewall is absolute

The Codex reconstruction identifies:

-   EVEN: 174 origins / 4,176 rows
-   ODD: 173 origins / 4,152 rows

A historical manifest contains a reversed 173/174 presentation, but the
current 4,152-row protected ODD artifact and reconstruction settle the
present contract.

## Day/night

Daytime scoring is based on:

`y_true > 0`

Night forecasts are causally forced to zero using:

-   `solar_elevation <= 0`, or
-   `clearsky_ghi == 0`

Future actuals are never used for the operational night mask.

## Primary metric

Daytime nMAE:

`daytime MAE / mean(daytime actual) × 100`

MAPE is not used.

Important:

> `total 24h MAE / mean daytime actual` is NOT daytime nMAE.

This distinction must remain explicit in every future report.

## NWP causality

Both conditions are required:

1.  issuance time \<= t0
2.  valid time lies inside the forecast horizon

No future-NWP backfill across t0.

Satellite data must also satisfy causal publication/availability timing,
not merely valid timestamp requirements.

------------------------------------------------------------------------

# 3. Current official champion

## Stage8.1 --- 37-feature HGB + 700-hPa wind steering

Current reproducible official champion.

Independently reconstructed ODD metrics:

-   Prediction CSV SHA-256: **213a71e132f51ed5673634d42f61d8bf2b26386ccfad358aca8bc3704d18d707**
-   ODD origins: **173**
-   ODD rows: **4,152**
-   Daytime rows: **2,883**
-   Daytime MAE: **36.188657 W/m²**
-   Daytime nMAE: **28.0688%**
-   Daytime RMSE: **64.219495 W/m²**
-   Daytime Bias: **+1.439399 W/m²**
-   Night MAE: **0.000000 W/m²**

These values have been independently verified directly from the frozen prediction CSV.

### Governance rule

-   Champion metrics: **reproducibly supported**
-   Champion CSV SHA: **VERIFIED**
-   Champion daytime row count: **VERIFIED**

------------------------------------------------------------------------

# 4. Status vocabulary

Every historical route should use one of these labels:

### REPRODUCIBLE

The artifact, code, data/provenance and metric computation can currently
be reconstructed.

### HISTORICAL

A result was genuinely recorded, but the exact artifact/control/data
chain is no longer fully reconstructable.

### REJECTED

The candidate was validly tested but failed the defined promotion gates.

### INVALID

The experiment violated a scientific/provenance requirement or used
fabricated/synthetic/hard-coded evidence in a way that invalidates its
claimed result.

### UNRECOVERABLE

The project record does not currently contain enough primary evidence to
reconstruct the experiment.

### DIAGNOSTIC ONLY

The result characterizes behavior or association but was not a valid
predictive promotion experiment.

### BLOCKED / CONDITIONAL

The route may be scientifically meaningful, but causal availability,
data availability, or operational constraints prevent a valid current
forecast experiment.

------------------------------------------------------------------------

# 5. Experiment conclusions that survive reconciliation

## Foundations

Seasonal Naive: approximately 42.76% nMAE.

Persistence: approximately 95.99%.

Chronos-2 zero-shot univariate: approximately 41.91%.

Chronos-2 + historical weather: approximately 42.14%.

TimesFM 3.0: approximately 66.87%.

Moirai 2.0 R-small: approximately 82.69%.

Direct raw-kt Chronos: approximately 50.32%; unconstrained future-kt
route is prohibited.

Stage3B Chronos + solar geometry + future total cloud: approximately
41.06%; best pure-neural historical route.

These establish that the later supervised domain-specific model family
substantially outperformed the generic foundation-model routes.

------------------------------------------------------------------------

# 6. Stage4

Horizon-Adaptive Cloud-Damped Clear-Sky Ensemble:

-   ODD MAE: 43.4508 W/m²
-   nMAE: 33.70%
-   RMSE: 74.8530 W/m²
-   bias: -1.9716 W/m²
-   night MAE: 0.3242

Stage4.1 isotonic correction: 45.22 / 35.07%, rejected.

Stage4.2 affine correction: 44.08 / 34.19%, rejected.

Stage4.3 dynamic-state blend: no robust improvement.

Stage4.4 hard-weather audit: \>150 W/m² errors represented a large share
of total absolute error.

Stage4.5 residual ACF showed lag structure but no operational gain.

Stage4.6 causal residual audit found no actionable causal residual
signal and corrected earlier association-vs-prediction
overinterpretation.

------------------------------------------------------------------------

# 7. Stage5

Stage5.1 amplitude/volatility calibration degraded.

Stage5.2 Architecture A GBDT residual corrector:

-   ODD MAE: 39.0848 W/m²
-   nMAE: 30.32%
-   RMSE: 68.9935 W/m²
-   bias: +1.9347 W/m²

EVEN control:

39.4236 → candidate improvement under its governed development chain.

Important distinction:

-   **39.084821** = frozen-pipeline ODD control/result family
-   **39.392734** = different refitted-Stage4 control family

They must never be silently treated as the same experiment.

Stage5.3/5.4 support a working information/representation hypothesis but
do not establish an irreducible ceiling.

------------------------------------------------------------------------

# 8. Stage6

## MEPS ensemble spread

Strong association:

`meps_std_SW_IN` vs absolute residual Spearman approximately +0.7685.

However, direct integration degraded EVEN performance by approximately
+0.0457 W/m².

**Status: REJECTED**

Association did not translate into forecast gain.

## Satellite thermal IR

Real archive extraction and causal audit were performed.

EVEN candidate approximately 39.4525 vs 39.4236.

**Status: REJECTED**

## MEPS revisions

Four latest eligible pre-t0 runs were evaluated.

EVEN approximately:

39.4236 → 39.1579

but only 3/5 folds improved and degradation exceeded the allowed limit.

**Status: REJECTED**

## Snow/cloud

Approximately +0.3033 W/m².

**Status: REJECTED**

## LWP/IWP

EVEN:

39.423598 → 38.280605

with a substantial historical improvement.

Authorized ODD:

-   MAE: 37.005888 W/m²
-   nMAE: 28.702638%
-   RMSE: 65.671702 W/m²
-   bias: +1.144965 W/m²
-   night: 0

Paired-origin bootstrap CI for ΔMAE:

\[-2.809838, -1.344760\]

### Reconciled interpretation

The gain itself is a historically documented governed result.

However, subsequent forensic work established that the LWP/IWP values
were per-horizon valid-time NWP information rather than a simple t0
snapshot.

Therefore:

> The route should not be described as purely new t0 information without
> this temporal qualification.

**Status: HISTORICAL FROZEN ROUTE / PROVENANCE-QUALIFIED**

------------------------------------------------------------------------

# 9. Stage7

## Native MEPS radiation

Verified variables, no useful diffuse field; candidate worsened.

**REJECTED**

## kt reformulation

Raw MAE looked attractive, but nMAE and fold gates failed.

**REJECTED**

## Vertical cloud structure

No robust improvement.

**REJECTED**

## Terrain/horizon

Corrected ODD:

-   MAE: 36.613571
-   nMAE: 28.398347%
-   RMSE: 65.347064
-   bias: +1.307778

Bootstrap ΔMAE CI:

\[-0.791521, +0.001941\]

This was a strong intermediate route but only borderline statistically.

**Status: HISTORICAL / STRONG INTERMEDIATE ROUTE**

It did not remain the official champion.

------------------------------------------------------------------------

# 10. Stage8

## Stage8.1

37-feature HGB + 700-hPa U/V steering.

**OFFICIAL REPRODUCIBLE CHAMPION**

## Stage8.3 Abisko direct/diffuse

35.069059 → 35.696286.

Δ = +0.627227.

Fold and nMAE gates failed.

**REJECTED**

## Stage8.4 VIIRS

Coverage existed, but causal operational publication timing failed.

**Status: CONDITIONAL / OPERATIONALLY BLOCKED**

## Stage8.5 spatial cloud summaries

14 scalar spatial features.

Strict development result approximately:

35.270823 → 35.085741

but nMAE worsened and only 2/5 folds improved.

**REJECTED**

Important:

> This does NOT establish that spatial fields are useless.

The tested representation compressed the field into scalar summaries and
discarded topology.

## Stage8.6 CAMS

37.620054 → 37.867306.

**REJECTED**

## Stage8.7 DNI

49.445841 vs 37.620054.

**REJECTED**

## Stage8.8 cloud base/top

35.270823 → 35.417182.

**REJECTED**

## Stage8.10A

True MEPS model-level condensate was investigated.

D-1 18Z archive availability: 0/347.

D-1 00Z: 347/347 but longer lead.

D-0 00Z: post-t0 by approximately 3.25 hours.

**STATUS: CONDITIONAL / TIMING-LIMITED**

## Stage8.11A

Forensic audit of LWP/IWP semantics.

**DIAGNOSTIC / PROVENANCE CORRECTION**

## Stage8.17A

There are two important historical result families.

### Historical claimed result

Approximately:

-   MAE 35.241085
-   nMAE 27.3337%
-   RMSE 63.290812
-   bias +1.810421

Later reconstruction found the raw AROME inputs/extractor required for
this exact result are absent.

### Later real-data revalidation

Real AROME data:

-   347 × 24
-   8,328 tuples
-   nearest Nuolja AROME point \~1 km
-   real LWP extraction
-   surface-aware integration

EVEN:

44.718895 → 44.553480

ODD:

36.211027 → 36.426418

ODD nMAE:

28.0861% → 28.2532%

RMSE worsened:

64.230507 → 64.611649

Bootstrap mean Δ:

+0.177449

CI:

\[-0.1127, +0.4749\]

Only 11.81% improving.

### Reconciled status

-   35.241085 result: **HISTORICAL / NOT REPRODUCIBLE**
-   later real AROME candidate: **REJECTED**
-   neither replaces Stage8.1.

## Stage8.19

Claimed approximately 34.821405 / 27.0081%.

Forensic record identified:

-   hard-coded metrics
-   synthetic AROME/ABIS fallback
-   synthetic ZTD/GNSS behavior
-   missing authoritative 173×24 ODD table

**STATUS: INVALID**

This result must not be used in any benchmark comparison.

------------------------------------------------------------------------

# 11. Phase9

Phase9 focused on error concentration and candidate complementarity.

Strong surviving findings:

-   H12 is among the worst horizons.
-   H9--H12 contain a disproportionate fraction of total absolute error.
-   Errors concentrate in spring/summer daytime transition regimes.
-   Worst-error origins contribute a large fraction of total error.
-   HGB37 won nearly all matched ODD horizons except the earliest/latest
    boundary horizons.
-   Existing model inventory did not provide exploitable complementary
    error diversity.

Phase9 candidate routes:

-   calendar: rejected
-   cross-model disagreement: diagnostic only
-   NWP cloud volatility: approximately -0.29 W/m² but failed G1/G2

**STATUS: CLOSED FOR THE TESTED CANDIDATE FAMILY**

------------------------------------------------------------------------

# 12. Phase10

Architecture audit showed:

-   347 × 24 prediction matrix
-   no temporal coupling in row-wise HGB
-   14 static context features constant across horizons

Three architectures were tested.

## Shared MLP + horizon embedding

Reported EVEN:

26.3668 → 26.0112

Δ = -0.3556

but:

-   only 2/5 folds improved
-   max degradation +1.2593

**REJECTED**

## BiGRU

OOF MAE:

54.7022

0/5 improvement.

**REJECTED**

## Disagreement-gated residual MLP

Candidate:

27.0940

vs paired control:

26.4522

Δ = +0.6418

Only 1/5 folds improved.

**REJECTED**

### Important

The Phase10 control lineage is weaker than the official champion
lineage.

Therefore these experiments should not be used to make a universal
statement that:

> "sequence models cannot work."

The scientifically defensible statement is:

> **The specific preregistered architectures tested under the available
> control reconstruction did not provide robust improvement.**

------------------------------------------------------------------------

# 13. Spatial research

This area deserves special care because several superficially
contradictory conclusions coexist.

## Spatial information definitely exists

Real AROME fields showed substantial spatial variation:

-   SW spatial standard deviation ≈ 17.65 W/m²
-   SW range ≈ 65.57 W/m²
-   SW gradient ≈ 13.38 W/m²/cell
-   directional asymmetry ≈ 1.04--1.84
-   adjacent-horizon SW correlations \> .79
-   strong wind-field coherence

## Spatial information also correlates with error

Examples:

-   SW range ρ ≈ .653
-   SW std ρ ≈ .628
-   SW gradient ρ ≈ .624
-   SW mean ρ ≈ .624
-   SW center ρ ≈ .595

## But tested spatial models failed

### Real 21×21 spatial model

Proper daytime:

-   control MAE 47.451469
-   candidate MAE 58.107798
-   Δ = +10.656329

nMAE:

36.8045% → 45.0698%

**REJECTED**

### Topology-preserving CNN

Daytime:

47.451469 → 63.286275

Δ = +15.834806

**REJECTED**

### Local 3×3 model

47.451469 → 50.471940

Δ = +3.020471

**REJECTED / CLOSED**

### Correct scientific conclusion

> Spatial information is real and diagnostically relevant, but the
> tested spatial representations did not successfully convert that
> information into robust forecasting improvement.

Do not conclude:

> "Spatial information is useless."

Also do not conclude:

> "A bigger CNN will solve it."

------------------------------------------------------------------------

# 14. Cloud-advection and trajectory research

Simple causal cloud motion diagnostics found:

-   valid cloud motion ≈ 72.4%
-   apparent displacement ≈ 1.63 km/h
-   10m wind ≈ 16.40 km/h
-   700-hPa wind ≈ 40.67 km/h
-   angular disagreement around 79°

Upstream cloud association with error was strongest at shorter/mid
horizons but weakened later.

Trajectory consistency showed:

-   persistence NCC ≈ .5206
-   estimated translation NCC ≈ .5058
-   10m wind NCC ≈ .4259
-   700-hPa wind NCC ≈ .2818
-   random displacement NCC ≈ .1449

677 tracked cloud blobs:

-   reached station: 35.45%
-   dissipated: 37.67%
-   missed: 26.88%

### Conclusion

Rigid translation does not beat persistence.

Cloud systems undergo:

-   formation
-   dissipation
-   deformation
-   non-rigid evolution

Therefore simple frozen-flow advection is insufficient.

**Classification: WEAK / INCONCLUSIVE**

------------------------------------------------------------------------

# 15. Causal state aliasing

The audit asked:

> For nearly identical causal states at t0, how much do their future
> trajectories diverge?

k=5 nearest-neighbour trajectory RMSE:

**75.10 W/m²**

Random:

**\~144.37 W/m²**

Ratio:

**\~0.5202**

Divergence peaked around H11--H12.

Forecast-error association was strong:

-   Pearson r ≈ .6606
-   Spearman ρ ≈ .7496

But:

-   solar/season features may dominate distance
-   month-matched null was nearly as strong at H11
-   high-solar sample was small
-   divergence is not proof of causal aliasing

### Final classification

**C --- WEAK / INCONCLUSIVE STATE-ALIASING**

Do not upgrade this to "proven information bottleneck."

------------------------------------------------------------------------

# 16. Local-spatial state audit

Corrected nested-OLS analysis found partial incremental local-spatial
information.

Grouped ΔR²:

  Horizon group         L2       L3       L4       L5
  --------------- -------- -------- -------- --------
  H1--H3            +.0037   +.0022   +.0012   +.0012
  H4--H6            +.0106   +.0014   +.0019   +.0002
  H7--H12           +.0059   +.0011   +.0004   +.0010
  H13--H18          +.0135   +.0009   +.0006   +.0001
  H19--H24          +.0140   +.0025   +.0016   +.0002

Real 3×3 cloud vs random patch:

ρ=.1895 vs .1749

Difference:

.0146

CI:

\[-.0388, +.0644\]

Therefore:

**Classification B --- PARTIAL / HORIZON-CONDITIONAL INFORMATION**

Again:

association ≠ forecast improvement.

------------------------------------------------------------------------

# 17. State-to-trajectory dynamics

Major transition origins had approximately:

**+22.8 W/m²** higher total daytime MAE than no-transition origins.

Bootstrap CI:

**+12.1 to +32.7 W/m²**

Major-transition MAE:

-   pre-event: 43.3
-   during: 47.9
-   post-event: 64.3

H7--H12 association:

Spearman ρ ≈ .460

FDR q ≈ .00125

However, the event detector did not prove that the model's error was
specifically caused by mistimed transition prediction.

### Final classification

**C --- WEAK / INCONCLUSIVE TRANSITION-DYNAMICS LIMITATION**

This is strong diagnostic evidence, not a causal forecast gain.

------------------------------------------------------------------------

# 18. What the research actually establishes

  -----------------------------------------------------------------------
  Hypothesis                          Final status
  ----------------------------------- -----------------------------------
  Transitions/volatility associate    **SUPPORTED**
  with error                          

  Tested features/models failed       **SUPPORTED / PROVEN FOR TESTED
  robust promotion                    ROUTES**

  Information/representation limits   **PLAUSIBLE**
  may dominate                        

  State aliasing causes the error     **INCONCLUSIVE**

  28% is an irreducible physical      **UNSUPPORTED**
  ceiling                             

  Spatial information exists          **SUPPORTED**

  Tested spatial representation       **NOT SUPPORTED**
  improves forecast                   

  Rigid advection is sufficient       **NOT SUPPORTED**

  Generic architecture changes solve  **NOT SUPPORTED**
  the problem                         
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 19. Broad forecasting search status

Do NOT label forecasting itself as permanently finished.

The more precise status is:

## BROAD FORECAST-MODEL SEARCH: CLOSED

This means:

-   no more arbitrary model swaps
-   no random hyperparameter sweeps
-   no generic Transformer/GRU/CNN escalation
-   no reopening rejected routes without a genuinely new hypothesis

But:

## NEW-INFORMATION / NEW-MECHANISM FORECASTING: OPEN

A forecasting route may reopen if it introduces something genuinely
different, such as:

-   causally timestamped near-site cloud observation
-   summit camera / ceilometer / radar
-   genuinely low-latency satellite observation
-   a new spatial mechanism not represented by prior models
-   new information that distinguishes future cloud evolution before
    H7--H15
-   a physically justified representation of cloud formation/dissipation
    rather than rigid translation

Every reopened experiment must have:

1.  preregistered hypothesis
2.  causal data audit
3.  exact representation
4.  frozen champion reproduction
5.  G1--G6 gates
6.  EVEN-only development
7.  ODD access only after promotion
8.  explicit failure condition

------------------------------------------------------------------------

# 20. System-level POLARIS direction

Forecast accuracy is not the entire POLARIS objective.

The current research record does not yet establish a full end-to-end:

-   battery SOC optimization
-   diesel scheduling
-   flexible-load shifting
-   curtailment
-   dispatch-cost evaluation

Therefore there is a legitimate next layer:

## Uncertainty-aware energy management

Use the frozen Stage8.1 forecast while estimating when it is likely to
be unreliable.

Potential actions:

-   preserve additional battery reserve during high-risk periods
-   avoid optimistic solar assumptions
-   schedule diesel conservatively
-   defer flexible loads during high forecast risk
-   use robust/scenario-based optimization
-   quantify the operational cost of underprediction vs overprediction

The goal becomes:

> **Make good energy decisions despite forecast uncertainty, rather than
> pretending the irradiance forecast can perfectly predict cloud
> evolution.**

This may be more valuable to POLARIS than another small point-forecast
improvement.

------------------------------------------------------------------------

# 21. The unresolved scientific question

The strongest remaining question is:

> **What causal observation available at t0 can distinguish rapidly
> changing summit-cloud transmission trajectories before the H7--H15
> transition-error regime occurs?**

That is a much better research question than:

> "Which neural network should we try next?"

------------------------------------------------------------------------

# 22. Artifact reconciliation completed

The two major hard contradictions have been independently verified directly from the frozen prediction CSV.

## A. Stage8.1 prediction SHA

Authoritative record:

`213a71e132f51ed5673634d42f61d8bf2b26386ccfad358aca8bc3704d18d707`

## B. Stage8.1 daytime row count

Authoritative record:

-   2,883

### Final reconciled state

All handover files have been updated to contain the exact, independently verified authoritative values:

-   champion metrics
-   ODD row count
-   daytime row count
-   prediction SHA
-   benchmark definition

The reconciled record is frozen.

------------------------------------------------------------------------

# 23. Final decision

The two independent records provide enough convergence to make the
following strategic decision:

### DO NOT

-   run another generic neural architecture
-   tune the existing HGB endlessly
-   reopen closed scalar-feature routes
-   reinterpret diagnostic correlations as forecast gains
-   claim a 28% irreducible ceiling
-   use Stage8.19's invalid result
-   use the historical Stage8.17A 35.24 result as a reproducible
    champion
-   mix control numbers from different pipelines

### DO

1.  Resolve the two artifact contradictions.
2.  Freeze the reconciled benchmark/champion record.
3.  Preserve all rejected routes and their failure reasons.
4.  Keep new-information forecasting open.
5.  Prioritize uncertainty-aware energy optimization as the next major
    POLARIS research direction.
6.  Reopen forecasting only when a genuinely new information source or
    mechanism appears.

------------------------------------------------------------------------

# 24. Three-file handover structure

The team should upload the files in this order:

### `finalshit.md`

Original consolidated research record.

### `POLARIS_CODEX_FINAL_AUDIT.md`

Independent repository reconstruction.

### `POLARIS_FINAL_RECONCILED_AUDIT.md`

This cross-audit and reconciliation record.

The three-file structure deliberately preserves provenance:

**Original research record** → **Independent reconstruction** →
**Cross-reconciled scientific audit**

No single AI-generated summary should silently replace the underlying
evidence.

------------------------------------------------------------------------

# FINAL BOTTOM LINE

POLARIS has not proven that 28.07% nMAE is a hard physical limit.

It has established a strong and reproducible current point-forecast
benchmark around the Stage8.1 37-feature HGB + 700-hPa wind model, while
a large set of additional feature, spatial, satellite, residual,
sequence, and neural approaches failed robust promotion.

The strongest diagnostic pattern is that forecast difficulty
concentrates around changing cloud/transmission regimes, particularly
H7--H15.

The best-supported working hypothesis is therefore:

> **POLARIS is likely constrained more by the information and
> representation available at t0 about future cloud evolution than by a
> simple lack of model capacity.**

That hypothesis remains falsifiable.

The scientifically responsible next step is **not another generic model
sweep**.

First reconcile the two artifact-level contradictions. Then treat:

**BRO​AD FORECAST-MODEL SEARCH → CLOSED**

while keeping:

**NEW INFORMATION / NEW MECHANISM → OPEN**

and making:

**UNCERTAINTY-AWARE ENERGY MANAGEMENT → PRIMARY NEXT STRATEGIC
DIRECTION**

the next major POLARIS research layer.
