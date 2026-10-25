# POLARIS EMS — ECD EDGE-CASE TEST SPECIFICATION

## 1. Overview

This document specifies the expected semantic behavior for technical edge cases, boundary conditions, and invalid inputs for the Emergency Condition Detector (ECD).

---

## 2. Edge-Case Behavioral Specification Table

| Edge Case Condition | Inputs / State | Expected Semantic Result | Resulting Mode | Governance Status |
|---------------------|----------------|--------------------------|----------------|-------------------|
| **SOC Exactly at Minimum** | $\text{SOC} = \text{SOC}_{\text{min}} = 20\%$ | $T_{\text{battery}} = 0.0\text{ h}$, $M_{\text{battery}} = -T_{\text{target}}$ | `EMERGENCY` | `GOVERNANCE_CLOSED` |
| **SOC Exactly at Maximum** | $\text{SOC} = 100\%$ | $T_{\text{battery}} = 5.888\text{ h}$ (under prototype params) | Evaluated vs $T_{\text{target}}$ | `GOVERNANCE_CLOSED` |
| **Fuel Remaining = 0 L** | Fuel = $0.0\text{ L}$ | $T_{\text{diesel}} = 0.0\text{ h}$, $M_{\text{diesel}} = -T_{\text{target}}$ | `EMERGENCY` | `GOVERNANCE_CLOSED` |
| **Critical Load = 0 W** | $P_{\text{crit}} = 0\text{ W}$ | Reject as invalid input (division by zero) | `UNKNOWN_INVALID` | `ENGINEERING_DEFINITION_REQUIRED` |
| **Negative Fuel / SOC** | Fuel $< 0$ or $\text{SOC} < 0$ | Reject as invalid telemetry payload | `UNKNOWN_INVALID` | `GOVERNANCE_CLOSED` |
| **SOC > 100%** | $\text{SOC} > 1.0$ | Reject as invalid telemetry payload | `UNKNOWN_INVALID` | `GOVERNANCE_CLOSED` |
| **NaN / Inf Input** | Any float input is NaN/Inf | Reject as non-finite float error | `UNKNOWN_INVALID` | `GOVERNANCE_CLOSED` |
| **Missing $T_{\text{required}}$** | $T_{\text{required}}$ absent | Fail closed; no default substitution | `UNKNOWN_INVALID` | `GOVERNANCE_CLOSED` |
| **Expired $T_{\text{required}}$** | $\text{time} > \text{expires\_at}$ | Fail closed; expire operational command | `UNKNOWN_INVALID` | `GOVERNANCE_CLOSED` |
| **Stale Telemetry** | Telemetry age > `max_age_seconds` | Fail closed; stale telemetry guard | `UNKNOWN_INVALID` | `GOVERNANCE_CLOSED` |
| **Floating Point Tie Margin** | $|M_{\text{battery}} - M_{\text{diesel}}| < 10^{-6}\text{ h}$ | `tie_status = true`, `preserved_resource = BOTH` | `NORMAL` / `EMERGENCY` | `ENGINEERING_DEFINITION_REQUIRED` |
| **Battery Endurance == $T_{\text{required}}$** | $T_{\text{battery}} = T_{\text{required}}$ ($M_{\text{battery}} = 0.0\text{ h}$) | Zero margin is non-negative ($M \ge 0$) | `NORMAL` (if $M_{\text{diesel}} \ge 0$) | `GOVERNANCE_CLOSED` |
| **Diesel Endurance == $T_{\text{required}}$** | $T_{\text{diesel}} = T_{\text{required}}$ ($M_{\text{diesel}} = 0.0\text{ h}$) | Zero margin is non-negative ($M \ge 0$) | `NORMAL` (if $M_{\text{battery}} \ge 0$) | `GOVERNANCE_CLOSED` |

---

## 3. Engineering Parameter Notes

- **Floating-Point Equality Tolerance**: An explicit engineering epsilon ($\epsilon = 10^{-6}\text{ h} = 3.6\text{ ms}$) must be used for float equality comparison to determine `tie_status`. This is an engineering implementation detail and does not alter governance rules.

Status: `SPECIFIED`
