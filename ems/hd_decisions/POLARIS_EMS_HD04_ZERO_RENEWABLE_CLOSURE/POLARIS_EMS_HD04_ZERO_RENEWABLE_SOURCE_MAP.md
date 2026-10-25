# POLARIS EMS — HD-04 Option A Source Evidence Map

**Governance Scope**: Traceability map of HD-04 Option A Zero-Renewable Emergency Survivability Baseline governance decision across system files and audit records.

---

## 1. Traceability & Source Mapping Matrix

| Specification / Artifact | Location / File Path | Relevant Line / Section | Pre-Closure Status | Governed State After Closure |
| :--- | :--- | :--- | :--- | :--- |
| **HD-04 Stakeholder Decision** | User Request & Closure Package | `HD-04` | `OPEN (Decision Required)` | `CLOSED (Option A Zero-Renewable)` |
| **Formal Policy Wording** | [`POLARIS_EMS_HD04_ZERO_RENEWABLE_CLOSURE.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD04_ZERO_RENEWABLE_CLOSURE/POLARIS_EMS_HD04_ZERO_RENEWABLE_CLOSURE.md#L11) | Section 1 | Option A proposal | Authoritative Human Policy Statement |
| **Prior HD-04 Evidence Audit** | [`POLARIS_EMS_HD04_ADVERSE_RENEWABLE_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD04_ADVERSE_RENEWABLE_AUDIT/HD04_ADVERSE_RENEWABLE_AUDIT.md) | L54, L182 | Recorded $P=0$ as open proposal | `PRESERVED` (Retained as historical evidence) |
| **Prior HD-04 Governance Audit**| [`POLARIS_EMS_HD04_ADVERSE_RENEWABLE_GOVERNANCE_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD04_ADVERSE_RENEWABLE_GOVERNANCE_AUDIT/POLARIS_EMS_HD04_ADVERSE_RENEWABLE_GOVERNANCE_AUDIT.md) | L40 | `HD04_HUMAN_DECISION_REQUIRED = YES` | `PRESERVED` (Historical evidence of pre-closure audit) |
| **MILP Point Forecasts** | [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L68-L69) | L68-L69 | Point forecasts used in MPC | `UNCHANGED` (Normal MPC point forecasts protected) |

---

## 2. Stale Reference & Historical Handling Report

- **Stale Active References**: `0` (Zero active policy documents conflict with HD-04 Option A).
- **Historical Evidence Artifacts**: Preserved without modification. Historical audit packages (`POLARIS_EMS_HD04_ADVERSE_RENEWABLE_AUDIT` and `POLARIS_EMS_HD04_ADVERSE_RENEWABLE_GOVERNANCE_AUDIT`) accurately record the evidence evaluation stage that preceded stakeholder selection.
- **Codebase Boundary**: Source code files (`milp.py`, `loads.yaml`, `battery.yaml`) remain untouched in compliance with `IMPLEMENTATION_STATE = NOT_AUTHORIZED`.
