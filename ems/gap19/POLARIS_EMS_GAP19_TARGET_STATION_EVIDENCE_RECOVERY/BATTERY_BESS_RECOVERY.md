# POLARIS EMS GAP19 — BATTERY / BESS RECOVERY

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_TARGET_STATION_EVIDENCE_RECOVERY`  
**Domain B**: **BATTERY ENERGY STORAGE SYSTEM (BESS)**  

---

## 1. Disambiguation of BESS Parameter Layers

```text
NOMINAL_SPECIFICATION (Manufacturer Nameplate)
        ≠
USABLE_OPERATIONAL_LIMIT (SOC 20%-95%, Power 50kW)
        ≠
GOVERNED_EMERGENCY_LIMIT (Emergency Discharge Floor)
```

---

## 2. Granular Recovery Audit Matrix

| Battery Parameter | Nominal Spec | Usable Limit | Governed Limit | Recovery Status | Classification |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Battery Capacity ($C_{\text{bat}}$)** | Un-documented | $200\text{ kWh}$ (config) | Un-established | `NOT_ESTABLISHED` | `SYNTHETIC_ENGINEERING_ASSUMPTION` |
| **Operational SOC Window** | Un-documented | $20\%\dots95\%$ (config) | Un-established | `NOT_ESTABLISHED` | `IMPLEMENTATION_FACT` |
| **Discharge Efficiency ($\eta_{\text{dis}}$)** | Un-documented | $92\%$ (config) | Un-established | `NOT_ESTABLISHED` | `IMPLEMENTATION_FACT` |
| **Max Discharge Power ($P_{\text{dis,max}}$)** | Un-documented | $50\text{ kW}$ (config) | Un-established | `NOT_ESTABLISHED` | `IMPLEMENTATION_FACT` |
| **Thermal / Temperature Limits** | Un-documented | Unspecified | Un-established | `NOT_ESTABLISHED` | `NOT_ESTABLISHED` |

---

## 3. Recovery Outcome & Status

```text
BATTERY_ENGINEERING_INPUT_STATUS = NOT_ESTABLISHED
```

No target-station BESS datasheets, commissioning reports, or measured performance logs exist in local or external evidence repositories.
