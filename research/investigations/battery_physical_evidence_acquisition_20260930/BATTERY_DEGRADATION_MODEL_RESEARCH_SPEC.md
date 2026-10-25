# Candidate Battery Degradation Model Research Specification

```yaml
SPEC_ID: BATTERY_DEGRADATION_MODEL_RESEARCH_SPEC_V1
STATUS: RESEARCH_ONLY_CANDIDATE_MODEL
PRODUCTION_PROMOTION: NOT_AUTHORIZED
```

## 1. Objective & Scope

This specification defines a **candidate, research-only physical battery degradation model** based on Tier C peer-reviewed literature (Wang et al. 2011, Schmalstieg et al. 2014, NREL BLAST).

- It is designed solely for **offline evaluation and sensitivity modeling**.
- It is **NOT** promoted into production `milp.py` or governance.
- It separates **physical capacity loss ($Q_{\text{loss}}$)** from economic cost penalties ($/kWh).

---

## 2. Mathematical Formulation

Physical degradation is modeled as the superposition of **cycle aging** and **calendar aging**:

$$\Delta Q_{\text{loss}} = Q_{\text{cycle}} + Q_{\text{calendar}}$$

### A. Cycle Aging Component ($Q_{\text{cycle}}$)

$$Q_{\text{cycle}} = M_{\text{cycle}} \cdot (\text{EFC})^{0.55} \cdot (\text{DoD})^{1.5} \cdot \exp\left(-\frac{E_a}{R \cdot T}\right)$$

Where:
- $\text{EFC} = \frac{\int |P_{\text{batt}}(t)| dt}{2 \cdot E_{\text{nom}}}$ (Equivalent Full Cycles)
- $\text{DoD} = \text{SOC}_{\text{max}} - \text{SOC}_{\text{min}}$ (Depth of Discharge)
- $E_a = 31.7 \text{ kJ/mol}$ (Activation Energy for LFP SEI growth)
- $R = 8.314 \text{ J/(mol}\cdot\text{K)}$
- $T = \text{Battery Temperature (K)}$ (Assumed thermally controlled at $20^\circ\text{C} / 293.15\text{ K}$)

### B. Calendar Aging Component ($Q_{\text{calendar}}$)

$$Q_{\text{calendar}} = M_{\text{cal}} \cdot (t_{\text{days}})^{0.5} \cdot \exp\left(k_{\text{soc}} \cdot (\text{SOC} - 0.5)\right) \cdot \exp\left(-\frac{E_{a,\text{cal}}}{R \cdot T}\right)$$

Where:
- $t_{\text{days}} = \text{Elapsed time in days}$
- $k_{\text{soc}} = 0.85$ (SOC stress exponent)

---

## 3. Separation of Physical Loss vs. Economic Cost

```text
Physical Degradation (Capacity Fade ΔQ_loss)
        ↓  (Requires Target Stack Replacement Invoice & Polar Freight Cost)
Economic Degradation Cost ($/kWh)
        ↓  (Requires Formal Governance Authorization)
Optimizer Penalty Weight
```

Because target site replacement cost ($/kWh) and logistics invoices are **MISSING** in the workspace:

```yaml
ECONOMIC_DEGRADATION_COST:
  STATUS: NOT_IDENTIFIABLE
```

No economic dollar weight is invented or promoted into production.
