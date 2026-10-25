# STAGE 8.7A — GOVERNANCE REVIEW & PROXY PROVENANCE AUDIT

**Author:** POLARIS Lead Governance & AI Audit Team  
**Date:** September 12, 2026  
**Status:** Authoritative Governance Audit & Proxy Provenance Review  
**Target Station:** SITES Nuolja ($68.362074^\circ\text{N}, 18.738752^\circ\text{E}$)  
**Governance Decision:** **CONDITIONAL_PENDING_PROXY_APPROVAL**

---

## 1. Governance Review Summary

This governance review evaluates the Stage 8.7A feasibility audit prior to any Stage 8.7B model execution. Under POLARIS strict benchmark governance:

1. **Stage 8.7B Execution Status:** **NOT AUTHORIZED.** No model training, no cross-validation, no hyperparameter tuning, no ODD evaluation, and no predictions have been executed.
2. **Master Handoff Status:** `POLARIS_MASTER_HANDOFF.md` remains strictly **UNTOUCHED**.
3. **ODD Firewall:** Strictly **ENFORCED** (0 target reads, 0 predictions, 0 metrics, 0 tuning).

---

## 2. Task 1 — Proxy Provenance & Methodological Classification

### Provenance Audit of DirectProxy Formula
The implementation script (`run_stage8_7a_feasibility.py`) constructed the direct-beam proxy using:
$$\text{DirectProxy}_h = \text{DNI}_h \times \max(0, \sin(\text{solar\_elevation}_h)) \times (1 - \text{terrain\_solar\_obstruction\_flag}_h)$$

### Audit Findings
- **Predeclaration Check:** Section 10 of `POLARIS STAGE 8.7 — SCIENTIFIC ROUTE SELECTION STUDY` (`/home/punith-bs/Downloads/8.7POLARIS_STAGE8_7_ROUTE_SELECTION_STUDY.md`) specified the proxy in functional form as $\text{DirectProxy}_h = \text{DNI}_h \times f(\text{terrain\_solar\_obstruction\_flag}_h, \text{solar\_elevation}_h)$, but did **NOT** provide a closed-form algebraic specification of $f(\cdot)$.
- **Methodological Classification:** Although this formula reflects standard physical geometry projecting direct normal irradiance onto a horizontal surface zeroed during local terrain shading, physical plausibility is **NOT equivalent to explicit predeclaration**.
- **Formal Determination:** The specific closed-form equation implemented is classified as an **IMPLEMENTATION ASSUMPTION**, rather than an explicitly predeclared formula from prior study artifacts.
- **Governance Requirement:** Stage 8.7B authorization requires explicit scientific governance approval of this specific proxy formulation before any model training or cross-validation may begin.

---

## 3. Task 2 — Negative Residual Language & Empirical Breakdown

### Revised Scientific Classification
Unsupported causal claims (e.g., attributing negative residuals to "cloud placement timing noise" or "NWP forecast error") are removed. The empirical facts established by the audit are:

- **Total Negative Residual Count (All Tuples):** $95 / 8,328$ ($1.14\%$)
- **Total Negative Residual Count (Daytime Tuples):** $95 / 5,768$ ($1.65\%$)
- **Minimum Residual Value:** $-333.4285\text{ W/m}^2$

### Empirical Regime Breakdown
> **The negative-residual cases are concentrated mostly at solar elevation $>20^\circ$, but their causal origin is not established by this feasibility audit.**

- Solar elevation $\le 5^\circ$: $3$ rows
- Solar elevation $5^\circ < \gamma_s \le 20^\circ$: $1$ row
- Solar elevation $> 20^\circ$: $91$ rows

---

## 4. Task 3 — Leakage & Target Causality Audit

A forensic audit of data flow and variable roles confirms strict causal isolation:

1. **Feature Input Causality:** $\text{DirectProxy}_h$ uses exclusively causally available forecast inputs ($\text{DNI}_h$ from D-1 18Z MEPS run) and static/astronomical geometry ($\text{solar\_elevation}_h$, $\text{terrain\_solar\_obstruction\_flag}_h$). It is causally valid as a forecast-time model input or anchor.
2. **Target Definition Isolation:** $\text{DiffuseResidual}_h = \text{actual\_SW\_IN}_h - \text{DirectProxy}_h$ is an **OUTCOME-DERIVED TRAINING TARGET**.
3. **Operational Prohibition:** $\text{DiffuseResidual}_h$ contains ground-truth observation $\text{actual\_SW\_IN}_h$ and must **NEVER** be ingested as a model feature, context input, routing signal, or normalization factor at forecast time.
4. **Validation / Test Reading Rule:** Validation and test actual $\text{SW\_IN}$ values must **NOT** be read or accessed before predictions are generated.
5. **Stage 8.7B Target Protocol:** In Stage 8.7B, actual $\text{SW\_IN}$ may only be accessed after predictions are produced, strictly for post-hoc loss computation and evaluation. No future actual $\text{SW\_IN}$ may enter feature matrices, routing, normalization, or hyperparameter selection.

---

## 5. Task 4 — Governance Decision

```
+-----------------------------------------------------------------------------------+
|                       STAGE 8.7A GOVERNANCE DECISION                              |
+-----------------------------------------------------------------------------------+
| Final Decision:                   CONDITIONAL_PENDING_PROXY_APPROVAL              |
| Stage 8.7B Authorization:         HOLD (NOT AUTHORIZED)                           |
| Data Feasibility:                 PASS (8,328 / 8,328 tuples causally available) |
| Proxy Formula Status:             IMPLEMENTATION ASSUMPTION (Requires Approval)   |
| ODD Firewall Status:              100% ENFORCED (0 reads, 0 preds, 0 metrics)     |
| Master Handoff Status:            UNTOUCHED                                       |
+-----------------------------------------------------------------------------------+
```

### Action Required for Stage 8.7B Authorization
Stage 8.7B execution remains **ON HOLD**. Authorization requires explicit scientific approval of the closed-form equation $\text{DirectProxy}_h = \text{DNI}_h \times \max(0, \sin(\gamma_s)) \times (1 - \text{flag}_h)$ as the official proxy definition for Head 1.
