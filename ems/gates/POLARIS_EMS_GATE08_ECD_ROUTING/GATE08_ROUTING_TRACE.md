# POLARIS EMS GATE-08 — ECD ROUTING TRACE

## 1. Executive Summary
This document records the complete routing trace evaluated by the Emergency Condition Detector (ECD) and the EMS Control Router across all operational modes and governance boundaries.

## 2. Comprehensive ECD Routing Decision Matrix

| Scenario / Trigger | Input Telemetry / Assessment | ECD Classification | Router Selected Path | Downstream Solver / Handler | State Advancement | Governance Boundary Preserved |
| :--- | :--- | :---: | :---: | :--- | :---: | :---: |
| **Case 1: Standard Normal** | Valid telemetry, $m_{\text{bat}} \ge 0, m_{\text{diesel}} \ge 0$ | `NORMAL` | `NORMAL` | Option B (GAP19 HiGHS Native MPC) | TRUE (1 step) | Nominal Operation |
| **Case 2: Emergency Survivability** | Low fuel ($4.0\text{ L}$), $m_{\text{diesel}} < 0$ | `EMERGENCY` | `EMERGENCY` | Option D Protected Fallback Solver | TRUE (1 step) | Gate-03 Emergency Rule |
| **Case 3: Telemetry / Horizon Fault** | Invalid horizon ($t_{\text{req}} = 0.0\text{ h}$) | `UNKNOWN_INVALID` | `UNKNOWN_INVALID` | Automatic Optimization Stopped | **FALSE** (0 steps) | Gate-01 GOVERNED_HYBRID |
| **Case 4: Emergency Return** | Resupplied fuel ($100.0\text{ L}$), $m \ge 0$ | `NORMAL` | `NORMAL` | Option B (Auto-return with event) | TRUE (1 step) | Gate-03 Automatic Return |
| **Case 5: MILP Infeasibility** | Infeasible HighsModelStatus | `NORMAL` | `NORMAL` | Governed Degraded / Infeasible | **FALSE** (0 steps) | Gate-02 Hard Critical Load |

> [!NOTE]
> All routing traces were generated using the synthetic H1.0 fixture and verified against sealed governance contracts.

## 3. Key Observations
- Every classified mode routes deterministically to its designated downstream handler.
- `UNKNOWN_INVALID` immediately halts execution and prevents state advancement.
- `MILP_INFEASIBLE` solver status triggers governed halt without state advancement or invalid zero-dispatch execution.
