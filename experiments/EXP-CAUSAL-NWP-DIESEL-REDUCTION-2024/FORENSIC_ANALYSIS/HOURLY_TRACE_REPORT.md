# Hourly Trace Report: Does B's Forecast Drive GAP19 Diesel Through Reserve/Terminal Constraints?

**Experiment:** `EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024` (frozen, authoritative; not rerun or modified)
**Artifacts:** `FORENSIC_ANALYSIS/trace_hourly.py`, `FORENSIC_ANALYSIS/hourly_trace/origin_{56,77,66,23,8,30}.json`, `hourly_trace/summary.json`, `FORENSIC_ANALYSIS/forecast_only_all_origins.csv`
**Method:** Research-only observation wrapper around the existing campaign functions and `AdaptedClosedLoopRunner`. No dispatch rule, config, or frozen file changed. Realized solar is the campaign's own `actual_SW_IN`. Realized wind and demand use the campaign's formulas, copied verbatim.
**Date:** 2026-10-04

---

## 0. Blocker Check and Reproduction Gate

No blocker. The realized inputs are in the 2024 weather CSV (`actual_SW_IN`), so nothing had to be reconstructed.

Reproduction gate: the trace reproduced the frozen per-arm diesel fuel for all six origins to four decimals (for example origin 56: A 41.5323 / 41.5323, B 93.7559 / 93.7559). The trace is faithful to the frozen path. Its records are observation only.

**Subset (chosen from frozen data, not cherry-picked by outcome):** worst B-vs-A fuel gaps at origins 77 (+52.5 L), 56 (+52.2 L), 66 (+43.2 L), 23 (+40.0 L), plus two typical origins with near-zero gap, 8 (−0.06 L) and 30 (−0.37 L). Six of 123 origins, so this is not a representative sample of the campaign.

---

## 1. First Divergence: Same State, Different Decision

At every traced origin, the **first reoptimization (step 0) is the first point where A and B make different decisions**, and at that point both arms are in the **same physical state**: same SOC (50%, the frozen initial state), same fuel (100 L), same diesel status. The only difference is the 24-hour solar forecast the planner receives.

Origin 56 (2024-06-25), step 0, same state:

| Quantity | Arm A | Arm B |
|---|---:|---:|
| Forecast solar, 24-h sum (W/m²·h) | 6,091.9 | **21.1** |
| Forecast solar at t+1 (W/m²) | 0.0 | 0.0 |
| Realized solar, 24-h sum (W/m²·h) | 2,530 | 2,530 |
| Planned diesel t0 (kW) | 37.4 | **44.5** |
| Planned charge t0 (kW) | 32.8 | **39.9** |
| Planned end-of-horizon SOC E_next[23] (Wh) | — | **140,000** (target) |
| Reserve/terminal margin at t0 (Wh) | +7.8 (reserve) | +7.8 (reserve) |
| **Terminal margin at t23 (Wh)** | **+340** (slack) | **0.0** (tight) |
| GAP19 J2 shortfall | 0 | 0 |
| GAP19 J3 fuel objective | 16.4 | **89.5** |
| GAP19 J4 curtailment objective | 110,145 | 0 |

The fact that matters: in A, the forecast surplus lets the planner meet the horizon-end target with slack and plan 110 kWh of curtailment in its own model. In B, the forecast is nearly zero, so the planner meets the same target only by charging from diesel. B's planned curtailment objective is zero because its plan has no solar surplus at all.

---

## 2. Which Constraint Causes the Difference

Recorded margins over all reoptimizations (margin below 100 Wh counted as tight):

| Origin | Reserve tight, steps A / B | Terminal tight, steps A / B | Terminal margin at step 0, A / B (Wh) | B forecast 24-h sum | Realized 24-h sum | Frozen B−A fuel (L) |
|---|---|---|---|---:|---:|---:|
| 56 | 15 / 17 | 5 / **12** | 340 / **0** | 21 | 2,530 | +52.2 |
| 77 | 17 / 17 | 6 / **10** | 340 / **0** | 1,002 | 5,015 | +52.5 |
| 66 | 16 / 13 | 6 / **10** | 340 / **0** | 2,981 | 3,130 | +43.2 |
| 23 | 16 / 17 | 5 / **14** | 340 / **0** | 1,069 | 5,232 | +40.0 |
| 8 | 15 / 18 | 5 / **20** | 340 / **0** | 3,581 | 6,100 | −0.1 |
| 30 | 16 / 14 | 5 / 3 | 340 / 1,160 | 5,558 | 5,562 | −0.4 |

Findings:

1. **The reserve constraint is tight in both arms** (13–18 of 24 steps), so the 6-hour EBR reserve is active structurally and is not the B-specific difference. This matches the frozen min SOC of 57.83%.
2. **The terminal target (140 kWh at t+24, J2 priority above fuel J3) is the B-specific binding term.** In five of six traced origins, B's terminal margin is 0 at step 0 while A's is 340 Wh of slack. In origin 56, B's planned E_next[23] is exactly 140,000 Wh, meaning the planner charges the battery to the terminal target from diesel.
3. **J2 shortfall is zero in every step of both arms**, and so is the realized terminal shortfall. The target is met exactly, not violated. The binding is in the feasibility set, not through slack.
4. **Origin 30 is the control.** B's forecast was accurate (5,558 vs realized 5,562), its terminal margin is +1,160 Wh (slack), and its fuel is near A's (−0.37 L).

---

## 3. How the Terminal Binding Turns Into Curtailment

The hourly detail for origin 56 (B | A) shows the sequence:

| Hours (UTC) | Forecast solar (W/m²) | Realized solar (W/m²) | B plan | B realized outcome |
|---|---|---|---|---|
| 00–07 | 0 | 4–67 | Diesel charge to 27–56 kW in several blocks | SOC rises to 92% by 07:00 |
| 08–14 | 0 | 80–542 (peak 11:00) | **Battery discharge 4.6–9.1 kW** (solar-free plan) | Surplus when the sun arrives, **same-hour discharge blocks charging → curtailed** (146 Wh at 08:00, 27.3 kWh at 11:00) |
| 15 | 0 | 155 | Discharge 2.5 kW | 5.7 kWh curtailed (same-hour discharge) |
| 19–23 | 0 | 6–71 | Diesel charge 26–40 kW | Diesel charges battery at night for the terminal target |

Summed over the day: B curtailed 88.0 kWh vs A 15.3 kWh. Curtailment cause over 24 steps: B has 8 same-hour-discharge steps, A has 1. A's forecast surplus meant it charged the battery at midday instead of discharging, so it had no same-hour discharge conflict.

**The executor rule is the mechanism of the curtailment, not the planner's economics.** When a discharge is realized in an hour with surplus solar, the executor curtails the entire surplus instead of reducing the discharge (`research_realization_executor.py` lines 210–223). The planner's discharge is fixed at plan, so the realized sun is wasted. This is a realization-layer artifact that converts the forecast error into curtailment.

Across all six traced origins, the same-hour-discharge cause accounts for almost all B curtailment: B 4–8 steps per origin, A 0–5 steps, with `charge_cap` and `other` in a few steps only.

---

## 4. Forecast Error Across All 123 Origins (forecast-only, no dispatch solves)

Forecast totals were computed with the same `CausalNwpPhysicsForecastEngine` (forecast only, no solver). A is the fixed clear-sky curve, identical every origin (6,092 W/m²·h).

| | Mean 24-h total (W/m²·h) | Notes |
|---|---:|---|
| Realized (SITES `actual_SW_IN`) | 3,981 | range 436–6,822 |
| Arm A forecast | 6,092 | constant, over-forecasts on average by +2,111 |
| Arm B forecast | 2,278 | under-forecasts on **104 of 123** origins; cloud ≥95% days: mean error −2,464 |

Linkage to the frozen per-origin results:
- Corr(B forecast error, B−A fuel) = **−0.28** (more B under-forecast, more B fuel).
- Corr(B forecast error, B−A curtailment) = **−0.57**.
- B under-forecast origins: mean B−A fuel +10.9 L. Accurate or over-forecast origins: mean −0.65 L.
- Cloud ≥95% origins (17): mean B−A fuel +19.9 L vs +7.4 L elsewhere.

Forecast error explains the direction and much of the size of the penalty, but not all of it. Origin 66 has an accurate day total (B error −149 W/m²·h) yet a +43 L penalty. Its hourly forecast shifts solar peak to 09 UTC while realized peaks at 12–13 UTC, so the penalty there is a timing/shape error, not a volume error.

---

## 5. Evaluation Against the Four Hypotheses

| Hypothesis | Verdict | Evidence |
|---|---|---|
| 1. Forecast-driven reserve/diesel commitment | **Partly.** Diesel is committed because of the forecast, but through the terminal target, not the EBR reserve | EBR reserve is tight in both arms (structural). Diesel charges are planned in B only where the 24-h forecast is solar-poor. |
| 2. Terminal-target effect | **Primary.** The B-specific binding term | Terminal margin 0 in 5 of 6 B origins vs +340 Wh slack in A; B's E_next[23] = 140,000 Wh exactly in origin 56. J2 has priority above fuel, so diesel is bought to meet it. |
| 3. Ordinary forecast-error effect | **Trigger.** Under-forecasting cloud-saturated and cloud-shifted days | Forecast-only: 104/123 origins under-forecast; errB vs fuel r = −0.28, vs curtailment r = −0.57. Origin 66 shows a timing error. |
| 4. Controller artifact | **Amplifier.** The realization layer converts the surplus into curtailment | Same-hour discharge blocks charging, so surplus is curtailed rather than absorbed (executor lines 210–223). The planner's plan is also unaware of this realization rule. |

**Combined verdict:** the evidence supports a combination. Forecast error (under-forecasting solar on cloud-saturated and timing-shifted days) makes the frozen horizon-end terminal target (J2 priority above fuel) binding in B and forces diesel charging. The realization rule then curtails the surplus when the sun arrives. The terminal target is the mechanism that links the forecast to diesel; the executor rule is what makes that diesel wasted.

**Not supported:** a pure reserve-driven effect (the reserve is tight in both arms). A pure ordinary forecast-error effect without the terminal link (origin 66 has an accurate day total with a large penalty, and origin 8 has a large under-forecast with a zero fuel gap).

---

## 6. Limits

1. **Sample:** six traced origins are selected for large gaps (plus two controls), not a representative sample. The forecast-only correlations cover all 123 origins but not the dispatch outcome.
2. **Causation is inferred, not tested.** I recorded margins and objective values; I did not run a counterfactual. The chain "terminal target → diesel charge → curtailment" is supported by recorded values, not isolated by a solve with the term removed. Removing or altering the term would change the dispatch rule, so I did not do it here.
3. **Origin 8 is an exception:** B's terminal is tight at step 0 and under-forecast by 2,519 W/m²·h, yet fuel is tied with A. The terminal link alone does not determine the fuel penalty; the size of the solar shortfall in the 24-h window matters too.
4. **Margins are measured from rounded plan SOC** (2-decimal percent, about ±20 Wh). The "0" margins mean |margin| under about 20 Wh.
5. **Startup fuel is not charged at realization** (noted earlier). This does not change the terminal or curtailment mechanism, but it biases the planner against starts.

---

## 7. Summary

- The first divergence is at **step 0 of each origin**, in the same physical state. The difference comes from the 24-hour solar forecast.
- The **terminal target** (140 kWh at t+24, J2 above fuel) is the B-specific binding term. It is tight at step 0 in five of six B origins and slack in A.
- The forecast causing this is **under-forecast of cloud-saturated and timing-shifted solar**, which affects 104 of 123 origins.
- Diesel is then **charged into the battery** to meet the terminal target. The **realization rule curtails the surplus** when the sun arrives, because a same-hour discharge blocks charging.

---

VERDICT: Combination. Forecast-driven terminal-target effect as the primary mechanism, triggered by ordinary forecast error (under-forecast of cloud-saturated and timing-shifted solar) and converted into curtailment by a realization-layer rule. Not a pure reserve effect (the reserve is tight in both arms), and not a pure controller artifact.

PRIMARY MECHANISM: Arm B's solar under-forecast makes the frozen horizon-end terminal target (140 kWh at t+24, J2 priority above fuel J3) binding at step 0 in 5 of 6 traced origins, where A has 340 Wh of slack. GAP19 buys diesel and charges the battery to meet it. When the sun then arrives, the planned discharge blocks charging, so the surplus is curtailed (B 4–8 same-hour-discharge steps per origin vs A 0–5).

CONFIDENCE: Moderate. The reproduction is exact and the recorded margins and objective values are consistent across six origins. Limits: six selected origins, no counterfactual solve, and origin 8 shows a large under-forecast with a zero fuel gap, so the terminal link does not fully determine the fuel penalty.

NEXT SINGLE EXPERIMENT: Research-only diagnostic counterfactual on the same six origins, Arm B only, with the horizon-end terminal term removed from the harness (not a candidate policy and not a production change). If the diesel charging and same-hour curtailment disappear, the terminal target is confirmed as the causal link; if they remain, the cause is the forecast shape and the realization rule.
