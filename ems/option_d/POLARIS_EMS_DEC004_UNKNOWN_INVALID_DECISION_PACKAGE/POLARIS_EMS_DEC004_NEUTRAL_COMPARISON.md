# POLARIS EMS — DEC-004 NEUTRAL COMPARISON OF CANDIDATE OPTIONS (A, B, C, D)

## 1. Executive Summary

This document presents a strictly neutral, evidence-based comparative analysis of Candidate Options **A**, **B**, **C**, and **D** for DEC-004. In compliance with governance instructions:
- **NO rankings, scores, or weighted totals are assigned.**
- **NO option is declared "best", "safest", "preferred", "superior", or "recommended".**
- **Option D is documented strictly as a candidate policy concept.**

---

## 2. 15-Question Neutral Comparison Matrix

| # | Comparison Dimension | Option A: Hold Last Plan | Option B: Zero Dispatch | Option C: Operator Intervention | Option D: Protected Critical Fallback |
|---|----------------------|--------------------------|-------------------------|---------------------------------|--------------------------------------|
| **1** | **Immediate Action after UNKNOWN_INVALID** | Re-applies setpoints/schedule from previous $t_{k-1}$ plan | Enforces zero controllable dispatch ($P_{\text{chg}}=0, P_{\text{dis}}=0, P_{\text{diesel}}=0$) | Halts pipeline immediately (`CRITICAL_TERMINATION`) | Suppresses noncritical loads; dispatches renewables + diesel for critical load ONLY |
| **2** | **Does Automated MPC Continue?** | Yes (reusing prior plan steps) | Yes (advancing 0-power state) | No (MPC loop suspended) | Degraded execution (bypasses 24h optimizer) |
| **3** | **Previous Dispatch Retained?** | Yes (retained from $t_{k-1}$) | No (overridden to zero) | No (overridden to halt) | No (overridden to critical-only dispatch) |
| **4** | **Renewable Resources Usable?** | Yes (per previous plan) | Yes (direct power to load if uncurtailed) | Dependent on hardware relays | Yes (renewable-first for critical load) |
| **5** | **Diesel Generation Usable?** | Yes (per previous plan) | No ($P_{\text{diesel}} = 0$) | Locked out | Yes (to cover remaining critical load) |
| **6** | **Battery Dispatch Involved?** | Yes (per previous plan) | No ($P_{\text{chg}}=0, P_{\text{dis}}=0$) | Locked out | Unresolved (requires governance decision) |
| **7** | **Noncritical Load Served?** | Yes (all loads served per plan) | No (all noncritical loads shed) | No (automated service halted) | No (noncritical loads explicitly shed) |
| **8** | **Critical Load Protected?** | Indirectly (if plan covers it) | No (critical load shed with noncritical) | Dependent on hardware relays | Yes (explicitly prioritized & protected) |
| **9** | **Unmet Demand Behavior** | Zero (unless load exceeds plan) | Equals total station demand minus uncurtailed renewables | Dependent on local protection relays | Equals unserved noncritical demand ($23\text{ kW}$ in synthetic example) |
| **10** | **Resource-Consumption Risk** | High (risk of fuel/battery drain if forecast inaccurate) | Zero (zero fuel/battery consumption) | Zero (automated dispatch locked) | Medium (diesel consumed for critical load only) |
| **11** | **Stale-Information Risk** | High (executes plan based on invalid $t_0$ state) | Low (ignores stale inputs, forces zero power) | Low (halts automated processing) | Medium (uses $t_0$ critical load definition) |
| **12** | **Operator Dependency** | Low initially; high upon plan expiry | Low initially; high for load restoration | Immediate operator intervention required | High (awaits operator to restore valid state) |
| **13** | **Recovery Mechanism** | Resumes normal MPC on valid ECD | Resumes normal MPC on valid ECD | Requires manual SCADA fault reset | Resumes normal MPC on valid operator/ECD input |
| **14** | **New Components Required** | Plan cache & watchdog timer | Extension of D4-C0 failure contract | SCADA alarm & lockout handler | Critical load shedder & renewable-first router |
| **15** | **Unresolved Governance** | Max hold duration & fallback threshold | Acceptability of zero-dispatch load shedding | Operator alert escalation policy | Exact critical load circuits & battery behavior |

---

## 3. Synthetic Illustrative Numerical Example

> [!CAUTION]
> **SYNTHETIC ILLUSTRATIVE EXAMPLE ONLY**
> The numbers below are **NOT STATION DATA**, **NOT DEPLOYMENT PARAMETERS**, and **NOT GOVERNANCE VALUES**. They are used purely to explain the comparative mechanics of Options A, B, C, and D under an identical synthetic scenario.

### Baseline Synthetic Scenario Setup:
- **Total Station Demand**: $30\text{ kW}$
- **Conceptual Critical Load**: $7\text{ kW}$ ($3\text{ kW}$ heating + $2\text{ kW}$ water treatment + $2\text{ kW}$ comms)
- **Non-Critical Demand**: $23\text{ kW}$
- **Available Renewable Generation**: $3\text{ kW}$ ($2\text{ kW}$ solar + $1\text{ kW}$ wind)
- **Diesel Generator Capacity**: $100\text{ kW}$ rating ($10\text{ kW}$ min power)
- **Battery State**: $80\%\text{ SOC}$ ($160\text{ kWh}$ stored)
- **Previous Valid Plan ($t_{k-1}$)**: $P_{\text{solar\_used}} = 3\text{ kW}, P_{\text{dis}} = 12\text{ kW}, P_{\text{diesel}} = 15\text{ kW}$ to meet $30\text{ kW}$ total demand.

---

### Comparative Mechanics under `UNKNOWN_INVALID` at Timestep $t_k$:

#### **Option A (Hold Last Valid Dispatch)**
- **Executed Dispatch**: $P_{\text{solar}} = 3\text{ kW}, P_{\text{dis}} = 12\text{ kW}, P_{\text{diesel}} = 15\text{ kW}$
- **Served Demand**: $30\text{ kW}$ (100% total demand served: $7\text{ kW}$ critical + $23\text{ kW}$ noncritical)
- **Unmet Demand**: $0\text{ kW}$
- **Resource Consumption**: Battery discharged at $12\text{ kW}$; diesel burned at $15\text{ kW}$ rate ($8.75\text{ L/h}$)
- **Tradeoff**: Maintains full station power, but drains fuel and battery based on potentially invalid forecast.

#### **Option B (Zero-Dispatch Fail-Closed)**
- **Executed Dispatch**: $P_{\text{chg}} = 0, P_{\text{dis}} = 0, P_{\text{diesel}} = 0$
- **Served Demand**: $3\text{ kW}$ (direct uncurtailed renewables)
- **Unmet Demand**: $27\text{ kW}$ ($4\text{ kW}$ critical load unmet + $23\text{ kW}$ noncritical load unmet)
- **Resource Consumption**: $0\text{ kW}$ battery discharge; $0\text{ L/h}$ fuel burn
- **Tradeoff**: Completely preserves fuel and battery energy, but causes immediate critical load interruption.

#### **Option C (Operator Intervention / Pipeline Halt)**
- **Executed Dispatch**: Automated MPC halted (`CRITICAL_TERMINATION`). $0\text{ kW}$ automated dispatch.
- **Served Demand**: $0\text{ kW}$ (automated system); relies on site local hardware protective relays.
- **Unmet Demand**: Dependent on local hardware fallback.
- **Resource Consumption**: Zero automated resource consumption.
- **Tradeoff**: Prevents automated control actions on invalid data, but stops automated microgrid management until human operator intervenes.

#### **Option D (Protected Critical-Load Fallback)**
- **Executed Dispatch**:
  - Noncritical load ($23\text{ kW}$) is shed / not dispatched.
  - Conceptual critical load ($7\text{ kW}$) prioritized.
  - Renewable-first: $3\text{ kW}$ renewables ($2\text{ kW}$ solar + $1\text{ kW}$ wind) applied to critical load.
  - Remaining critical load demand = $7 - 3 = 4\text{ kW}$.
  - Diesel dispatch & model constraint resolution:
    - *Illustrative Power Balance*: Dispatches $4\text{ kW}$ diesel power to match remaining critical demand ($7 - 3 = 4\text{ kW}$).
    - *Model Minimum Constraint Boundary*: In prototype config (`system/config/diesel.yaml`), `min_power_w = 10000.0` ($10\text{ kW}$). If constrained by $10\text{ kW}$ minimum output, diesel produces $10\text{ kW}$ (resulting in $13\text{ kW}$ total generation, producing $6\text{ kW}$ excess power over $7\text{ kW}$ critical load). Disposition of excess generation (charging battery vs. curtailment) is `UNRESOLVED_GOVERNANCE_DECISION`.
    - *Deployment Parameter*: Physical generator turndown ratio and minimum loading rules are `ENGINEERING_DEFINITION_REQUIRED`.
  - Battery dispatch: `UNRESOLVED` (requires governance decision; not assumed in candidate concept).
- **Served Demand**: $7\text{ kW}$ (100% conceptual critical load served; $0\text{ kW}$ noncritical load served).
- **Unmet Demand**: $23\text{ kW}$ (noncritical demand shed).
- **Resource Consumption**: 
  - *At Illustrative $4\text{ kW}$ Dispatch*: Diesel fuel burn rate = $5.0 + (0.25 \times 4) = 6.0\text{ L/h}$.
  - *At $10\text{ kW}$ Model Minimum*: Diesel fuel burn rate = $5.0 + (0.25 \times 10) = 7.5\text{ L/h}$.
  - Noncritical fuel/battery energy conserved relative to Option A.
- **Tradeoff**: Explicitly protects critical life-safety load while shedding noncritical demand, but requires diesel generation and critical load shedding infrastructure.

---

## 4. Fact-Based Summary Statement

Each option reflects a distinct governance prioritization:
- **Option A** prioritizes full station demand continuity.
- **Option B** prioritizes absolute energy resource preservation.
- **Option C** prioritizes security and human authority by locking automated control.
- **Option D** prioritizes critical life-safety service preservation while shedding noncritical demand.

Status: `NEUTRAL_COMPARISON_COMPLETE`
