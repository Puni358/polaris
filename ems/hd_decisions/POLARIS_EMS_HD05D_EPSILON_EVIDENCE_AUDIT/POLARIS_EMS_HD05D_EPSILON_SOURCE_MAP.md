# POLARIS EMS — HD-05D-ε Source Evidence Map

**Audit Target**: Traceability of all parameters, files, terms, and governance entries searched for extra-fuel tolerance $\epsilon$.

---

## 1. Traceability & Inspection Matrix

| Search Term / Category | Inspected File Path | Line Range | Findings / Content | Classification |
| :--- | :--- | :--- | :--- | :--- |
| **`solver_tolerance`** | [`system/config/optimizer.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/optimizer.yaml#L9) | L9 | `solver_tolerance: 1e-5` | `IMPLEMENTATION_FACT` (Numerical solver feasibility tolerance only) |
| **`deg_penalty_per_wh`** | [`system/config/battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L11) | L11 | `deg_penalty_per_wh: 0.00005` | `PROTOTYPE_ASSUMPTION` / `# Cycling penalty` |
| **`fuel_cost_per_l`** | [`system/config/diesel.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml#L7) | L7 | `fuel_cost_per_l: 2.50` | `PROTOTYPE_ASSUMPTION` (`status_label: "PROTOTYPE_ASSUMPTION"`) |
| **Marginal Fuel Rate** | [`system/config/diesel.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml#L6) | L6 | `marginal_fuel_consumption_l_per_wh: 0.00025` | `IMPLEMENTATION_FACT` ($0.25\text{ L/kWh}$) |
| **Base Fuel Rate** | [`system/config/diesel.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml#L5) | L5 | `base_fuel_consumption_l_per_h: 5.0` | `IMPLEMENTATION_FACT` ($5.0\text{ L/h}$) |
| **Seasonal Fuel Budget** | Policy Decision Sheet D08 | Decision 08 | "Seasonal fuel budget with dynamic management" | `HUMAN_SELECTED_POLICY` (Structure only; numerical volume `STATION_DATA_REQUIRED`) |
| **Stage-3 Objective Terms** | [`milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L109-L113) | L109-L113 | Composite scalar coefficients $c_i$ for fuel & degradation | `IMPLEMENTATION_FACT` (Prototype scalar MILP; no lexicographic $\epsilon$) |

---

## 2. Exhaustive Repository Term Search Results

The following terms were searched across the repository codebase and governance records. **Zero instances of operational or policy extra-fuel tolerance $\epsilon$ were found**:

- `epsilon` / `ε`: **ABSENT** (Found only in 3rd party `.venv` dates/fonts libraries and numerical code tests).
- `fuel tolerance`: **ABSENT** (Appeared only in recent HD-05D option notes).
- `fuel tolerance fraction`: **ABSENT**
- `extra fuel`: **ABSENT** as a quantitative tolerance parameter.
- `fuel margin` / `fuel slack`: **ABSENT**
- `objective bound` / `objective lock`: **ABSENT**
- `lexicographic tolerance`: **ABSENT**
- `fuel degradation tradeoff`: **ABSENT** as a quantitative value.
