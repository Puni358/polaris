# POLARIS EMS — T_REQUIRED & OPTION D ARCHITECTURAL BOUNDARY

## 1. Executive Summary

This document re-establishes the strict architectural boundary between **ECD $T_{\text{required}}$** and **Option D — Protected Critical-Load Fallback** (sealed in DEC-004).

---

## 2. Parametric Separation Matrix

| Architectural Subsystem | ECD Risk Classification | Option D Degraded Fallback |
| :--- | :--- | :--- |
| **Governing Parameter** | **$T_{\text{required}}$** ($T_{\text{required\_baseline}} = 6\text{h}$) | **$T_{\text{max,degraded}}$** (Option D Watchdog Timer) |
| **Secondary Parameter** | N/A (Consumes $C_{\text{usable}}, \text{Fuel}_{\text{rem}}$) | **$F_{\text{reserve,min}}$** (Volumetric Fuel Floor) |
| **Subsystem Location** | Emergency Condition Detector (`system/control/ecd.py`) | EMS Mode Manager / Safe State (`system/control/mode.py`) |
| **Primary Responsibility** | Evaluate $T_{\text{battery}}, T_{\text{diesel}}$ vs $T_{\text{required}}$ under zero-renewable stress. | Manage protected critical loads ($P_{\text{critical}}$) after `UNKNOWN_INVALID`. |
| **Trigger Mechanism** | Evaluated continuously at every control loop step. | Initiated upon entering Option D degraded state. |
| **Failure Behavior** | Missing/Invalid $T_{\text{required}} \rightarrow$ Emit `UNKNOWN_INVALID`. | Expired $T_{\text{max,degraded}}$ OR $F_{\text{rem}} \le F_{\text{reserve,min}} \rightarrow$ Mandatory Rule D5 Escalation. |
| **Sealed Governance Status** | Baseline $6\text{h}$ sealed under `TREQ-001`. | Option D Policy sealed under DEC-004. |

---

## 3. Boundary Rules

1. **No Merging**: $T_{\text{required}}$ and $T_{\text{max,degraded}}$ MUST NOT be merged or combined into a single parameter.
2. **Independent Escalation**: Expiration of $T_{\text{max,degraded}}$ triggers mandatory operator escalation under Option D Rule D5. It does NOT modify or recalculate $T_{\text{required}}$.
3. **Open Status Preserved**: $T_{\text{max,degraded}}$ and $F_{\text{reserve,min}}$ remain OPEN parameters to be resolved in dedicated Option D implementation gating tasks.
