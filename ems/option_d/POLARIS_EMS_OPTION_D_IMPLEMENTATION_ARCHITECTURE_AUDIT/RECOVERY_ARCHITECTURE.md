# RECOVERY ARCHITECTURE

## 1. STATE RECOVERY STATE MACHINE SPECIFICATION

The audit established the recovery state machine architecture for transitioning from emergency/degraded modes back to valid normal operation.

---

## 2. STATE MACHINE DIAGRAM

```text
               ┌─────────────────────────────────────────────────┐
               │                  NORMAL Mode                    │
               └────────┬────────────────────────────────▲───────┘
                        │                                │
                 m < 0  │                                │  m >= 0 AND
                        │                                │  Operator Clear
                        ▼                                │  Fresh Telemetry
               ┌─────────────────────────────────────────┴───────┐
               │          OPTION_D_EMERGENCY Mode                │
               └────────┬────────────────────────────────▲───────┘
                        │                                │
         t_degraded     │                                │  Operator Action /
         >= t_max OR    │                                │  Fresh Horizon
         Resource Limit │                                │
                        ▼                                │
               ┌─────────────────────────────────────────┴───────┐
               │           OPERATOR ESCALATION                   │
               └─────────────────────────────────────────────────┘
```

---

## 3. GOVERNED RECOVERY REQUIREMENTS
1. **Survivability Margin Verification**: Recovery to `NORMAL` mode requires ECD to return `operating_mode == OperatingMode.NORMAL` ($m_{\text{battery}} \ge 0$ AND $m_{\text{diesel}} \ge 0$) based on fresh telemetry.
2. **Freshness & Provenance Check**: Telemetry timestamp must be within configured freshness window (`max_telemetry_age_seconds`).
3. **Hysteresis / Stability Guard**: To prevent rapid mode oscillation (chattering) between `NORMAL` and `EMERGENCY`, recovery requires survivability margin $m \ge \epsilon_{\text{recovery}}$ for at least $N_{\text{stable}}$ consecutive MPC timesteps (e.g. 2 hours).
4. **Operator Acknowledgment**: If operator escalation was previously triggered, returning to `NORMAL` requires an explicit operator acknowledgment event log.
