# POLARIS — SOLAR FORECAST BRANCH 01
## CONTROLLED MULTI-TRAJECTORY EMS CAMPAIGN PLAN

**Governance Gate**: Pre-Execution Campaign Plan  
**Date**: 2026-09-21  
**Mode**: **READ-ONLY CAMPAIGN RECONNAISSANCE & DESIGN**  

---

### 1. CAMPAIGN OBJECTIVE & IDENTITY
- **Target Model**: `POLARIS_SOLAR_FORECAST_BRANCH_01_HGB_V1` (SHA `65c04d6c3aa426b9ead9e103d4c1c8d033095b9070676dcbffe71f8e16dd4781`)
- **Control Model**: `Stage81ForecastEngine` (`s81_solar.py` SHA `d76249bb0fc78680f0ea6723fbec62a234511d181e0a091b2f80fa06838aca7c`)
- **Evaluation Dataset**: `POLARIS_HYBRID_FIXTURE_H1_0` (8,784 hourly rows, Jan 1 – Dec 31, 2024)
- **Eligible Trajectories**: 173 even-day 24-hour trajectories ($173 \times 24 = 4,152$ MPC cycles)

---

### 2. COVERAGE & ANNUALIZATION SEMANTICS
- **Candidate Trajectories**: 173
- **Eligible Trajectories**: 173
- **Excluded Trajectories**: 0
- **Total MPC Cycles**: 4,152
- **Total Evaluated Hours**: 4,152
- **Coverage Status**: `PARTIAL` / `REPRESENTATIVE_TRAJECTORY_SET`
- **Annualization Rule**: Results are reported strictly across the evaluated 173 representative trajectories (`ANNUAL_RESULT_STATUS = REPRESENTATIVE_TRAJECTORY_SET`). Unsubstantiated daily multiplication ($	imes 365$) is strictly prohibited.

---

### 3. MANDATORY SAFETY BOUNDARIES
- Zero retraining or hyperparameter tuning of Branch01.
- Zero modification to Stage 8.1, MILP optimizer (`milp.py`), `DispatchPlan` (`dispatch_plan.py`), or Digital Twin simulator (`simulator.py`).
- Zero fallback (clear-sky, persistence, or zero fill) allowed in treatment.
- Strict hidden truth firewall enforced between forecast engines and simulator ground truth.

---

### 4. PRE-EXECUTION GOVERNANCE STATUS
```
CAMPAIGN_PLAN =
APPROVED_FOR_REVIEW

PRE_EXECUTION_GATE =
PASS

MODEL_IDENTITY_GATE =
PASS

CONTROL_IDENTITY_GATE =
PASS

ANNUAL_RESULT_STATUS =
REPRESENTATIVE_TRAJECTORY_SET

EXECUTION_AUTHORIZATION =
PENDING_EXPLICIT_USER_AUTHORIZATION
```
