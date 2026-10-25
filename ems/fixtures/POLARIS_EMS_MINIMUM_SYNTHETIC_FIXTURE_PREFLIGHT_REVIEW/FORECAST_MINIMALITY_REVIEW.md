# FORECAST MINIMALITY REVIEW
## FORECAST INTERFACE AUDIT & TRUTH FIREWALL COMPLIANCE

### 1. FORENSIC AUDIT OF FORECAST PROFILES
The proposed minimum fixture specifies a synthetic forecast profile generated using:
$$\text{Forecast}(t+k|t) = \text{Actual}(t+k) \times (1 + \beta)$$
Where $\beta = +0.10$ ($10\%$ persistent over-estimation bias).

This review evaluated whether a biased forecast is minimum-sufficient or whether a perfect forecast ($\beta = 0$) should be used instead.

### 2. ARCHITECTURAL ROLE OF THE FORECAST BUNDLE
In the POLARIS EMS architecture:
1. `ForecastEngine` consumes raw telemetry and outputs a `ForecastBundle` for lookahead horizon $H=24\text{h}$.
2. The controller (`EnergyOptimizer / MILP`) consumes `ForecastBundle` predictions, NOT future actuals.
3. `DigitalTwinSimulator` steps physical equations using actual synthetic trajectories.

### 3. MINIMALITY EVALUATION
- **Option A: Perfect Forecast ($\beta = 0$)**:
  - The controller sees future truth perfectly.
  - *Deficiency*: Masking potential lookahead mismatch issues in the controller. Makes it impossible to verify that the controller relies strictly on `ForecastBundle` rather than reading future truth directly from the Digital Twin.
- **Option B: Persistence $+ 10\%$ Bias ($\beta = 0.10$)**:
  - The controller receives a distinct prediction trajectory ($\hat{P}_{\text{PV}} = 1.10 \times P_{\text{PV}}$).
  - Verifies that the controller computes dispatch using $\hat{P}$, while the Digital Twin updates state using $P$.
  - Proves strict enforcement of the **Truth Firewall**.

### 4. CLAIM FIREWALL ON FORECASTING
The synthetic forecast carries the explicit provenance tag:
`forecast_provenance: SYNTHETIC_ENGINEERING_ASSUMPTION`
`forecast_accuracy_claim: NOT_VALIDATED`

It MUST NOT be used to claim forecasting model accuracy for Nuolja.

### 5. CONCLUSION & RECOMMENDATION
`FORECAST_MINIMALITY_STATUS = MINIMUM_REQUIRED`.
Retain Persistence $+ 10\%$ Bias as the synthetic forecast generation method for the minimum fixture. It is minimum-sufficient to prove Truth Firewall isolation and lookahead MPC interface compliance.
