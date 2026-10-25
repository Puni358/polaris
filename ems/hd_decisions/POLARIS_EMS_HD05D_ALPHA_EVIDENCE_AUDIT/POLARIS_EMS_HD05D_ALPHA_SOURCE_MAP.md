# POLARIS EMS — HD-05D-α Source Evidence Map

**Audit Target**: Exhaustive traceability map of all repository searches for relative extra-fuel tolerance $\alpha$.

---

## 1. Traceability & Inspection Matrix

| Search Term / Category | Inspected File Path | Line Range | Findings / Content | Classification |
| :--- | :--- | :--- | :--- | :--- |
| **`alpha`** | [`system/tests/test_model_reproducibility_governance.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/tests/test_model_reproducibility_governance.py#L96) | L96 | `Ridge(alpha=1.0)` | `UNRELATED` (Machine learning Ridge regression test parameter) |
| **Qualitative Policy** | Decision Sheet HD-05B | HD-05B | "Spend additional diesel fuel to reduce unnecessary battery cycling" | `CLOSED_POLICY` (Qualitative policy approved; quantitative $\alpha$ unresolved) |
| **Fuel Budget Policy** | Policy Decision Sheet D08 | Decision 08 | "Seasonal fuel budget with dynamic management" | `HUMAN_SELECTED_POLICY` (Structure only; numerical volume `STATION_DATA_REQUIRED`) |
| **Generator Config** | [`system/config/diesel.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml#L5-L8) | L5-L8 | Idle $5\text{ L/h}$, marginal $0.25\text{ L/kWh}$, startup $\$15$ | `IMPLEMENTATION_FACT` (Technical generator performance curves) |
| **Battery Config** | [`system/config/battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L11) | L11 | `deg_penalty_per_wh: 0.00005` | `PROTOTYPE_ASSUMPTION` (`# Cycling penalty`) |
| **MILP Objective** | [`milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L107-L115) | L107-L115 | Composite scalar coefficients $c_i$ for fuel & degradation | `IMPLEMENTATION_FACT` (Prototype scalar MILP; no lexicographic $\alpha$) |

---

## 2. Exhaustive Repository Term Search Results

The following terms were searched across the repository codebase and governance records. **Zero instances of numerical relative fuel tolerance $\alpha$ were found**:

- `alpha` / `α`: **ABSENT** as an operational fuel tolerance parameter.
- `fuel percentage`: **ABSENT**
- `fuel sacrifice`: **ABSENT**
- `acceptable fuel increase`: **ABSENT**
- `fuel allowance`: **ABSENT** as a quantitative percentage.
- `extra fuel`: **ABSENT** as a quantitative percentage.
- `fuel margin` / `fuel slack`: **ABSENT**
- `degradation tolerance`: **ABSENT** as a quantitative percentage.
