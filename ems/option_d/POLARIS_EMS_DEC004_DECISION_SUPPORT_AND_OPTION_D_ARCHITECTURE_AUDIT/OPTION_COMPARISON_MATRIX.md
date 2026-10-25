# POLARIS EMS — DEC-004 27-DIMENSION COMPARATIVE MATRIX

## 1. Executive Summary

This document presents a 27-dimension comparative matrix evaluating Options **A**, **B**, **C**, and **D** under `UNKNOWN_INVALID`. All cells contain strictly factual, evidence-backed statements without evaluative terms or scores.

---

## 2. Exhaustive 27-Dimension Comparison Table

| # | Comparison Dimension | Option A: Hold Last Plan | Option B: Zero Dispatch | Option C: Operator Intervention | Option D: Protected Critical Fallback |
|---|----------------------|--------------------------|-------------------------|---------------------------------|--------------------------------------|
| **1** | **UNKNOWN_INVALID Initial Action** | Re-applies setpoints/schedule from previous $t_{k-1}$ plan | Enforces zero controllable dispatch ($P_{\text{chg}}=0, P_{\text{dis}}=0, P_{\text{diesel}}=0$) | Immediately halts MPC pipeline (`CRITICAL_TERMINATION`) | Suppresses noncritical loads; dispatches renewables + diesel + battery for critical load ONLY |
| **2** | **Automated Dispatch Continuity** | Continuous (executing prior plan steps) | Continuous (advancing 0-power state) | Suspended (MPC loop halted) | Continuous degraded dispatch (bypasses 24h optimizer) |
| **3** | **Critical-Load Treatment** | Served if $t_{k-1}$ plan covered it | Shed alongside noncritical load | Dependent on site hardware relays | Explicitly prioritized & protected |
| **4** | **Noncritical-Load Treatment** | Served if $t_{k-1}$ plan covered it | Shed alongside critical load | Dependent on site hardware relays | Explicitly shed / suppressed |
| **5** | **Battery Discharge Behavior** | Executed per $t_{k-1}$ plan | Prohibited ($P_{\text{dis}} = 0$) | Prohibited (automated dispatch locked) | Permitted solely for protected critical load when generation is deficient |
| **6** | **Battery Charging Behavior** | Executed per $t_{k-1}$ plan | Prohibited ($P_{\text{chg}} = 0$) | Prohibited (automated dispatch locked) | Permitted from unavoidable diesel minimum excess or surplus renewables up to charge limit |
| **7** | **Diesel Behavior** | Executed per $t_{k-1}$ plan | Prohibited ($P_{\text{diesel}} = 0$) | Prohibited (automated dispatch locked) | Dispatched when required to maintain critical load; diesel-only-for-charging prohibited |
| **8** | **Renewable Behavior** | Applied per $t_{k-1}$ plan | Direct power to load if uncurtailed | Dependent on site hardware relays | Directed first toward protected critical demand |
| **9** | **Behavior when Renewable Unavailable** | Retains $t_{k-1}$ diesel/battery setpoints | $P_{\text{chg}}=0, P_{\text{dis}}=0, P_{\text{diesel}}=0$ | Automated MPC halted | Dispatches diesel generator; uses battery as fallback under D3 |
| **10** | **Behavior when Diesel Unavailable** | Retains $t_{k-1}$ battery setpoints | $P_{\text{chg}}=0, P_{\text{dis}}=0, P_{\text{diesel}}=0$ | Automated MPC halted | Uses renewables + battery fallback to maintain critical load |
| **11** | **Behavior when Battery Unavailable** | Retains $t_{k-1}$ diesel setpoints | $P_{\text{chg}}=0, P_{\text{dis}}=0, P_{\text{diesel}}=0$ | Automated MPC halted | Uses renewables + diesel to maintain critical load; excess diesel power is curtailed |
| **12** | **Insufficient Critical-Power Behavior** | Executes fixed $t_{k-1}$ setpoint | Critical load remains unserved | Dependent on site hardware relays | Proportionally allocates available power across critical systems; escalates to operator |
| **13** | **Operator Involvement** | Awaits input upon plan expiry | Awaits input for load restoration | Immediate intervention required to clear fault | Awaits input; escalates at D4 shortfall or D5 time/resource boundary |
| **14** | **Operator Timing Dependency** | Low initially; high upon plan expiry | Low initially; high for load restoration | Immediate dependency on human latency | Low initially; dependent upon D5 watchdog boundary |
| **15** | **Recovery after Valid ECD Return** | Resumes normal MPC loop on valid ECD | Resumes normal MPC loop on valid ECD | Requires manual SCADA fault reset / pipeline restart | Resumes normal MPC loop on valid ECD or operator override |
| **16** | **Additional Runtime State Required** | Requires `last_valid_dispatch_plan` cache & watchdog | Reuses existing D4-C0 zero-power state handler | Reuses existing `CRITICAL_TERMINATION` handler | Requires Critical Load Shedder module & policy router |
| **17** | **Additional Schema Requirements** | Additive `plan_hold_count` in `DispatchPlan` metadata | Additive `FaultEvent` class code | Additive `FaultEvent` class code | Additive `protected_critical_load_w` & `shed_noncritical_load_w` in `DispatchPlan` |
| **18** | **Additional Engineering Parameters** | Plan hold duration limit | None (reuses 0-power physics) | SCADA alert notification endpoint | Equipment inventory, $P_{\text{critical}}(t)$, minimum viable levels $P_{\text{min,viable}}$, battery limits |
| **19** | **Additional Governance Decisions** | Maximum plan hold time limit | Policy confirmation of zero-dispatch | Policy confirmation of terminal trip | DEC-004 final selection across A, B, C, D |
| **20** | **Failure-Mode Containment** | Prevents blackout during brief dropouts | Eliminates fuel/battery degradation risk | Prevents automated execution on corrupted data | Protects life-safety loads while shedding noncritical demand |
| **21** | **Risk of Stale Dispatch** | High (executes setpoints from stale forecast) | Zero (ignores stale forecast) | Zero (halts automated pipeline) | Low (uses dynamic $P_{\text{critical}}(t)$, bypasses 24h optimizer) |
| **22** | **Risk of Immediate Load Loss** | Low (maintains power output) | High (sheds all station loads) | High (suspends automated management) | Low for critical loads; high for noncritical loads |
| **23** | **Compatibility with Runner Semantics** | Requires runner plan caching | Natively compatible with D4-C0 failure path | Natively compatible with `CRITICAL_TERMINATION` | Compatible with additive runner policy router |
| **24** | **Compatibility with ECD Architecture** | Compatible (consumes `UNKNOWN_INVALID`) | Compatible (consumes `UNKNOWN_INVALID`) | Compatible (consumes `UNKNOWN_INVALID`) | Compatible (consumes `UNKNOWN_INVALID` in Mode Manager) |
| **25** | **Implementation Complexity** | Low (requires plan caching) | Low (reuses 0-power runner path) | Low (reuses fatal fault runner path) | Moderate (requires load shedder & schema additions) |
| **26** | **Test Burden** | Low (unit test for plan cache) | Low (unit test for 0-power dispatch) | Low (unit test for pipeline halt) | Moderate (requires load shedding & excess diesel tests) |
| **27** | **Production Deployment Dependencies** | Watchdog timeout definition | None | SCADA alarm integration | Critical load circuit mapping & dynamic trajectory adapter |

Status: `COMPARISON_MATRIX_SEALED`
