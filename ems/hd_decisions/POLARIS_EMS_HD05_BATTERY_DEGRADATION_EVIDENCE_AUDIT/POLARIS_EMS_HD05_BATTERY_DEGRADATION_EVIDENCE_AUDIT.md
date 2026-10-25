# POLARIS EMS — HD-05 BATTERY DEGRADATION EVIDENCE AUDIT REPORT

**Phase**: Human Governance Decision HD-05 Read-Only Evidence Audit  
**Audit Date**: 2026-09-22  
**Audit Status**: COMPLETED (READ-ONLY TECHNICAL AND GOVERNANCE EVIDENCE AUDIT)  
**Output Package**: `POLARIS_EMS_HD05_BATTERY_DEGRADATION_EVIDENCE_AUDIT`  

---

## 1. Executive Summary & Required Final Classifications

This report provides the read-only technical and governance evidence audit for **Human Governance Decision HD-05**:
> *"How does the existing POLARIS implementation represent battery degradation/cycling, what physical meaning does it have, and what remains unresolved for the governed HD-05 policy?"*

All findings in this report are grounded strictly in inspected source code, configuration files, and authorized governance artifacts. No code modifications, parameter selections, or solver executions were performed.

### Final Governed Classifications

| Metric | Governed Classification | Justification |
| :--- | :--- | :--- |
| **`HD05_CURRENT_MODEL_STATUS`** | **`ENGINEERING_THROUGHPUT_PROXY`** | The existing model is a simple linear energy throughput penalty; it contains zero electrochemistry aging physics. |
| **`HD05_CDEG_STATUS`** | **`UNCALIBRATED_MONETARY_PENALTY`** | `c_deg = $0.00005/Wh` ($0.05/kWh) is an static monetary throughput penalty in code, not a calibrated battery replacement cost. |
| **`HD05_PHYSICAL_AGING_CALIBRATION`** | **`NOT_ESTABLISHED`** | Confirmed by [`POLARIS_SYSTEM_D5_SCIENTIFIC_INTERPRETATION.md:L261`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_SYSTEM_D5_SCIENTIFIC_INTERPRETATION.md#L261): physical component aging calibration is `LEVEL 3 — NOT ESTABLISHED`. |
| **`HD05_THROUGHPUT_PROXY_STATUS`** | **`CURRENTLY_IMPLEMENTED`** | Implemented as linear penalty on charge and discharge power: $c_{\text{deg}} \cdot (p_{\text{chg}} + p_{\text{dis}}) \Delta t$. |
| **`HD05_UNIT_COMPATIBILITY_WITH_FUEL`** | **`CONVERSION_REQUIRED`** | Combining fuel Liters $[\text{L}]$ and degradation Dollars $[\$]$ in Stage 3 requires an authorized monetary fuel cost parameter ($\$2.50/\text{L}$). |
| **`HD05_NORMAL_MODE_COMPATIBILITY`** | **`STAGE3_COMPATIBLE`** | Compatible with Stage 3 resource management during `NORMAL` operation to trade diesel generation against battery throughput. |
| **`HD05_EMERGENCY_MODE_COMPATIBILITY`** | **`OVERRIDE_REQUIRED`** | Policy HD-05C requires dynamic suppression ($c_{\text{deg}} = 0.0$) during emergency operation, which requires a code override. |
| **`HD05_STAGE3_PLACEMENT`** | **`STAGE3_RESOURCE_MANAGEMENT`** | Fixed governance policy: battery degradation belongs to Stage 3 resource management. |
| **`HD05_NUMERICAL_TRADEOFF_STATUS`** | **`GOVERNANCE_DECISION_REQUIRED`** | The numerical fuel↔degradation tradeoff coefficient remains unresolved and requires human governance authorization. |
| **`HD05_SCHEMA_STATUS`** | **`ADDITIVE_EXTENSION_REQUIRED`** | `StationState` schema lacks SOH / battery health tracking fields, requiring additive schema extension for telemetry logging. |
| **`HD05_IMPLEMENTATION_AUTHORIZATION`** | **`NOT_GRANTED`** | Read-only evidence audit. Implementation authorization remains strictly **NOT_GRANTED**. |
| **`HD05_EXECUTION_AUTHORIZATION`** | **`NOT_GRANTED`** | Read-only evidence audit. Execution authorization remains strictly **NOT_GRANTED**. |

---

## 2. Authoritative HD-05 Governance Context

The following governance decisions are established and treated as fixed:

- **HD-05A Placement**: Battery degradation belongs to **Stage 3 — resource management**.
- **HD-05B Normal Mode Policy**: Extra diesel generation MAY be used to reduce unnecessary battery cycling during **NORMAL** operation.
- **HD-05C Emergency Subordination**: During **EMERGENCY** operation, battery degradation is subordinate to critical load reliability (Stage 1) and resilience (Stage 2). Battery preservation does not inhibit emergency load support.
- **HD-05D Numerical Tradeoff**: The numerical fuel↔degradation tradeoff coefficient remains **UNRESOLVED** (`GOVERNANCE_DECISION_REQUIRED`).

---

## 3. Answers to Primary Evidence Questions (Q1 – Q8)

### Q1: Location of Battery Degradation in Code
- **Configuration File**: [`system/config/battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L11)
  - Line 11: `deg_penalty_per_wh: 0.00005` (Comment: `# Cycling penalty`).
- **Optimizer File**: [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L33)
  - Line 33: `deg_penalty = float(bat_cfg.get("deg_penalty_per_wh", 0.00005))`
  - Line 109: `c[base + 4] = deg_penalty * dt * w_t  # p_chg ($/Wh * W * h)`
  - Line 110: `c[base + 5] = deg_penalty * dt * w_t  # p_dis ($/Wh * W * h)`

### Q2: Mathematical Formulation
The exact mathematical degradation term $J_{\text{deg}}$ implemented in `milp.py` is:

$$ J_{\text{deg}} = \sum_{t=0}^{H-1} c_{\text{deg}} \cdot \Delta t \cdot w_t \cdot \left( p_{\text{chg}}[t] + p_{\text{dis}}[t] \right) $$

where $c_{\text{deg}} = \$0.00005/\text{Wh}$ ($0.05 \$ /\text{kWh}$), $\Delta t = 1.0\text{ h}$, $w_t = \gamma^t$, $p_{\text{chg}}$ is charge power [W], and $p_{\text{dis}}$ is discharge power [W].

### Q3: Value and Nature of $c_{\text{deg}}$
- **Value**: `0.00005`
- **Units**: $\$ /\text{Wh}$ ($\$0.05/\text{kWh}$).
- **Nature**: It is a static monetary penalty on energy throughput, acting as an optimization regularizer (`# Cycling penalty`). It is **NOT** a calibrated battery replacement cost or electrochemistry aging parameter.

### Q4: Actual Degradation vs Throughput Proxy
- **Classification**: $\mathbf{ENGINEERING\_THROUGHPUT\_PROXY}$.
- It penalizes total linear energy throughput ($p_{\text{chg}} + p_{\text{dis}}$). It contains zero physics of battery aging.

### Q5: Capability Matrix

| Physical / Aging Feature | Present in Repo? | Exact File / Location | Used in Optimizer? | Repository Evidence / Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Charging Throughput** | **YES** | [`milp.py:L109`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L109) | **YES** | Penalized linearly at $c_{\text{deg}} \cdot p_{\text{chg}} \cdot \Delta t$ |
| **Discharging Throughput** | **YES** | [`milp.py:L110`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L110) | **YES** | Penalized linearly at $c_{\text{deg}} \cdot p_{\text{dis}} \cdot \Delta t$ |
| **Depth of Discharge (DoD)** | **NO** | N/A | **NO** | Penalty is strictly linear; independent of SOC level or cycle depth |
| **Cycle Count / Rainflow** | **NO** | N/A | **NO** | No cycle counting or rainflow algorithm implemented |
| **Equivalent Full Cycles (EFC)** | **NO** | N/A | **NO** | EFC is not computed, logged, or penalized |
| **C-rate / Power Stress** | **NO** | N/A | **NO** | Penalty is independent of C-rate relative to 200 kWh capacity |
| **SOC-Dependent Stress** | **NO** | N/A | **NO** | High SOC shelf stress (e.g. 95%) and low SOC stress are unpenalized |
| **Calendar Aging** | **NO** | N/A | **NO** | No time-dependent capacity fade or shelf-life degradation |
| **Temperature Effects** | **NO** | N/A | **NO** | Thermal model absent in degradation formulation |
| **Battery Chemistry** | **NO** | N/A | **NO** | Battery electrochemistry (LFP, NMC, Lead-Acid) unestablished in repo |
| **Charge/Discharge Asymmetry** | **NO** | [`milp.py:L109-110`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L109) | **NO** | $p_{\text{chg}}$ and $p_{\text{dis}}$ are penalized at identical coefficient $c_{\text{deg}}$ |
| **Partial-Cycle Aging** | **NO** | N/A | **NO** | No non-linear stress accumulation for partial cycles |
| **State of Health (SOH)** | **NO** | [`station_state.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/station_state.py) | **NO** | SOH state variable absent from schemas and state tracking |
| **Remaining Useful Life (RUL)**| **NO** | N/A | **NO** | Absent from schemas, optimizer, and simulation twin |

### Q6: Shallow vs Deep Cycle Discrimination
- **Shallow Cycle ($10\% \text{ DoD}$)**: Throughput = $40\text{ kWh} \implies \text{Penalty} = \$2.00$.
- **Deep Cycle ($70\% \text{ DoD}$)**: Throughput = $280\text{ kWh} \implies \text{Penalty} = \$14.00$.
- **Finding**: The model penalizes deep cycles purely linearly ($7\times \text{energy} = 7\times \text{penalty}$). It fails to represent non-linear electrochemistry stress acceleration (where deep cycles cause exponentially higher degradation per Wh).

### Q7: Cycle Frequency, SOC Range, and Rate Discrimination
- The current linear term **CANNOT** distinguish one large cycle from many small cycles of equal throughput, sustained high SOC resting stress, or rapid high C-rate cycling versus slow gentle cycling.

### Q8: Empirical Battery-Aging Calibration
- Repository search confirms zero battery datasheets, cycle-life curves, SOH telemetry, or capacity fade measurements exist.
- Confirmed by [`POLARIS_SYSTEM_D5_SCIENTIFIC_INTERPRETATION.md:L261`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_SYSTEM_D5_SCIENTIFIC_INTERPRETATION.md#L261): physical component aging calibration is `LEVEL 3 — NOT ESTABLISHED`.

```
BATTERY_AGING_CALIBRATION = NOT_ESTABLISHED
```

---

## 4. Dimensional & Unit Audit

- $J_{\text{deg}} = (\$/\text{Wh}) \cdot (\text{W} \cdot \text{h}) = \$ \quad [\text{Currency Dollars}]$.
- $J_{\text{fuel}} = \text{Liters of diesel} \quad [\text{L}]$.
- **Direct Addition Check**: Adding Liters $[\text{L}]$ directly to Dollars $[\$]$ is **dimensionally invalid**.
- **Conversion Requirement**: Combining fuel and degradation in Stage 3 requires an authorized monetary fuel cost parameter ($\text{fuel\_cost\_per\_l} = \$2.50/\text{L}$) or exchange factor ($\lambda_{\text{fuel\_deg}}$ $[\text{L}/\text{Wh}]$).

```
UNIT_CONVERSION_REQUIREMENT = REQUIRED
```

---

## 5. Implementation Facts vs Governance Policy

| Item / Feature | Classification | Source / Location |
| :--- | :--- | :--- |
| $c_{\text{deg}} = 0.00005 \$ /\text{Wh}$ | **CURRENT IMPLEMENTATION FACT** | [`battery.yaml:L11`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L11) |
| Throughput Equation $c_{\text{deg}} (p_{\text{chg}}+p_{\text{dis}}) \Delta t$ | **CURRENT IMPLEMENTATION FACT** | [`milp.py:L109-110`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L109) |
| Battery Capacity $200\text{ kWh}$ | **CURRENT IMPLEMENTATION FACT** | [`battery.yaml:L3`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L3) |
| Technical SOC Floor $20\%$ | **CURRENT IMPLEMENTATION FACT** | [`battery.yaml:L4`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L4) |
| Inverter Efficiency $\eta=0.92$ | **CURRENT IMPLEMENTATION FACT** | [`battery.yaml:L6-7`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L6) |
| Stage 3 Placement for Degradation (HD-05A) | **STAKEHOLDER POLICY DECISION** | Decided in HD-05 Policy Charter |
| Normal-Mode Extra Diesel for Cycling (HD-05B) | **STAKEHOLDER POLICY DECISION** | Decided in HD-05 Policy Charter |
| Emergency Degradation Subordination (HD-05C) | **STAKEHOLDER POLICY DECISION** | Decided in HD-05 Policy Charter |
| Numerical Fuel↔Degradation Tradeoff (HD-05D) | **UNRESOLVED GOVERNANCE ITEM** | `GOVERNANCE_DECISION_REQUIRED` |

---

## 6. Stage-3 Compatibility Audit

- **Option A (Retain Linear Throughput Proxy)**: Fully supported in current [`milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py). Requires governance authorization of $c_{\text{deg}}$ as Stage 3 cycling penalty coefficient.
- **Option B (Non-Linear DoD Aging Model)**: `NOT_ESTABLISHED`. Requires non-linear MINLP solver (incompatible with linear HiGHS solver) and empirical aging curves.
- **Option C (Economic Battery Replacement Surrogate)**: Supported linearly as $c_{\text{deg\_econ}} = \frac{C_{\text{replacement}}}{2 \cdot C_{\text{bat}} \cdot N_{\text{cycles}}}$. Requires governance authorization of battery replacement cost.
- **Option D (Governed Daily Throughput Budget)**: Supported linearly as $\sum (p_{\text{chg}}+p_{\text{dis}})\Delta t \le E_{\text{budget}}$. Requires governance authorization of daily cycle limit.

---

## 7. Emergency-Mode Compatibility

- [`milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py) currently applies $c_{\text{deg}}$ unconditionally across all timesteps (no operating mode switch).
- HD-05C policy implementation requires passing `operating_mode` from the Emergency Detector into `LocalMILPEnergyOptimizer` and dynamically overriding $c_{\text{deg}} = 0.0$ when `operating_mode != NORMAL`.

---

## 8. Scientific Validity Verdict & Answers to Key Questions

1. **What does POLARIS currently mean by "battery degradation"?**  
   It means a linear energy throughput penalty acting as an optimization regularizer to suppress unnecessary micro-cycling.
2. **Is it a physical degradation model or a cycling/throughput penalty?**  
   It is strictly an **engineering throughput proxy**.
3. **What exactly does $c_{\text{deg}}$ do?**  
   It assigns a static monetary penalty ($\$0.05/\text{kWh}$) per unit of charge and discharge energy throughput.
4. **Can the current formulation scientifically support the new HD-05 policy as-is?**  
   **YES for Option A (throughput proxy in Stage 3)** when paired with a monetary fuel cost parameter ($\$2.50/\text{L}$); **NO for physical aging physics** without new empirical data.
5. **What evidence is missing?**  
   Battery chemistry, cycle-life degradation curves, DoD non-linearity, temperature aging, battery replacement cost, SOH telemetry.
6. **What must be decided by governance?**  
   The numerical fuel↔degradation tradeoff coefficient (HD-05D), whether the linear throughput proxy is accepted for Stage 3 (HD-05E), and emergency override authorization (HD-05F).
7. **What can be implemented later without inventing unsupported science?**  
   Option A (throughput proxy with dynamic $c_{\text{deg}}=0.0$ emergency override) can be implemented immediately without inventing unsupported electrochemistry parameters.

---

## 9. Final Required Verdict & Declarations

```
HD05_IMPLEMENTATION_AUTHORIZATION=NOT_GRANTED
HD05_EXECUTION_AUTHORIZATION=NOT_GRANTED
HD05_NUMERICAL_TRADEOFF=GOVERNANCE_DECISION_REQUIRED
```
