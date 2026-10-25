# POLARIS Stage8.1 → EMS V2 Mechanism Observability Wording Correction
## Documentation-Only Scientific Interpretation Lock

```yaml
V1 STATUS = ACCEPTED + FROZEN (Control: 4671.00 L, Treatment: 6447.44 L, Mean Delta: +10.2684 L)
V2 EXECUTION = VALID + COMPLETED (173 Origins, 4,152 Timesteps)
V2 RAW EVIDENCE = FROZEN (SHA256: 652a047dd272058527d0458fa32738a97cbf70d4aa8a2d59aeaa33b33183415a)
V2 FORENSIC AUDIT REFERENCE = POLARIS_STAGE8_1_EMS_V2_POST_EXECUTION_FORENSIC_AUDIT.md (Classification B)
GOVERNANCE ACTION = DOCUMENTATION-ONLY SCIENTIFIC INTERPRETATION LOCK
EMS MODIFICATION = NOT AUTHORIZED
ENGINEERING INTERVENTION = NOT AUTHORIZED
```

---

## 1. Executive Governance Statement

Following the completion of the V2 empirical replay execution and the subsequent read-only forensic acceptance audit (Classification B), this document establishes the **authoritative documentation-only scientific interpretation lock** for all Stage8.1 $\rightarrow$ EMS mechanism observability findings.

### Immutable Evidence Declaration:
The raw numerical evidence preserved in the following artifacts is **100% frozen, valid, and immutable**:
- `POLARIS_STAGE8_1_EMS_V2_EXECUTION_RAW.csv` (SHA256: `652a047d...`)
- `POLARIS_STAGE8_1_EMS_V2_EXECUTION.json` (SHA256: `97a1dec8...`)
- `POLARIS_STAGE8_1_EMS_V2_MECHANISM_ANALYSIS.csv` (SHA256: `7af2b56b...`)
- `POLARIS_STAGE8_1_EMS_V2_MECHANISM_ANALYSIS.json` (SHA256: `9b7867d6...`)

No source code, raw evidence, primary endpoints, or numerical metrics have been edited, recomputed, or modified. This task performs a **documentation-only wording alignment** to ensure all scientific interpretation statements strictly adhere to what the preserved raw evidence establishes.

---

## 2. Core Scientific Boundary

### Approved Overarching Framing:
> *"V2 provides timestep-level evidence identifying observed forecast-to-dispatch-to-storage/diesel pathways associated with the aggregate diesel difference. The experiment does not isolate the causal contribution of every individual pathway or forecast horizon."*

### Governing Distinction:
$$\text{OBSERVED TEMPORAL PATHWAY} \neq \text{UNIQUELY ISOLATED CAUSAL MECHANISM}$$

The V2 execution observed full receding-horizon trajectories across 173 paired origins. While temporal precedence and physical model constraints are directly observed, individual forecast horizons ($h=1, 2 \dots 24$) were not independently manipulated in isolation. Scientific claims are bounded accordingly.

---

## 3. Approved Evidence & Terminology Hierarchy

| Level | Classification Category | Permitted Terminology | Forbidden Terminology |
|---|---|---|---|
| **A** | **DIRECTLY ESTABLISHED** | *"directly observed in the preserved timestep telemetry"*, *"directly established for the observed execution"*, *"the telemetry shows..."*, *"the observed sequence is..."* | *"proved universally"*, *"caused"* (unless specific causal attribution is isolated by design) |
| **B** | **STRONGLY SUPPORTED** | *"strongly supported by the observed telemetry"*, *"consistent with the observed pathway"*, *"the evidence strongly supports..."*, *"associated with..."* | *"proves"*, *"uniquely causes"*, *"demonstrates causal necessity"* |
| **C** | **ASSOCIATION ONLY** | *"associated with"*, *"correlated with"*, *"co-occurs with"*, *"the observed data are consistent with..."* | *"demonstrates causation"*, *"explains entirely"* |
| **D** | **HYPOTHESIS** | *"hypothesized"*, *"plausible explanation"*, *"not established"* | *"established fact"*, *"proven driver"* |
| **E** | **NOT IDENTIFIABLE** | *"not identifiable from the preserved evidence"*, *"not established by this experiment"* | Any affirmative claim |

---

## 4. Mechanism Wording Corrections & Classifications (M1 – M7)

### M1 — Diesel Commitment
- **Raw Telemetry Evidence**:
  - Treatment Startups = **178**
  - Control Startups = **346**
  - Treatment Diesel Timesteps = **400**
  - Control Diesel Timesteps = **346**
  - Treatment Mean Diesel Power when ON = **33.79 kW**
  - Control Mean Diesel Power when ON = **10.00 kW**
- **Original Problematic Wording**: *"Treatment induces additional diesel commitment and startup events."*
- **Corrected Approved Wording**: *"Treatment exhibited fewer diesel startup events (178 vs 346) but longer diesel-on duration (400 vs 346 timesteps) and higher average diesel power (33.79 kW vs 10.0 kW) across diesel-active timesteps."*
- **Evidence Classification**: `M1 = B — STRONGLY SUPPORTED`

---

### M2 — Battery Dispatch
- **Raw Telemetry Evidence**: Battery charge/discharge decisions diverge at early MPC timesteps ($k=1 \dots 4$), causing SOC divergence prior to daytime solar arrival and subsequent diesel dispatch.
- **Original Problematic Wording**: *"The battery definitively caused the diesel increase."*
- **Corrected Approved Wording**: *"The preserved timestep telemetry directly shows early divergence in battery dispatch and SOC trajectories that precedes later diesel divergence. The observed forecast/optimization difference is associated with the subsequent battery/SOC pathway."*
- **Evidence Classification**: `M2 = A — DIRECTLY ESTABLISHED FOR THE OBSERVED TEMPORAL PATHWAY`

---

### M3 — Renewable Absorption & Curtailment
- **Raw Telemetry Evidence**: Higher renewable curtailment occurs during active diesel generator commitment due to the minimum operating constraint ($P_{\text{min}} = 15 \text{ kW}$).
- **Original Problematic Wording**: *"Stage8.1 directly caused all curtailment."*
- **Corrected Approved Wording**: *"The telemetry shows renewable curtailment occurring during periods in which diesel commitment/minimum-output constraints limited renewable absorption. This provides evidence for a downstream pathway connecting forecast-dependent dispatch to renewable curtailment."*
- **Evidence Classification**: `M3 = A — DIRECTLY ESTABLISHED AT THE OBSERVED DISPATCH/EVENT LEVEL`

---

### M4 — SOC Positioning
- **Raw Telemetry Evidence**: Early SOC divergence established at $k=1$ persists into afternoon peak demand hours, coinciding with differences in diesel commitment.
- **Original Problematic Wording**: *"SOC mispositioning is the unique cause of the aggregate fuel deficit."*
- **Corrected Approved Wording**: *"The observed telemetry shows early SOC divergence that persists into later operating periods and coincides with subsequent differences in diesel dispatch."*
- **Evidence Classification**: `M4 = A — DIRECTLY ESTABLISHED FOR THE OBSERVED TEMPORAL PATHWAY`

---

### M5 — Forecast-Horizon Shape
- **Raw Telemetry Evidence**: Multi-horizon forecast vectors ($h=5 \dots 12$) at $k=0$ differ between Control and Treatment before $H1$ ($h=1$) values diverge at $k=5$.
- **Original Problematic Wording**: *"h=5..12 was proven to cause the diesel increase."*
- **Corrected Approved Wording**: *"The treatment and control forecast vectors differed in their multi-horizon shape before the H1 forecast divergence occurred, and the optimizer/dispatch trajectories subsequently diverged. This strongly supports involvement of forecast-horizon shape, but the individual causal contribution of specific horizons was not isolated by this experiment."*
- **Evidence Classification**: `M5 = B — STRONGLY SUPPORTED, NOT INDIVIDUALLY ISOLATED`

---

### M6 — Multi-Pathway Interaction
- **Raw Telemetry Evidence**: Linked trajectory traces confirm sequential involvement of multi-horizon forecast shape, battery SOC positioning, generator commitment, and renewable curtailment.
- **Original Problematic Wording**: *"V2 proved the complete causal chain."*
- **Corrected Approved Wording**: *"The V2 telemetry supports a sequential multi-pathway association involving multi-horizon forecast differences, battery/SOC positioning, diesel dispatch, and renewable curtailment."*
- **Evidence Classification**: `M6 = B — STRONGLY SUPPORTED`

---

### M7 — Other Mechanisms
- **Approved Status**: `M7 = E — NOT IDENTIFIABLE FROM THE AVAILABLE EVIDENCE`. No secondary un-modeled mechanisms observed.

---

## 5. Technical Reconciliations & Clarifications

### Diesel Fuel vs Diesel Energy Reconciliation
- **Preserved Raw Values**:
  - Control: Fuel $= 4671.00 \text{ L}$, Energy $= 3460.00 \text{ kWh}$ (Implied ratio: $0.7407 \text{ kWh/L}$).
  - Treatment: Fuel $= 6447.44 \text{ L}$, Energy $= 13517.38 \text{ kWh}$ (Implied ratio: $2.0965 \text{ kWh/L}$).
- **Approved Explanation**:
  > *"The differing implied kWh/L ratios arise from the documented nonlinear/penalty-based fuel-consumption model $F(P) = 5.0 + 0.00025 \cdot P + 6.0 \cdot \mathbb{I}_{\text{startup}}$ and the different diesel operating regimes observed in control and treatment; they should not be interpreted as a conventional constant fuel efficiency."*

---

### Heterogeneity Arithmetic Reconciliation
- **Preserved Raw Values**:
  - Positive Origins ($N_{\text{pos}} = 95$): Subgroup Mean $= \mathbf{+36.0633 \text{ L / origin}}$; Population Contribution $= 95 \times 36.0633 / 173 = \mathbf{+19.8035 \text{ L}}$.
  - Negative Origins ($N_{\text{neg}} = 77$): Subgroup Mean $= \mathbf{-21.4230 \text{ L / origin}}$; Population Contribution $= 77 \times -21.4230 / 173 = \mathbf{-9.5351 \text{ L}}$.
  - Zero Origins ($N_{\text{zero}} = 1$): Mean $= 0.00 \text{ L}$.
  - Overall Population Mean: $+19.8035 - 9.5351 = \mathbf{+10.2684 \text{ L / origin}}$.
- **Approved Clarification**:
  Numbers $+21.64 \text{ L}$ and $-13.06 \text{ L}$ from preliminary text summaries represent **population-weighted contributions across all 173 origins**, NOT subgroup means. Subgroup means are $+36.0633 \text{ L}$ and $-21.4230 \text{ L}$.

---

### Temporal Divergence Index Clarification
- **MPC Timestep Index ($k \in \{0 \dots 23\}$)**: Refers to the receding-horizon execution step (hour offset from origin issuance $t_0$).
- **Forecast Horizon Index ($h \in \{1 \dots 24\}$)**: Refers to the lookahead hours within a single forecast vector.
- **Approved Clarification**:
  > *"At the initial MPC cycle ($k=0$), treatment and control already differed in their multi-horizon forecast vectors ($h=5 \dots 12$) even before the H1 values ($h=1$) diverged at $k=5$. The subsequent battery/SOC and diesel trajectories diverged at later MPC timesteps ($k=1 \dots 4$)."*

---

## 6. Causal Language Policy Compliance

The following verb substitutions have been enforced across all documentation artifacts:

| Unsupported Causal Verb | Approved Context-Appropriate Substitution |
|---|---|
| *causes / caused* | *preceded / was followed by / was associated with* |
| *induces / induced* | *coincided with / was followed by* |
| *forces / forced* | *was associated with / constrained by* (except for explicit physical model constraints) |
| *drives / drove* | *strongly supports involvement of* |
| *proves / proven* | *directly establishes for the observed execution / provides evidence for* |
| *demonstrated causality* | *demonstrates temporal alignment and physical model consistency* |

---

## 7. Documentation-Only Audit Confirmation Checklist

- [x] **Source Code Unchanged**: Zero edits to `s81_solar.py`, `baseline.py`, `milp.py`, `simulator.py`, `runner.py`, or `v2_logger.py`.
- [x] **Raw Evidence Unchanged**: `POLARIS_STAGE8_1_EMS_V2_EXECUTION_RAW.csv` hash verified (`652a047d...`).
- [x] **Manifest Unchanged**: `POLARIS_STAGE8_1_EMS_V2_EXECUTION.json` hash verified (`97a1dec8...`).
- [x] **No Execution Rerun**: Zero origins, zero pilots, zero smoke tests executed.
- [x] **EMS Modification Locked**: Zero parameter tuning or engineering changes permitted.

---

## 8. Authoritative Final Governance State

```yaml
V1 = ACCEPTED + FROZEN
V2 EXECUTION = VALID + COMPLETED
V2 RAW EVIDENCE = FROZEN
V2 PRIMARY RESULT = FROZEN (+10.2684 L / origin, p = 0.0014)
V2 MECHANISM EVIDENCE = ACCEPTED WITH QUALIFICATIONS
V2 MECHANISM WORDING = CORRECTED AND LOCKED
EMS MODIFICATION = NOT AUTHORIZED
ENGINEERING INTERVENTION = NOT AUTHORIZED
V3 = NOT INITIATED
```

---
**Authoritative Correction Artifacts**:
- [`POLARIS_STAGE8_1_EMS_V2_MECHANISM_WORDING_CORRECTION.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_STAGE8_1_EMS_V2_MECHANISM_WORDING_CORRECTION.md)
- [`POLARIS_STAGE8_1_EMS_V2_MECHANISM_WORDING_CORRECTION.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_STAGE8_1_EMS_V2_MECHANISM_WORDING_CORRECTION.json)
