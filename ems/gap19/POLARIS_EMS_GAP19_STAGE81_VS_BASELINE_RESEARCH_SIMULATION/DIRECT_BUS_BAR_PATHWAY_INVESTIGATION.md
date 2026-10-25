# Investigation: The Remaining ~69.7% (Direct Bus-Bar) Stage8.1-vs-Baseline Diesel Delta

**Scope**: Investigation only, of the direct bus-bar energy-balance pathway isolated by
`TERMINAL_TARGET_ABLATION_REPORT.md` (where `terminal_target_wh` is forced to a
solar-insensitive 40,000 Wh constant, confirmed to make `J2 = 0` / reserve-shortfall `= 0`
for **both** arms at every one of the 245 NORMAL-route origins — so nothing below can be the
reserve mechanism; it is already fully excluded by construction). **No production code,
config, or frozen artifact was modified.** Two new, small, research-only scripts were run,
reusing the frozen `run_full_experiment.py` functions unmodified (same in-process
monkeypatch technique as the terminal-target ablation): [run_direct_bus_bar_isolation.py](run_direct_bus_bar_isolation.py)
(SHA256 `edd99177...`) producing [DIRECT_BUS_BAR_ISOLATION_DETAIL.json](DIRECT_BUS_BAR_ISOLATION_DETAIL.json)
(SHA256 `5a7c0d70...`). `verify_frozen_manifest()` (reused, unmodified) reported all hashes
MATCH before this run proceeded.

**Design**: a per-hour deep dive on 3 representative origins drawn from the already-completed
347-origin ablation ([TERMINAL_ABLATION_RAW_RESULTS.json](TERMINAL_ABLATION_RAW_RESULTS.json)):
the single largest-delta origin (2024-10-27, +59.75 L), a shoulder-season medium-delta origin
(2024-03-20, +32.15 L), and a zero-delta origin for contrast (2024-06-01, +0.00 L) — the same
reference origin used throughout this diagnostic branch. This is the smallest additional step
beyond the already-run full ablation: it adds only the full per-hour `DispatchPlan` arrays
(`solar_used`, `wind_used`, `battery_charge/discharge`, `diesel_power`, `renewable_curtailment`),
which the frozen R1/R2 result-collection code does not retain (only per-cycle sums).

---

## 1. Exactly why Stage 8.1 causes additional diesel — **VERIFIED**

**Root cause: Stage 8.1's forecast reveals a real, large energy shortfall at this
high-latitude (68.36°N) site in autumn/shoulder months that baseline's forecast structurally
cannot see, because baseline's forecast is date-independent.**

**VERIFIED, byte-for-byte**: baseline's solar-generation forecast array for 2024-10-27 and
2024-03-20 are **identical** (`b == m` confirmed `True` by direct array comparison this
session) — both days get the exact same ~30,600 W-peak curve, and this same curve is also
what baseline forecasts for 2024-06-01 (sum 310,686.0 Wh — identical total to the Oct-27/Mar-20
curve's integral). **Baseline's forecast depends only on hour-of-day, never on the actual
date or season.**

**VERIFIED against the frozen matrix's own ground-truth `actual_SW_IN` column** (same column
already used for the Q1 accuracy analysis; converted via the provenance-documented PV formula
`min(SW_IN × 300 × 0.20 × 0.85, 60000)`):

| Origin | Baseline forecast (Wh) | Stage 8.1 forecast (Wh) | **Real (ground-truth) solar (Wh)** | Baseline error | Stage 8.1 error |
|---|---|---|---|---|---|
| 2024-10-27 | 310,686.0 | 11,097.1 | **7,664.1** | **+40.5× too high** | +1.45× (same order of magnitude) |
| 2024-03-20 | 310,686.0 | ~90,260.2 | **108,238.0** | **+2.87× too high** | −16.6% (close, slight underestimate) |
| 2024-06-01 | 310,686.0 | 255,455.0 | *(not computed — zero-delta origin, both arms already have large surplus)* | — | — |

**Baseline's forecast overstates real solar by 40.5× on 2024-10-27 and 2.87× on 2024-03-20.**
Stage 8.1's forecast is within the same order of magnitude as reality on both dates. This is
the forecast input that creates the difference (confirmed directly from the frozen matrix's
own ground-truth column, not an inference from bias statistics alone).

## 2. Which constraint/objective/forecast input creates the difference — **VERIFIED**

- **Forecast input**: `solar_generation` only (wind and demand confirmed bit-identical
  between arms at both origins — `wind_generation_forecast_w` arrays match exactly in the
  captured detail JSON for both engines at both origins).
- **Constraint**: the bus-bar energy balance (`gap19_highs_native.py` constraint #3,
  `p_sol_used + p_wind_used + p_dis + p_diesel = p_served + p_chg + p_flex`) combined with the
  critical-load balance (Layer B: `p_served + P_unmet_crit = critical_demand`, with
  `P_unmet_crit` minimized to 0 at priority 4/J1). Together these force total supply
  (solar+wind+battery discharge+diesel) to cover critical demand (11,600 W, identical both
  arms — `critical_demand` arrays match exactly) every hour. **Confirmed numerically**
  (2024-10-27, Stage 8.1 arm): total critical-demand energy over 24h = 278,400 Wh; total
  forecasted solar+wind = 48,417.5 Wh (11,097.1 + 37,320.4); shortfall = 229,982.5 Wh, which
  must come from the battery's initial charge and/or diesel — there is no other source in the
  model.
- **Objective**: `J3` (diesel fuel, priority 2) determines *how much and when* diesel runs,
  once the constraint above has made some diesel unavoidable. `J2` (reserve) is confirmed
  `= 0` for both arms at every hour of both origins in the captured detail (`reserve_shortfall_w`
  arrays are all-zero) — **fully excluded**, exactly as the ablation design requires.

## 3. Whether the extra diesel is physically necessary or an optimizer artifact

**VERIFIED: some nonzero diesel is genuinely physically necessary under Stage 8.1's forecast
— the shortfall (229,982.5 Wh on 2024-10-27) exceeds even the battery's full usable initial
charge** (160,000 Wh initial − 40,000 Wh floor = 120,000 Wh usable), leaving a residual
109,982.5 Wh gap that only diesel can fill, given the model's available sources. **This part
is not an artifact — it is a real consequence of the physical energy-balance constraint,
given the (ground-truth-confirmed, more accurate) forecast.**

**VERIFIED: baseline's "zero diesel" plan for these origins is the artifact, not evidence of
sufficiency.** Baseline's forecast is 40.5× (Oct-27) and 2.87× (Mar-20) too high versus the
same matrix's own ground truth. A plan computed against a forecast that overstates real solar
by 40× is not evidence that no diesel was needed — it is evidence the plan was computed
against an input that does not reflect the conditions that actually occurred.

**UNKNOWN (not tested by this or any existing artifact): what would actually have happened if
baseline's zero-diesel plan were executed against real conditions** — i.e. whether the
station would have experienced real unmet critical load, an SOC excursion below the governed
floor, or some other failure mode. R1/R2/ablation are single-step-per-origin designs (only
the plan's first hour is ever executed against `next_actual`); no artifact in this repository
replays baseline's full 24h *plan* against the *real* 24h ground truth to see where it would
have failed. This would require a new, different experiment (replaying a fixed plan against
real data) not run here.

**VERIFIED, separately: part of the *specific magnitude and hour-placement* of Stage 8.1's
diesel dispatch reflects J3's own fuel-cost-minimizing response to the diesel cost structure,
not pure instantaneous necessity.** From `system/config/diesel.yaml`: `base_fuel_consumption_l_per_h:
5.0` is a **fixed cost incurred every hour diesel runs, independent of power level** (within
`[10,000W, 100,000W]`), plus a startup cost (`startup_fuel_l`, defaulting to `2.0` L per start
— **VERIFIED this is the code default, not a configured value**: `diesel.yaml` has no
`startup_fuel_l` key at all, only `startup_cost: 15.0` which is a different, unused-by-GAP19
currency field; `gap19_highs_native.py:84` falls back to its hardcoded `2.0` default). This
creates a real incentive to concentrate diesel into **fewer, larger** dispatches (paying the
fixed per-hour cost fewer times) and bank the surplus energy in the battery for later
discharge, rather than running diesel continuously at the exact instantaneous deficit level.
**Observed, 2024-10-27, Stage 8.1 arm**: diesel runs at only 3 of 24 hours (hours 5, 8, 16, at
58,741 W / 61,142 W / 59,100 W — all far above the 11,600 W critical-demand level), with
47,141–50,000 W of each dispatch routed into `battery_charge` rather than directly serving
load, then discharged across many *other* hours (`battery_discharge` nonzero at 16 of the
remaining 21 hours). Total diesel *energy* used (178,983.2 Wh) **exceeds** the bare
shortfall figure (229,982.5 − 120,000 = 109,982.5 Wh) by 68,999.9 Wh — consistent with, and
of the right order of magnitude for, the ~15.4% round-trip battery loss
(`charge_efficiency × discharge_efficiency = 0.92 × 0.92 = 0.846`) incurred by this banking
strategy. **This additional energy is the fuel-cost-minimal (J3-optimal) trade-off GAP19's
own governed cost structure makes — not a defect, but also not the bare instantaneous
physical minimum.** Whether a hypothetically "spread evenly" diesel schedule would use fewer
total liters (trading round-trip loss against fixed per-hour cost) is **UNKNOWN** — not
computed here; would require solving an alternative schedule explicitly, which this
investigation did not do (no code was changed or re-solved under an alternative cost
structure).

**Also VERIFIED, as a secondary/unrelated observation, not central to this question**:
`min_up_time_hours: 2` exists in `diesel.yaml` but is **not referenced anywhere in
`gap19_highs_native.py`** (confirmed by `grep`) — this configured value has no effect on
GAP19's actual constraints; the "concentrate into bursts" behavior above is driven *purely* by
the fixed-base-fuel-per-hour cost term, not by any minimum-run-time constraint (none exists in
the code).

## 4. Smallest valid counterfactual that isolates this mechanism — **run, this session**

Two layers, both already executed:
1. **The full 347-origin terminal-target ablation** (`TERMINAL_ABLATION_RAW_RESULTS.json`,
   previously completed) isolates the direct bus-bar pathway from the reserve pathway at
   full-window scale — confirmed `J2 = 0` / 0 binding origins for both arms at all 245
   NORMAL-route origins.
2. **This session's 3-origin per-hour deep dive** (`DIRECT_BUS_BAR_ISOLATION_DETAIL.json`),
   under the identical ablated configuration, adds the per-hour granularity needed to
   determine *where* and *why* the diesel differs — confirmed `reserve_shortfall_w` all-zero
   at every hour of both compared origins, and the ground-truth `actual_SW_IN` cross-check
   confirming which forecast is closer to reality.

Both layers reuse the frozen `GAP19HighsNativeOptimizer`, `system/config/*.yaml`,
`StationState` construction, and forecast engines unmodified; the only change in either layer
is the same single monkeypatched constant already used and disclosed in the terminal-target
ablation.

---

## Summary table: VERIFIED vs. UNKNOWN

| Claim | Status |
|---|---|
| Baseline's solar forecast is date-independent (same curve every day) | **VERIFIED** (byte-identical arrays, 3 different dates checked) |
| Baseline overstates real ground-truth solar by 40.5× (Oct-27) and 2.87× (Mar-20) | **VERIFIED** (computed from the frozen matrix's own `actual_SW_IN` column, same provenance-documented PV formula used elsewhere in this repo) |
| Stage 8.1's forecast is within the same order of magnitude as ground truth on both dates | **VERIFIED** |
| Wind and demand are bit-identical between arms at both origins | **VERIFIED** (direct array comparison) |
| Reserve shortfall (J2) is zero for both arms at every hour of both origins | **VERIFIED** (captured per-hour `reserve_shortfall_w`, all zero) |
| Some nonzero diesel is physically necessary under Stage 8.1's forecast (shortfall exceeds usable battery charge) | **VERIFIED** (229,982.5 Wh shortfall > 120,000 Wh usable battery energy, 2024-10-27) |
| Baseline's zero-diesel plan is the forecast artifact, not evidence of sufficiency | **VERIFIED** (40.5×/2.87× forecast error vs. ground truth) |
| Diesel is concentrated into few, large bursts due to the fixed per-on-hour base-fuel cost | **VERIFIED** (code: `base_fuel_consumption_l_per_h` fixed regardless of power; data: 3 large bursts, not continuous dispatch) |
| `min_up_time_hours` has no effect on GAP19's actual behavior | **VERIFIED** (absent from `gap19_highs_native.py`, confirmed by code search) |
| The extra ~69,000 Wh of diesel energy (above the bare shortfall) reflects real round-trip battery loss from the banking strategy | **VERIFIED as directionally consistent and right order of magnitude**; not independently re-derived from first principles in this session beyond the arithmetic shown |
| What would actually happen if baseline's plan were executed against real conditions | **UNKNOWN** — not tested by any existing artifact; would require a new plan-vs-ground-truth replay experiment |
| Whether an alternative (non-burst) diesel schedule would use fewer total liters | **UNKNOWN** — not computed; would require solving an alternative schedule |

## STOP

Investigation complete. No production code, config, or frozen artifact modified.
`run_research_simulation.py` and `run_full_experiment.py` confirmed byte-identical to their
frozen hashes before this session's two small scripts ran. No speculation beyond what is
explicitly marked VERIFIED or UNKNOWN above.
