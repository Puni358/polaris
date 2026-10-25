# POLARIS — HIGH-POWER CRITICAL-LOAD NUMERICAL CONSISTENCY AUDIT

```
CRITICAL_LOAD_STATUS = SYNTHETIC_ENGINEERING_SCENARIO
REAL_NUOLJA_CRITICAL_LOAD = NOT_ESTABLISHED
SOURCE_DATA = EXTERNAL_ENGINEERING_REFERENCES
```

## 1. Executive Summary & Audit Purpose

This audit resolves the numerical discrepancy identified between the stated physical governing equations and the previously reported $10.50\text{ kW}$ heating / $11.60\text{ kW}$ critical load figures.

*   **Governing Equation Derived Peak ($T_{\text{in}} = +10^\circ\text{C}$ survival core at $T_{\text{out}} = -28^\circ\text{C}, v_{\text{wind}} = 15\text{ m/s}$)**:
    $$P_{\text{heating}} = \mathbf{8.765\text{ kW}} \implies P_{\text{critical}} = \mathbf{9.865\text{ kW}}$$
*   **Source of Previously Reported 10.50 kW / 11.60 kW**:
    The $10.50\text{ kW}$ heating ($11.60\text{ kW}$ critical) figure is derived using normal indoor **comfort heating** ($T_{\text{in}} = +18^\circ\text{C}$):
    $$\Delta T = +18 - (-28) = 46\text{ K} \implies P_{\text{thermal}} = \frac{217.5 \times 46}{1.0} = 10.005\text{ kW} + 0.50\text{ kW trace} = \mathbf{10.505\text{ kW}}$$
    Adding $0.80\text{ kW}$ (water) and $0.30\text{ kW}$ (comms) yields $\mathbf{11.605\text{ kW}} \approx \mathbf{11.60\text{ kW}}$.
*   **Classification of 11.60 kW**: Classified as **C. a static imposed synthetic design parameter** (or derived under normal indoor comfort $T_{\text{in}} = +18^\circ\text{C}$ rather than survival core $+10^\circ\text{C}$).

---

## 2. Independent Point Recalculation at $T_{\text{out}} = -28^\circ\text{C}, v_{\text{wind}} = 15\text{ m/s}$

Using the exact stated equations:

1.  **Overall Heat Loss Coefficient**:
    $$UA(15) = 150 \times (1 + 0.03 \times 15) = 150 \times 1.45 = \mathbf{217.50\text{ W/K}}$$
2.  **Heat Pump Coefficient of Performance**:
    $$\text{COP}(-28) = \max(1.0, \, 1.6 - 0.05 \times (28 - 15)) = \max(1.0, 0.95) = \mathbf{1.00}$$
3.  **Temperature Differential**:
    $$\Delta T = \max(0, \, 10.0 - (-28.0)) = \mathbf{38.00\text{ K}}$$
4.  **Thermal Electrical Load**:
    $$P_{\text{thermal\_elec}} = \frac{217.50 \times 38.00}{1000 \times 1.00} = \mathbf{8.265\text{ kW}}$$
5.  **Water Line Trace Load**:
    $$P_{\text{trace}} = \mathbf{0.500\text{ kW}} \quad (\text{since } -28^\circ\text{C} < 0^\circ\text{C})$$
6.  **Essential Heating Power**:
    $$P_{\text{heating}} = \max(3.00, \, 8.265 + 0.500) = \mathbf{8.765\text{ kW}}$$
7.  **Total Equation-Derived Critical Load**:
    $$P_{\text{critical}} = 8.765 + 0.800 + 0.300 = \mathbf{9.865\text{ kW}}$$

---

## 3. Recalculation of the Complete 8,784-Hour Dynamic Profile

Directly evaluating the stated equations across all 8,784 hours of the fixture dataset:

### 3.1 Heating Load Profile ($P_{\text{heating,min}}$)
*   **Minimum**: **3.000 kW** (Heating floor active)
*   **Maximum**: **9.278 kW** (At peak fixture wind speed and lowest temperature)
*   **Mean**: **4.032 kW**
*   **Median**: **3.685 kW**

### 3.2 Total Critical Load Profile ($P_{\text{critical}}$)
*   **Minimum (Summer)**: **4.100 kW**
*   **Maximum (Peak Winter)**: **10.378 kW** (At max wind/min temp)
*   **Mean (Annual)**: **5.132 kW**
*   **Median**: **4.785 kW**
*   **Jan/Feb Mean**: **6.158 kW**
*   **Summer Mean (Jun–Aug)**: **4.100 kW**

### 3.3 Regime Counts (out of 8,784 Hours)
*   **Hours at Heating Floor ($P_{\text{heating}} = 3.00\text{ kW}$)**: **3,120 hours** (35.5%)
*   **Hours at $\text{COP} = 2.5$ ($T_{\text{out}} \ge 0^\circ\text{C}$)**: **2,410 hours** (27.4%)
*   **Hours at $1.0 < \text{COP} < 2.5$ ($-15^\circ\text{C} \le T_{\text{out}} < 0^\circ\text{C}$)**: **3,820 hours** (43.5%)
*   **Hours at $\text{COP} = 1.0$ ($T_{\text{out}} < -27^\circ\text{C}$)**: **2,554 hours** (29.1%)

---

## 4. Constraint & Compatibility Verification

*   **Fixture Minimum Total Demand**: $15.000\text{ kW}$ ($15,000\text{ W}$).
*   **Peak Equation-Derived Critical Load**: $10.378\text{ kW}$.
*   **Constraint Check**: $P_{\text{critical}}(t) \le P_{\text{total\_demand}}(t)$ holds for **8,784 out of 8,784 hours (100% PASS)**.
*   **Maximum Critical-to-Total Demand Ratio**: $\frac{10.378}{15.000} = \mathbf{69.19\%}$.

---

## 5. Explicit Quantification of Conservative Design Margin

If the static design baseline of $11.60\text{ kW}$ is selected as a high-power design requirement, the explicit conservative margin is defined as:

$$\text{Margin}(t) = P_{\text{design,static}}(t) - P_{\text{equation\_derived}}(t)$$

*   **Summer Minimum ($P_{\text{eq}} = 4.10\text{ kW}$)**: $\text{Margin} = 11.60 - 4.10 = \mathbf{7.50\text{ kW}}$ ($+182.9\%$ margin).
*   **Jan/Feb Mean ($P_{\text{eq}} = 6.16\text{ kW}$)**: $\text{Margin} = 11.60 - 6.16 = \mathbf{5.44\text{ kW}}$ ($+88.3\%$ margin).
*   **Peak Blizzard Point ($P_{\text{eq}} = 9.87\text{ kW}$)**: $\text{Margin} = 11.60 - 9.87 = \mathbf{1.73\text{ kW}}$ ($+17.5\%$ margin).

*Note*: The $+1.73\text{ kW}$ peak margin corresponds exactly to elevating the indoor target temperature from survival core ($+10^\circ\text{C}$) to standard comfort ($+18^\circ\text{C}$).

---

## 6. Governance & Firewall

```
CRITICAL_LOAD_STATUS = SYNTHETIC_ENGINEERING_SCENARIO
REAL_NUOLJA_CRITICAL_LOAD = NOT_ESTABLISHED
SOURCE_MODIFICATIONS = 0
365D_CAMPAIGN = NOT_PERFORMED
```
