# Critical-Aware EBR: Failure Review (Six Origins)

**Scope:** explains why the critical-aware EBR candidate (Arm C) loses critical reliability. Uses only existing outputs: `critical_aware_ebr/origin_*.json` (hourly logs for Arm C and frozen Arm B) and `hourly_trace/origin_*.json` (governed EBR and realized solar). No dispatch solves were run. No margin is selected. No code is changed.
**Derived series:** `critical_aware_ebr/failure_review_series.json`.

**Definitions used:**
- Renewable supply, realized: `R = served + charge + curtailment − discharge − diesel`, from the executor's exact busbar balance. This gives solar + wind per hour.
- Wind realized: `R − realized solar`. Realized solar power: `irradiance × 51 W` (the D3 map).
- Wind forecast: `forecast renewable − forecast solar`.
- Reserve released: `governed EBR[t] − EBR_ca[t]`, both at the step's hour-0 window.

---

## FACT

**F1. Where critical unmet rises.** Hours where Arm C has more critical unmet than frozen B: origin 77 step 22; origin 56 steps 6, 7; origin 66 steps 3, 4, 5, 6, 7, 22; origin 30 steps 21, 22. That is 11 hours, all at night, dawn, or evening (about 20:00–07:00 UTC). The positive increases sum to **19,467 Wh**. Decreases elsewhere sum to **−11,833 Wh**, so the net is **+7,635 Wh**.

**F2. Reserve released at those hours.** At every failing hour, Arm C's reserve was far below the governed value (115,652 Wh). Released amounts: **66 to 116 kWh per hour**. At origin 66 steps 3 and 4, Arm C's reserve is **0 Wh**, so the release is the full 115.7 kWh.

**F3. Diesel committed at those hours.** Arm C's realized diesel is **0 at all 11 failing hours**. Frozen B had diesel at several of the same hours (e.g., origin 66 steps 5–7).

**F4. Exact identity at two hours.** At origin 66 steps 3 and 4, critical unmet equals `11,600 − realized renewable`, to the watt: 11,600 − 11,292 = 308 Wh (step 3) and 11,600 − 8,095 = 3,505 Wh (step 4). Neither hour had battery discharge or diesel to cover the gap.

**F5. Wind is the dominant forecast term at failing hours.** The subtracted forecast renewable is mostly wind. At origin 66 step 3, the forecast is 807 W solar and 12,000 W wind. Across the 11 failing hours, forecast wind ranges 2,500–12,000 W.

**F6. Wind over-forecast at every failing hour.** Wind error (realized − forecast):

| Origin, step | Forecast wind (W) | Realized wind (W) | Error (W) |
|---|---:|---:|---:|
| 77, 22 | 2,670 | 2,000 | −670 |
| 56, 6 | 7,000 | 2,000 | **−5,000** |
| 56, 7 | 4,500 | 170 | −4,330 |
| 66, 3 | 12,000 | 8,830 | −3,170 |
| 66, 4 | 11,330 | 7,000 | −4,330 |
| 66, 5 | 9,500 | 4,500 | **−5,000** |
| 66, 6 | 7,000 | 2,000 | **−5,000** |
| 66, 7 | 4,500 | 170 | −4,330 |
| 66, 22 | 2,670 | 2,000 | −670 |
| 30, 21 | 2,500 | 170 | −2,330 |
| 30, 22 | 2,670 | 2,000 | −670 |

**F7. Solar errors at failing hours are small and mixed in sign.** Solar error (realized − forecast) at failing hours ranges from −592 W to +3,368 W. In the largest case (origin 56 step 7) solar was under-forecast, which helped Arm C rather than hurting it.

**F8. Per-hour critical unmet vs realized renewable.** Critical unmet at failing hours ranges from 219 Wh to 4,723 Wh. The largest single-hour value across the six origins is **4,723 Wh** (origin 66, step 6).

**F9. Wind inputs are synthetic in this campaign.** The campaign's realized wind is `4,500 + 5,000·sin(hπ/6)` (`run_diesel_reduction_campaign.py` lines 113–114). The baseline wind forecast is persistence plus the same sinusoid (`baseline.py` lines 75, 98–99), with a lower bound of `0.85 × point` and an upper bound of `1.15 × point`.

---

## INFERENCE

**I1. Primary failure mode is wind magnitude error, not solar timing.** Every failing hour has a wind over-forecast of 0.7–5.0 kW. Solar errors at those hours are small and of both signs. None of the 11 failing hours is in a daytime solar-timing window. So magnitude error in wind is the primary driver, and solar timing is not implicated in these six origins.

**I2. The removal of the backstop converts a small forecast error into unmet load.** When forecast renewables cover the 11.6 kW critical load, Arm C releases the reserve and commits no diesel. A realized renewable shortfall at that hour then goes straight to critical unmet. Frozen B's reserve and diesel would have covered it. The exact identity in F4 shows this.

**I3. The reserve-release logic is the amplifier, but its inputs set the size.** The release is large (66–116 kWh per hour) because forecast wind alone exceeds the 11.6 kW critical load at several hours. Under the design's formula, the subtracted term is the full forecast wind. Any wind over-forecast of the observed size therefore releases almost all of the reserve.

**I4. A safety mechanism need not restore the full EBR.** The largest single-hour failure in the six origins is 4,723 Wh. The full reserve is 115,652 Wh. A backstop covering the uncovered critical energy at each hour, under the observed size of wind error, would have prevented these six failures. This is an inference from six origins. It does not select a margin.

**I5. The existing wind lower bound does not prevent the failure.** The baseline already carries a wind lower bound at `0.85 × point`. At origin 66 step 4 this gives `0.85 × 11,330 + 1,686 = 11,316.5 W`. The uncovered critical energy is then `11,600 − 11,316.5 = 283.5 Wh`, so the reserve is still almost fully released. The realized shortfall was 3,505 Wh. Using this bound alone would not restore the backstop.

---

## UNKNOWN

**U1. Whether the wind error is physical.** The campaign's wind is synthetic (F9). The size and sign of the wind error at failing hours reflect the benchmark construction, not real wind behaviour. Real-wind error distributions are not tested here.

**U2. Wind error across the 123 origins.** Only six origins are available. The frequency and magnitude of wind over-forecast across the campaign are not measured.

**U3. Whether solar timing matters in daytime.** Failing hours are all low-sun. Solar timing errors at critical daytime hours are not covered by these six origins.

**U4. Planner convention.** The critical convention used here is still the realized-demand one. The planner-convention question is open, as noted in the experiment report.

**U5. Whether a backstop changes other mechanisms.** A partial reserve or diesel backstop would also change fuel, curtailment, and SOC. The effect was not computed.

---

## Summary

- The failure is **primarily magnitude error in the wind forecast**, at night and low-sun hours, where forecast wind alone exceeds the critical load.
- **Timing** is not the primary failure mode in these six origins. Solar errors at failing hours are small and mixed.
- The **mechanism** is that Arm C releases the reserve and commits no diesel when forecast renewables cover the load. A wind shortfall then goes directly to critical unmet (exact identity at origin 66, steps 3–4).
- The **failure is small** in aggregate: +7.6 kWh net, from 11 hours.
- A **safety mechanism** that does not depend on the wind forecast being right would need to cover the uncovered critical energy at each hour. The observed scale is about 5 kWh per hour, far below the full 115.7 kWh reserve. The existing 0.85× wind bound does not cover it.

---

PRIMARY FAILURE MODE: Wind-forecast magnitude over-prediction at night and low-sun hours (over-forecast of 0.7–5.0 kW at all 11 failing hours). With the reserve released and no diesel committed, the realized shortfall goes to critical unmet. Solar timing is not the primary mode in these six origins.

MINIMUM SAFETY MECHANISM NEEDED: A critical-load backstop that does not rely on the forecast wind being correct. It must cover the uncovered critical energy at each hour under the observed size of wind error, which is roughly 5 kWh per hour across these six origins. The existing 0.85× wind lower bound would not provide it. No margin is selected here.

NEXT SINGLE EXPERIMENT: Analysis-only, on the existing six-origin outputs: measure the wind forecast error distribution (realized minus forecast, hourly, for each origin and arm), split by the solar-cover condition, so the size of the uncovered critical energy at failing hours can be compared with any candidate backstop. No dispatch, no margin choice, no new solves.
