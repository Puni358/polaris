# POLARIS EMS — P_CRITICAL PROVENANCE MATRIX

## Executive Statement

This document tracks data provenance across synthetic prototype research files, sealed governance decisions, and unestablished station engineering inputs for **Protected Critical Load ($P_{\text{critical}}(t)$)**.

---

## Provenance Classification Register

| Parameter / Field | Provenance Origin | Source File Reference | Classification Label | Production Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **$P_{\text{critical}}$ Categories (Heating/Water/Comms)** | Human Policy Selection | [`POLARIS_EMS_DEC004_OPTION_D_FINAL_SELECTION/DEC004_GOVERNANCE_RESOLUTION.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_DEC004_OPTION_D_FINAL_SELECTION/DEC004_GOVERNANCE_RESOLUTION.md) | `SEALED_GOVERNANCE_POLICY` | Enforce D1–D6 policy rules in software. |
| **$30,000\text{ W}$ Critical Baseline** | Research Prototype Assumption | [`system/config/loads.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/loads.yaml) | `SYNTHETIC_PROTOTYPE_PARAMETER` (`status_label: "PROTOTYPE_ASSUMPTION"`) | **Do NOT promote**; replace with site trajectory. |
| **$10,000\text{ W}$ Water Pumping** | Research Prototype Assumption | [`system/config/loads.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/loads.yaml) | `SYNTHETIC_PROTOTYPE_PARAMETER` (`status_label: "PROTOTYPE_ASSUMPTION"`) | **Do NOT promote**; replace with pump specs. |
| **$5,000\text{ W}$ Secondary Heating** | Research Prototype Assumption | [`system/config/loads.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/loads.yaml) | `SYNTHETIC_PROTOTYPE_PARAMETER` (`status_label: "PROTOTYPE_ASSUMPTION"`) | **Do NOT promote**; replace with heater specs. |
| **$10/\text{Wh}$ Unmet Penalty** | Solver Prototype Weight | [`system/config/loads.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/loads.yaml) | `SYNTHETIC_SOLVER_WEIGHT` | Replace with multi-stage lexicographic solver. |
| **Total Demand `demand.point`** | Forecast Schema v1.0.0 | [`system/schemas/forecast_bundle.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/forecast_bundle.py) | `ESTABLISHED_TOTAL_DEMAND_INTERFACE` | **Do NOT relabel** as $P_{\text{critical}}$. |
| **Nuolja Station Physical Equipment** | Empirical Site Data | `NOT_FOUND` | `NOT_ESTABLISHED` / `DATA_BLOCKED` | Conduct Nuolja site electrical audit. |
| **Nuolja Station Circuit Map** | Empirical Site Data | `NOT_FOUND` | `NOT_ESTABLISHED` / `DATA_BLOCKED` | Conduct Nuolja breaker schedule audit. |

---

## Provenance Audit Summary

Zero synthetic parameters have been promoted to station engineering facts. Provenance boundaries between prototype research artifacts, sealed policy, and missing station data remain 100% intact.
