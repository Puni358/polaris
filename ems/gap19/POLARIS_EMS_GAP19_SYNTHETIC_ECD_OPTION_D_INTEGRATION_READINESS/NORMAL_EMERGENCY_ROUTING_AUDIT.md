# NORMAL → EMERGENCY Routing Audit

## State Transition Boundaries & Decoupling

```text
                               ┌─────────────────────────┐
                               │  StationState & Config  │
                               └────────────┬────────────┘
                                            │
                               ┌────────────▼────────────┐
                               │   ECD Evaluator Core    │
                               └────────────┬────────────┘
                                            │
                    ┌───────────────────────┴───────────────────────┐
                    │                                               │
        m_battery >= 0 AND m_diesel >= 0             m_battery < 0 OR m_diesel < 0
                    │                                               │
         ┌──────────▼──────────┐                         ┌──────────▼──────────┐
         │ Mode = NORMAL       │                         │ Mode = EMERGENCY    │
         └──────────┬──────────┘                         └──────────┬──────────┘
                    │                                               │
       ┌────────────┴────────────┐                     ┌────────────┴────────────┐
       │ Is s_J2 > 0?            │                     │ Select Option D        │
       │  YES -> Log shortfall   │                     │ Protected Critical Load │
       │  NO  -> Full reserve    │                     │ Fallback Solver         │
       │ Route: Option B MPC     │                     └─────────────────────────┘
       └─────────────────────────┘
```

## Transition Decoupling Matrix

| Situation | $s_{J2}$ Status | ECD Margins ($m_b, m_d$) | Declared Operating Mode | Selected EMS Policy |
| :--- | :--- | :--- | :--- | :--- |
| **A. Nominal Reserve** | $s_{J2} = 0$ | $m_b \ge 0, m_d \ge 0$ | `NORMAL` | Option B Native HiGHS MPC |
| **B. Reserve Shortfall** | $s_{J2} > 0$ | $m_b \ge 0, m_d \ge 0$ | `NORMAL` | Option B Native HiGHS MPC (Degraded penalty) |
| **C. Resource Depletion** | $s_{J2} > 0$ | $m_b < 0$ or $m_d < 0$ | `EMERGENCY` | Option D Critical-Load Fallback |
| **D. Invalid Input** | N/A | Telemetry / Auth fault | `UNKNOWN_INVALID` | Fail-Closed Safety Boundary |

---

## Verdict
The decoupling between reserve shortfall ($s_{J2} > 0$) and Emergency Declaration (`EMERGENCY`) is complete and governed.
