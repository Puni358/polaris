# POLARIS EMS — EMERGENCY CONDITION DETECTOR CAUSAL MODEL & TRUTH FIREWALL

## 1. TEXTUAL CAUSAL DIAGRAM

```
  ┌──────────────────────────────┐
  │ Current Observed StationState│
  │ - battery_energy_wh          │
  │ - battery_soc_pct            │
  │ - fuel_remaining_liters (gap)│
  │ - diesel_running state       │
  └──────────────┬───────────────┘
                 │
                 │              ┌──────────────────────────────┐
                 ├─────────────►│ Critical Load Trajectory     │
                 │              │ - D_critical(t) across 72h   │
                 │              └──────────────┬───────────────┘
                 │                             │
                 │              ┌──────────────┴───────────────┐
                 ├─────────────►│ Resolved T_required (72h)    │
                 │              └──────────────┬───────────────┘
                 │                             │
                 │              ┌──────────────┴───────────────┐
                 ├─────────────►│ Battery & Diesel Models      │
                 │              │ - eta_dis = 0.92             │
                 │              │ - F_rate = 5.0 + 0.00025*P   │
                 │              └──────────────┬───────────────┘
                 │                             │
                 │              ┌──────────────┴───────────────┐
                 └─────────────►│ HD-04 Stress Scenario        │
                                │ - P_solar = 0, P_wind = 0    │
                                └──────────────┬───────────────┘
                                               │
                                               v
                               ┌───────────────────────────────┐
                               │ EMERGENCY CONDITION DETECTOR  │
                               └───────────────┬───────────────┘
                                               │
                                               v
                               ┌───────────────────────────────┐
                               │   Endurance Transformations   │
                               │   - T_batt (Battery Hours)    │
                               │   - T_diesel (Diesel Hours)   │
                               └───────────────┬───────────────┘
                                               │
                                               v
                               ┌───────────────────────────────┐
                               │   Authoritative Margins & Diag│
                               │   - Primary: M_r = T_r - T_req│
                               │   - Diag: Energy & Ratio      │
                               └───────────────┬───────────────┘
                                               │
                                               v
                               ┌───────────────────────────────┐
                               │    Classification Decision    │
                               │ NORMAL / EMERGENCY /          │
                               │ FAIL_CLOSED / GOV_REQUIRED    │
                               └───────────────┬───────────────┘
                                               │
                                               v
                               ┌───────────────────────────────┐
                               │      Energy Optimizer         │
                               │ Consumes mode & time margins  │
                               │ for E3 preservation decision  │
                               └───────────────────────────────┘
```

---

## 2. TRUTH FIREWALL & CAUSAL ISOLATION AUDIT

### 2.1 Permitted Inputs (At Decision Origin $t_0$):
- Current observed `StationState` at $t_0$.
- Causal critical load trajectory $D_{\text{critical}}(t)$ covering $T_{\text{required}}$.
- Governed physical parameters (`battery.yaml`, `diesel.yaml`).
- Exogenous resolved $T_{\text{required}}$ value ($72\text{h}$ synthetic test parameter).
- Detector-local stress scenario ($P_{\text{solar}}=0, P_{\text{wind}}=0$).

### 2.2 Prohibited Future Actual Data (Strictly Blocked by Truth Firewall):
- Future actual solar irradiance or generation measurements ($t > t_0$).
- Future actual wind speed or generation measurements ($t > t_0$).
- Future actual station demand realization ($t > t_0$).
- Future actual fuel consumption or battery SOC measurements ($t > t_0$).

---

## 3. TRANSFORMATIONS & OUTPUTS

1. **Battery Endurance ($T_{\text{batt}}$)**: Time until $E_{\text{usable,AC}} = (E_{\text{stored}} - 40\text{kWh}) \cdot 0.92$ is depleted by $D_{\text{critical}}(t)$ under $P_{\text{solar}}=0, P_{\text{wind}}=0$.
2. **Diesel Endurance ($T_{\text{diesel}}$)**: Time until remaining fuel $V_{\text{fuel}}$ is depleted by generator running to supply $D_{\text{critical}}(t)$ under $P_{\text{solar}}=0, P_{\text{wind}}=0$.
3. **Primary Time Margins**: $M_{\text{batt}} = T_{\text{batt}} - T_{\text{required}}$, $M_{\text{diesel}} = T_{\text{diesel}} - T_{\text{required}}$.
4. **Diagnostic Metrics**: Energy Margins ($E_{\text{margin,r}}$) and Survivability Ratios ($R_r = \frac{T_r}{T_{\text{required}}}$). Non-governing.
5. **Classification**:
   - If $T_{\text{required}}$ missing, invalid, stale, or unauthorized $\implies$ **`FAIL_CLOSED`**.
   - If other required detector input missing/unresolved $\implies$ **`GOVERNANCE_REQUIRED`** (do not default to FAIL_CLOSED or EMERGENCY).
   - Else if $M_{\text{batt}} \ge 0$ AND $M_{\text{diesel}} \ge 0 \implies$ **`NORMAL`**.
   - Else $\implies$ **`EMERGENCY`** (Preserved Resource = larger $M_r$, Limiting Resource = smaller $M_r$).
