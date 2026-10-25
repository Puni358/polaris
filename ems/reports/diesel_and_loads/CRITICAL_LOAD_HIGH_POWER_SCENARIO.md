# POLARIS — HIGH-POWER POLAR SYNTHETIC CRITICAL-LOAD SCENARIO SPECIFICATION

```
SELECTED_CRITICAL_LOAD_SCENARIO = DELIBERATELY_CONSERVATIVE_SYNTHETIC_DESIGN
P_CRITICAL_KW = 11.60
P_CRITICAL_TIME_VARIATION = CONSTANT
CRITICAL_LOAD_STATUS = SYNTHETIC_ENGINEERING_SCENARIO
REAL_NUOLJA_CRITICAL_LOAD = NOT_ESTABLISHED
P_CRITICAL_BASIS = DELIBERATELY_CONSERVATIVE_SYNTHETIC_DESIGN
```

## 1. Executive Summary & Human Governance Decision

By authoritative human project-owner decision, the critical load for the POLARIS 2024 annual synthetic experiment is locked as a **CONSTANT protected load requirement**:

$$P_{\text{critical}}(t) = 11,600 \text{ W} \quad (11.60 \text{ kW}) \quad \forall \, t \in [1, 8784]$$

This value represents a **Deliberately Conservative Synthetic Design Scenario** for polar research-station survivability under standard indoor comfort conditions ($T_{\text{in}} = +18.0^\circ\text{C}$).

*   **IMPORTANT**: This value is explicitly classified as `SYNTHETIC_ENGINEERING_SCENARIO` and `REAL_NUOLJA_CRITICAL_LOAD = NOT_ESTABLISHED`.
*   It must **never** be cited as measured Nuolja station load or validated empirical station data.

---

## 2. Component Composition & Provenance Distinction

The $11.60\text{ kW}$ constant critical load comprises:

1.  **Essential Heating ($P_{\text{heating,design}}$)**: **10.50 kW** ($10.00\text{ kW}$ thermal load at $T_{\text{in}} = +18^\circ\text{C}, T_{\text{out}} = -28^\circ\text{C}, v_{\text{wind}} = 15\text{ m/s}$ + $0.50\text{ kW}$ active water pipe trace heating).
2.  **Water System ($P_{\text{water}}$)**: **0.80 kW** (Continuous raw water intake feed pump, UV sterilization, and reverse osmosis purification).
3.  **Emergency Communications ($P_{\text{comms}}$)**: **0.30 kW** (Continuous Iridium Certus / VSAT satellite modem, VHF emergency radio base station, Campbell data logger, and network core).

$$P_{\text{critical}} = 10.50 + 0.80 + 0.30 = \mathbf{11.60\text{ kW}}$$

---

## 3. Explicit Quantification of Conservative Design Margin

To maintain technical transparency, the distinction between the physical survival-core equation output and the human-selected design requirement is preserved:

*   **Equation-Derived Survival-Core Requirement ($T_{\text{in}} = +10.0^\circ\text{C}$)**:
    $$P_{\text{heating,eq}}(-28^\circ\text{C}, 15\text{ m/s}) = 8.765\text{ kW} \implies P_{\text{critical,eq}} = \mathbf{9.865\text{ kW}}$$
*   **Human-Selected Conservative Design Requirement ($T_{\text{in}} = +18.0^\circ\text{C}$)**:
    $$P_{\text{heating,design}} = 10.500\text{ kW} \implies P_{\text{critical,design}} = \mathbf{11.600\text{ kW}}$$
*   **Explicit Peak Design Margin**:
    $$\text{Margin}_{\text{peak}} = 11.600\text{ kW} - 9.865\text{ kW} = \mathbf{+1.735\text{ kW}} \quad (+17.5\% \text{ above survival core})$$

---

## 4. 8,784-Hour Trajectory Validation & Compatibility

*   **Rows**: **8,784**
*   **Min**: **11.60 kW**
*   **Max**: **11.60 kW**
*   **Mean**: **11.60 kW**
*   **Median**: **11.60 kW**
*   **Fixture Minimum Station Total Demand**: **15.00 kW** ($15,000\text{ W}$)
*   **Compatibility Check**: $P_{\text{critical}}(t) \le P_{\text{total\_demand}}(t)$ holds for **8,784 / 8,784 hours (100% PASS)**.
*   **Maximum Ratio**: $\frac{11.60\text{ kW}}{15.00\text{ kW}} = \mathbf{77.33\%}$.

---

## 5. Implementation & Precedence

*   `system/config/loads.yaml` is updated to `baseline_power_w: 11600.0` with `status_label: "DELIBERATELY_CONSERVATIVE_SYNTHETIC_DESIGN"`.
*   The prototype default of $30\text{ kW}$ is overridden and cannot displace the selected $11.60\text{ kW}$ campaign scenario.
*   `PROTECTED_COMPONENT_MODIFICATIONS = 0`. All 6 protected components remain untouched.
*   `365D_CAMPAIGN = NOT_PERFORMED`. No annual campaign execution has occurred.
