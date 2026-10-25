# POLARIS EMS — EMERGENCY CONDITION DETECTOR DECISION TABLE

## 1. COMPACT COMPONENT AUDIT TABLE

| Component | Existing Evidence in Repository | Status | Blocking? |
| :--- | :--- | :--- | :--- |
| **$T_{\text{required}}$** | 72h prototype test value governed; real-station value unresolved | `CLOSED_PROTOTYPE_ONLY` | No (for prototype) |
| **Battery State** | `battery_energy_wh` and `battery_soc_pct` in `StationState` | `ESTABLISHED` | No |
| **Battery Efficiency** | Discharge efficiency $\eta_{\text{dis}} = 0.92$ in `battery.yaml` & `milp.py` | `ESTABLISHED` | No |
| **Battery Endurance** | Available AC energy $E_{\text{usable,AC}} = (E_{\text{cell}} - 40\text{kWh}) \cdot 0.92$ | `ESTABLISHED` | No |
| **Fuel Remaining** | Missing from `StationState` schema; not currently exposed | `MISSING` | **YES** |
| **Generator Model** | Min 10 kW, Max 100 kW, Base 5.0 L/h, Marg 0.00025 L/Wh in `diesel.yaml` | `ESTABLISHED` | No |
| **Diesel Endurance** | Fuel rate formula established; depends on fuel remaining $V_{\text{fuel}}$ | `ESTABLISHED_DEPENDENT` | **YES** (by fuel) |
| **Critical Load** | Synthetic 30 kW in `loads.yaml`; 5-tier demand schema missing | `ADDITIVE_SCHEMA_REQUIRED` | **YES** |
| **72h Trajectory** | `ForecastBundle` covers 24h only; 72h forecast trajectory missing | `MISSING` | **YES** |
| **Zero Renewable** | HD-04 detector-local stress scenario ($P_{\text{solar}}=0, P_{\text{wind}}=0$) | `ESTABLISHED` | No |
| **Survivability Margin** | Primary = Time Margin ($M_r = T_r - T_{\text{required}}$); Energy & Ratio = Diagnostic Only | `GOVERNANCE_CLOSED` | **No** (Closed) |
| **E3 Resource Guidance** | Emergency policy preserves resource with larger time margin | `ESTABLISHED` | No |
| **Truth Firewall** | Strict causal isolation from future actual measurements | `ESTABLISHED` | No |

---

## 2. SUMMARY OF REMAINING BLOCKERS FOR 72H PROTOTYPE IMPLEMENTATION

To unblock implementation of the 72h prototype detector:
1. Add `fuel_remaining_liters` field to `StationState` schema (or additive extension).
2. Provide a governed 72h critical load forecast trajectory (or additive extension).
3. Finalize additive schema extensions for 5-tier demand and `EmergencyAssessment` payload.

*(Note: Survivability margin selection is now **GOVERNANCE_CLOSED** with Primary = Time Margin).*
