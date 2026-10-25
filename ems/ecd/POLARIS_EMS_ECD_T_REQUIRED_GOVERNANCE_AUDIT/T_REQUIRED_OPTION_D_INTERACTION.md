# POLARIS EMS — T_REQUIRED & OPTION D INTERACTION ARCHITECTURE AUDIT

## 1. Executive Summary

This document establishes the architectural boundary and interaction contract between **ECD $T_{\text{required}}$** and **Option D — Protected Critical-Load Fallback**.

> [!IMPORTANT]
> **PARAMETRIC SEPARATION FIREWALL**:
> $T_{\text{required}}$ (ECD survivability horizon) and $T_{\text{max,degraded}}$ (Option D degraded-operation watchdog duration) are **DISTINCT PARAMETERS** located in different architectural subsystems. They must **NOT** be conflated or combined into a single parameter.

---

## 2. Architectural Pipeline & Control Flow

```
┌─────────────────────────────────────────────────────────────┐
│             Emergency Condition Detector (ECD)              │
│ Evaluates T_battery and T_diesel against T_required         │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼ EmergencyAssessment
┌─────────────────────────────────────────────────────────────┐
│                      EMS Mode Manager                       │
│  If assessment is UNKNOWN_INVALID ──► Engage Option D       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│         Option D Protected Critical-Load Fallback           │
│ Maintains P_critical while tracking:                        │
│   - Watchdog timer (T_max,degraded)                         │
│   - Fuel reserve floor (F_reserve,min)                      │
│ Triggers mandatory D5 escalation upon reaching either.      │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Subsystem Comparison Matrix

| Attribute | ECD $T_{\text{required}}$ | Option D Watchdog $T_{\text{max,degraded}}$ |
| :--- | :--- | :--- |
| **Subsystem Owner** | Emergency Condition Detector (`system/control/ecd.py`) | Option D Fallback / Mode Manager (`system/control/mode.py`) |
| **Primary Function** | Evaluate resource endurance ($T_{\text{bat}}, T_{\text{dsl}}$) under zero-renewable stress. | Monitor duration spent in degraded fallback mode after `UNKNOWN_INVALID`. |
| **Output State** | `NORMAL` / `EMERGENCY` / `UNKNOWN_INVALID` | Escalation alert / Operator notification under Rule D5. |
| **Trigger Mechanism** | Evaluated continuously at every control step. | Initiated upon entering Option D degraded state. |
| **Failure Effect** | Missing $T_{\text{required}} \rightarrow$ immediately emit `UNKNOWN_INVALID`. | Expired $T_{\text{max,degraded}} \rightarrow$ mandatory operator escalation (D5). |
| **Default Value** | `NOT_ESTABLISHED` (Prototype used 72h). | `NOT_ESTABLISHED` (No threshold authorized). |

---

## 4. Key Architectural Interaction Rules

1. **ECD Drives Option D Entry**: Option D fallback is engaged *because* ECD returns `UNKNOWN_INVALID` (or because a critical fault occurs). Option D does NOT compute or modify $T_{\text{required}}$.
2. **Independent Watchdog Monitoring**: Once inside Option D fallback, the system monitors $T_{\text{max,degraded}}$ as a safety timer. $T_{\text{max,degraded}}$ may be significantly shorter than $T_{\text{required}}$ (e.g. 2 hours of degraded operation allowed before operator escalation, even if station survivability horizon $T_{\text{required}}$ is 72 hours).
3. **No Dynamic Modification**: Neither ECD nor Option D may dynamically alter $T_{\text{required}}$ or $T_{\text{max,degraded}}$ at runtime without authenticated governance authorization.
