# POLARIS EMS — HD-01B (N = 6h) Source Evidence Map

**Governance Scope**: Traceability map of governance decision HD-01B ($N = 6\text{h}$) across specification files, audit artifacts, and system configurations.

---

## 1. Traceability & Source Mapping Matrix

| Specification / Artifact | Location / File Path | Relevant Line / Section | Status Prior to Update | Governed State After Closure |
| :--- | :--- | :--- | :--- | :--- |
| **HD-01B Governance Decision** | User Request & Closure Artifact | `HD-01B` | `UNRESOLVED` | `CLOSED ($N = 6\text{ HOURS}$)` |
| **Authoritative EBR Formula** | [`POLARIS_EMS_HD01B_N6H_CLOSURE.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD01B_N6H_CLOSURE/POLARIS_EMS_HD01B_N6H_CLOSURE.md#L15) | Section 1 | Candidate formula with variable $N$ | $E_{\text{EBR\_target}}(t) = \sum_{k=t+1}^{t+6\text{h}} \frac{D_{\text{critical}}(k) \Delta t}{\eta_{\text{dis}}}$ |
| **Terminal Target (HD-02)** | [`POLARIS_EMS_HD02_TERMINAL_TARGET_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD02_TERMINAL_TARGET_AUDIT/POLARIS_EMS_HD02_TERMINAL_TARGET_AUDIT.md) | Section 4 | $E_{\text{terminal\_target}} = E_{\text{EBR\_target}}(H)$ | `COMPATIBLE` (Evaluates steps $H+1 \dots H+6$) |
| **Survival Window (HD-03)** | [`POLARIS_HD03_SURVIVAL_WINDOW_EVIDENCE.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_HD03_SURVIVAL_WINDOW_EVIDENCE.md) | Executive Summary | $T_{\text{required}}$ unresolved | `CONFIRMED INDEPENDENT` ($T_{\text{required}} \neq N$) |
| **MPC Decision Horizon $H$** | [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L72) | L72 | $H = 24\text{h}$ | `CONFIRMED INDEPENDENT` ($H = 24\text{h} \neq N=6\text{h}$) |
| **Prior HD-01B Evidence Audit** | [`POLARIS_EMS_HD01B_N_EVIDENCE_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD01B_N_EVIDENCE_AUDIT/POLARIS_EMS_HD01B_N_EVIDENCE_AUDIT.md) | Entire File | Recorded $N$ as unresolved pre-closure | `PRESERVED` (Retained as historical evidence) |

---

## 2. Stale Reference & Historical Handling Report

- **Stale Active References**: `0` (Zero active policy documents conflict with $N=6\text{h}$).
- **Historical Evidence Artifacts**: Preserved without modification. Historical audit packages (such as `POLARIS_EMS_HD01B_N_EVIDENCE_AUDIT`) accurately document the pre-closure evidence audit stage that led to stakeholder decision-making.
- **Codebase Boundary**: Source code files (`milp.py`, `loads.yaml`, `battery.yaml`) remain untouched in compliance with `IMPLEMENTATION_STATE = NOT_AUTHORIZED`.
