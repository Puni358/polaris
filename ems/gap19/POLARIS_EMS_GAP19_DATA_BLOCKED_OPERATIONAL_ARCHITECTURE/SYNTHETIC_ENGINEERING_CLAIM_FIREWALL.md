# POLARIS EMS GAP19 — SYNTHETIC ENGINEERING CLAIM FIREWALL

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_DATA_BLOCKED_OPERATIONAL_ARCHITECTURE`  

---

## 1. Explicit Boundary Between Allowed vs Prohibited Claims

To preserve scientific rigor, all technical claims regarding POLARIS EMS are partitioned into two strict sets:

### A. Allowed Synthetic Engineering Claims
The synthetic environment is authorized to prove:
1. **Software Path Execution**: Python classes, schemas, and orchestrator loops execute without crashing.
2. **Solver Formulation Convergence**: Option B native HiGHS MILP formulation converges deterministically.
3. **MPC Receding Horizon**: 24-step horizon rolls correctly and commits ONLY $k=0$ each cycle.
4. **Digital Twin State Continuity**: `StationState` propagates seamlessly across cycle boundaries.
5. **ECD Logic Reproduction**: Canonical survivability equations match mathematical reference fixtures.
6. **Energy Balance & Truth Firewall**: Physical power balance equations and truth firewalls function as designed.

### B. Strictly Prohibited Claims (Firewall Enforced)
The following statements **MUST NOT** be asserted or implied:
* *"Nuolja station has a 200 kWh battery."*
* *"Nuolja station critical load is 30 kW."*
* *"Nuolja diesel generator consumes 5 L/h + 0.25 L/kWh."*
* *"Nuolja has 100 L of emergency diesel fuel."*
* *"Nuolja station can survive 6 hours or 72 hours."*
* *"The 200 kWh s_J2 upper bound is the station's required reserve."*
* *"Option D fallback is validated for production deployment at Nuolja."*

---

## 2. Firewall Enforcement Statement

`SYNTHETIC_VALUE_PROMOTION = NONE`  
`PROXY_PROMOTION = NONE`

Zero prototype parameters or regional proxies may be promoted to production evidence.
