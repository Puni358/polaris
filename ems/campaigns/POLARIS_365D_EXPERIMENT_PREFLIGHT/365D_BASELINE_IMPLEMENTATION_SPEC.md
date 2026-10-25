# 365D SIMPLE DIESEL-ONLY BASELINE IMPLEMENTATION SPECIFICATION

## Governed Baseline Definition
- **Classification**: `SIMPLE_DIESEL_ONLY_REFERENCE`
- **Purpose**: Establishes the exact baseline diesel fuel consumption required to supply total microgrid electrical demand over the full 2024 calendar trajectory without renewable contribution or predictive optimization.
- **Implementation File**: [`system/orchestration/worker.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/orchestration/worker.py)

## Execution Logic & Boundary Verification
1. **Independent Execution Path**: Cell A (`cell_a`) executes a standalone reference path inside `CampaignWorker.execute()`. It does NOT instantiate or invoke `LocalBaselineForecastEngine`, `EMSControlRouter`, `OptionDFallbackSolver`, `LocalRuleBasedEnergyOptimizer`, or `GAP19HighsNativeOptimizer`.
2. **Direct Demand Coverage**:
   - At each hourly timestep $k$: $P_{\text{diesel}}(k) = P_{\text{demand\_actual}}(k)$.
   - Battery charging and discharging decisions are set to zero ($P_{\text{chg}} = 0.0$, $P_{\text{dis}} = 0.0$).
3. **Governed Physical Fuel Consumption Model**:
   - $\text{Step Fuel } [L] = (\text{ON\_hours} \times 5.0\text{ L/h}) + (P_{\text{diesel}} \times 0.00025\text{ L/Wh})$.
   - Cumulative fuel is tracked monotonically without fuel tank artificial resupply depletion or clipping.
4. **Information Parity**:
   - Same underlying demand trajectory (`next_actual["actual_demand"]`).
   - Same physical asset parameters and 8,784 hourly timestamps.
   - Zero predictive forecast access or optimization algorithms.
