# Wind Forecast Error Analysis: Six Origins

**Scope:** existing six-origin hourly logs only. No new dispatch solves, no code or config changes. No margin chosen, no controller proposed.
**Sources:** `critical_aware_ebr/all_results.json` (hourly logs, arms A = frozen B and C = critical-aware), `hourly_trace/origin_*.json` (realized solar), and the derived table `wind_error_analysis/rows.json`.
**Error definition:** `wind error = realized wind − forecast wind` (W). Negative means the forecast over-predicted wind.
**Realized wind:** `served + charge + curtailment − discharge − diesel − realized solar`, from the executor's busbar balance.

---

## 0. Consistency Checks

- **Realized wind matches the campaign formula** `max(0, 4500 + 5000·sin(hπ/6))` in all 144 hours. The check is `h = step + 1` (`run_diesel_reduction_campaign.py` lines 113–114). Mismatches: 0.
- **Realized wind is identical across Arm A and Arm C** in all 144 hours. Mismatches: 0.
- **Forecast wind is identical across Arm A and Arm C** in all 144 hours. Mismatches: 0.

The arms therefore share the same wind inputs, and the wind error is a property of the benchmark rather than of dispatch.

---

## 1. Error Distribution (144 hours = 6 origins × 24 steps)

| Statistic (W) | Value |
|---|---:|
| Mean | **−2,500** |
| Median | **−2,500** |
| 5th percentile | −5,000 |
| 95th percentile | 0 |
| Worst (most negative) | **−5,000** |
| Best (most positive) | 0 |
| Standard deviation | 1,811 |
| Hours with over-forecast (error < 0) | **133 / 144 (92%)** |

Arm C gives identical numbers, consistent with §0.

**Important: the 144 hours are not 144 independent samples.** The error takes exactly one value per step index, and that value is the same in all six origins:

| Step | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Error (W) | 0 | −670 | −1,830 | −3,170 | −4,330 | −5,000 | −5,000 | −4,330 | −2,670 | −2,330 | −670 | 0 |

| Step | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Error (W) | 0 | −670 | −1,830 | −3,170 | −4,330 | −5,000 | −5,000 | −4,330 | −2,670 | −2,330 | −670 | 0 |

The profile repeats every 12 steps. The error depends only on the position within the origin's 24-step cycle, not on the weather. It is produced by the persistence wind forecast (last observed wind plus a sinusoid) compared against a synthetic realized wind with a different phase. The six origins give one deterministic profile, repeated six times.

---

## 2. Failing-Hour Errors

Critical-aware failing hours (11, as in the failure review):

| Origin, step | Wind error (W) | Forecast wind (W) | Forecast solar (W) | Uncovered by forecast solar (W) | Uncovered by forecast solar + wind (W) | Realized critical unmet, C (W) |
|---|---:|---:|---:|---:|---:|---:|
| 77, 22 | −670 | 2,670 | 2 | 11,598 | 8,928 | 327 |
| 56, 6 | −5,000 | 7,000 | 0 | 11,600 | 4,600 | 2,713 |
| 56, 7 | −4,330 | 4,500 | 0 | 11,600 | 7,100 | 962 |
| 66, 3 | −3,170 | 12,000 | 807 | 10,793 | **0** | 308 |
| 66, 4 | −4,330 | 11,330 | 1,686 | 9,914 | **0** | 3,505 |
| 66, 5 | −5,000 | 9,500 | 488 | 11,112 | 1,612 | 1,643 |
| 66, 6 | −5,000 | 7,000 | 854 | 10,746 | 3,746 | 4,723 |
| 66, 7 | −4,330 | 4,500 | 2,610 | 8,990 | 4,490 | 2,906 |
| 66, 22 | −670 | 2,670 | 58 | 11,542 | 8,872 | 261 |
| 30, 21 | −2,330 | 2,500 | 490 | 11,110 | 8,610 | 1,899 |
| 30, 22 | −670 | 2,670 | 82 | 11,518 | 8,848 | 219 |

At the two hours where the forecast renewables fully covered the critical load (origin 66, steps 3 and 4), the wind error alone is the entire failure: the forecast wind of 12,000 W and 11,330 W was over-predicted by 3,170 W and 4,330 W.

---

## 3. Uncovered Critical Energy

Uncovered energy per hour = `max(0, critical − forecast renewable)`, where critical is 11,600 W in most hours.

| Measure (144 hours, Arm C forecasts) | Mean (Wh/h) | Median | 95th pct | Max | Hours > 0 |
|---|---:|---:|---:|---:|---:|
| Uncovered by forecast **solar** only | 8,277 | 10,802 | 11,600 | 11,600 | 122 / 144 |
| Uncovered by forecast **solar + wind** | 3,066 | 1,701 | 8,930 | 9,100 | 83 / 144 |
| Realized critical unmet, Arm C (for comparison) | 627 | 0 | 3,439 | 7,151 | 38 / 144 |

Wind is the difference between the two uncovered measures. Subtracting forecast wind reduces the uncovered energy from a median of 10,802 Wh/h to 1,701 Wh/h, which is why the critical-aware reserve is so much smaller than the governed one.

---

## 4. Wind-Independent Comparison (Diagnostic Measurement Only)

To test whether a wind-independent backstop is possible from the existing evidence, I computed the 6-hour reserve that would result if only forecast solar is subtracted: `(1/0.92) × Σ max(0, critical − forecast solar) × dt` over each window. Only steps 0–18 are used, so the window stays within the logged 24 steps. This is a measurement of what a wind-free formula would retain, not a chosen design.

- **Solar-only reserve as a fraction of the governed EBR:** mean **0.65**, median **0.76**.
- **Coverage at the 11 failing hours:** every failing hour's uncovered-by-solar energy (8,990–11,600 Wh) exceeds its realized critical unmet (219–4,723 Wh). A solar-only backstop would have covered all 11 failing hours.

So a wind-free backstop is derivable and covers the observed failures, but it keeps about two-thirds of the reserve. Most of the fuel benefit of the critical-aware formula would be lost along with the wind term.

---

## 5. Limits

1. **Synthetic wind.** Realized wind is a benchmark formula (§0). Its error profile says nothing about real wind behaviour, so the error magnitudes cannot be defended as physical.
2. **Only one distinct error profile.** The 144 hours contain 24 distinct values. Any percentile is over the profile, not over independent weather. The six origins give no statistical spread.
3. **Solar-only reserve computed on steps 0–18 only** (windows inside the logged cycle), so the 65% retention figure excludes the last six steps.
4. **Uncovered energy uses forecast values at step 0 for the hour**, consistent with the existing logs, not the full 24-hour bundle at each step.

---

VERDICT: The wind forecast error in this benchmark is a deterministic, one-sided over-forecast that depends only on the step index within the origin, not on weather. A wind-free backstop is derivable from the existing evidence and would cover all 11 failing hours, but it retains about 65% of the governed reserve, so it is not a low-cost fix. Whether any real wind error is this large is not known.

WIND_ERROR_RANGE: −5,000 W to 0 W per hour (realized − forecast). Mean and median −2,500 W. Over-forecast in 92% of hours. Failing-hour errors: −670 W to −5,000 W. The range is set by the benchmark profile, not by weather.

BACKSTOP_REQUIRED: Yes. A critical-load backstop that does not subtract forecast wind is supported by the existing evidence, since it covers all 11 failing hours. Its size is a consequence of the solar-only formula (about 65% of the governed reserve) and was not chosen here. The evidence does not establish a defensible wind-error magnitude for real operation, because the wind is synthetic.

NEXT_SINGLE_EXPERIMENT: A six-origin solver run for a solar-only variant of the critical-aware reserve (forecast wind excluded from the subtraction), compared against frozen Arm B and the critical-aware arm, with fuel and critical reliability measured. This needs new dispatch solves, so it requires your approval before it runs. Fuel cannot be measured from the existing logs. No margin selection and no controller proposal.
