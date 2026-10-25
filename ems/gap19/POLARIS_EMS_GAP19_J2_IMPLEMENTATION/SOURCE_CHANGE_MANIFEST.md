# Source Change Manifest

## 1. Summary of Changes

The implementation required updating four existing schema/optimizer files and creating one new unit test module:

| File Path | Action | Description of Modification |
| :--- | :--- | :--- |
| `system/optimization/implementations/gap19_highs_native.py` | `MODIFIED` | Updated $J_2$ formulation to governed pointwise envelope ($N=408, M=312$). |
| `system/schemas/forecast_bundle.py` | `MODIFIED` | Added optional `demand_critical` field with non-negativity and bound validation. |
| `system/schemas/station_state.py` | `MODIFIED` | Added `operating_mode`, `ebr_target_wh_override`, `terminal_target_wh_override`. |
| `system/schemas/dispatch_plan.py` | `MODIFIED` | Added `j1_objective`, `j2_objective`, `j3_objective`, `j4_objective`, `reserve_shortfall`. |
| `system/tests/test_gap19_j2_option_b.py` | `CREATED` | Added 13-test isolated unit test suite. |

---

## 2. Line-by-Line Modification Summary

### 2.1 `system/optimization/implementations/gap19_highs_native.py`
- Implemented `demand_critical` ingestion from `forecast_bundle.demand_critical.point` or `config["critical_demand_w"]` or `config["critical_demand_ratio"]`.
- Added explicit rejection (`ValueError("MISSING_GOVERNED_INPUT...")`) if `demand_critical` is absent.
- Implemented governed $E_{\text{EBR,target}}[t]$ lookahead formula over 6h window $W(t) = [t, \min(t+5, 23)]$.
- Implemented governed $E_{\text{term,target}}$ ingestion from state override, config, or `terminal_reserve_model`. Added explicit rejection if absent.
- Implemented pointwise maximum reserve envelope $E_{\text{stage2,target}}[t] = \max(E_{\text{EBR,target}}[t], \, \delta_{t, 23} E_{\text{term,target}})$.
- Updated variable index structure to $N=408$ (eliminated variable 408 $s_{\text{terminal}}$).
- Updated constraint matrix to $M=312$ (unified Stage 2 reserve envelope constraints).
- Re-aligned objective vector $c_2$ to $N=408$ size array.
- Updated `DispatchPlan` output constructor to return individual stage objectives $J_1..J_4$ and 24h `reserve_shortfall` array.

### 2.2 `system/schemas/forecast_bundle.py`
- Added `demand_critical: Optional[TimeseriesForecast] = None` to `ForecastBundle.__init__()`.
- Added validation: $P_{\text{crit}}[t] \le P_{\text{demand}}[t]$ for all $t$.
- Updated `to_dict()` and `from_dict()` for `demand_critical` round-trip serialization.

### 2.3 `system/schemas/station_state.py`
- Added `operating_mode: str = "NORMAL"`, `ebr_target_wh_override`, `terminal_target_wh_override` to `StationState.__init__()`.
- Updated `to_dict()` and `from_dict()` for round-trip serialization.

### 2.4 `system/schemas/dispatch_plan.py`
- Added `j1_objective`, `j2_objective`, `j3_objective`, `j4_objective`, `reserve_shortfall` to `DispatchPlan.__init__()`.
- Updated `to_dict()` and `from_dict()` for round-trip serialization.

---

## 3. Modification Audit Verdict

```text
MODIFIED_SOURCE_FILES = 4
CREATED_TEST_FILES = 1
UNAUTHORIZED_FILES_MODIFIED = 0
SOURCE_INTEGRITY = PASS
```
