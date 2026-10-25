# R2 Forensic Report: Why the More Accurate Stage 8.1 Solar Forecast Causes +25.7% Diesel

**Scope**: Analysis only, of already-computed R2 data (`R2_FULL_EXPERIMENT_RAW_RESULTS.json`,
694 cycles) plus the already-reviewed GAP19 code
(`system/optimization/implementations/gap19_highs_native.py`). No code, config, assumption,
or model was changed. No new experiment was run — all numbers below are aggregated directly
from the existing R2/R1 raw results (which are numerically identical) and from the solar
accuracy metrics already computed in `R2_AUDIT_AND_STOP_REPORT.md` (Q1).

---

## The apparent paradox, resolved up front

A more *accurate* forecast is not the same as a more *favorable* one. The R2 baseline solar
forecast has a large, systematic **over-prediction bias of +164.6 W/m²** (nMAE 2.01) —
confirmed in `R2_AUDIT_AND_STOP_REPORT.md` Q1. Stage 8.1's forecast is accurate (bias −0.9
W/m², nMAE 0.26) but, on most of the 2024 days in this window, that accurate value is *lower*
than the baseline's optimistic constant curve. **The MILP does not know the baseline is
wrong** — each cycle plans against its own forecast as if it were true. So the baseline's
plans are internally self-consistent with a solar budget that doesn't exist; Stage 8.1's
plans are self-consistent with (approximately) the real one. The "+25.7% diesel" is diesel
that Stage 8.1's plan judges actually necessary; the baseline's lower diesel figure is an
artifact of believing in more sun than there was, not evidence of better fuel economy. This
is a confirmed fact (directly measured bias/accuracy numbers), not an interpretation of
intent.

---

## Quantified causal chain (from R2 raw data, 245 NORMAL-route origins)

### Step 0 — root cause: solar forecast difference only

Confirmed in the prior R1 forensic report and unchanged in R2: `demand` and
`wind_generation` are bit-identical between arms at all 347 origins (re-verified for R2,
347/347, 0 mismatches). Only `solar_generation` differs.

### Step 1 — objective-term totals, both arms, summed over all 245 NORMAL origins

| Objective | Baseline (sum) | Stage 8.1 (sum) | Δ (Stage8.1 − baseline) |
|---|---|---|---|
| J1 — critical deficit (Wh) | 0.00 | 0.00 | 0.00 (never binds, either arm) |
| J2 — reserve shortfall (Wh) | 1,499,921.9 | 2,115,932.4 | **+616,010.5** |
| J3 — diesel fuel (L) | 6,258.32 | 11,523.60 | **+5,265.28** |
| J4 — curtailment (Wh) | 31,916,981.8 | 10,157,843.9 | **−21,759,137.9** |
| `terminal_target_wh` (sum) | 35,778,742.0 | 36,255,679.0 | +476,937.0 |

J1 is identically zero for both arms in every NORMAL cycle — critical load is always fully
served; it plays no role in the diesel difference.

### Step 2 — curtailment vs. diesel: no cost trade-off exists in this model

**Confirmed from code** (`gap19_highs_native.py:365-385`): J3 (diesel, priority 2) and J4
(curtailment, priority 1) are solved as a **strict lexicographic sequence**, not a weighted
sum (`blend_multi_objectives = False`, line 349). Diesel fuel (liters) and curtailment (Wh)
are never combined into one scalar anywhere in the code — they are different units on
different priority tiers. The solver minimizes diesel first (`c3`, priority 2), and only
*among the solutions that already achieve that diesel minimum* does it then minimize
curtailment (`c4`, priority 1). **Confirmed from data**: `corr(Δ J4, Δ J3) = 0.014` across
the 245 origins — essentially no linear relationship. This directly falsifies any "diesel
cost vs. curtailment penalty trade-off" framing: there is no shared cost function being
balanced. The simultaneous pattern of "more diesel + much less curtailment" under Stage 8.1
is two *independent* downstream effects of the same upstream cause (less forecasted solar),
not one variable being traded for the other.

### Step 3 — terminal-reserve / J2 effect: the dominant mechanism, now quantified

`corr(Δ terminal_target_wh, Δ J3) = 0.683`; `corr(Δ J2, Δ J3) = 0.770` — the strongest
correlation of any pair measured. Decomposing the full Δ J3 = +5,265.28 L by whether the
governed reserve envelope was binding (`J2 > 0` for at least one arm) or fully slack
(`J2 = 0` for both arms):

| Origin subset (of 245) | n | Σ Δ J3 (L) | Share of total Δ J3 |
|---|---|---|---|
| Reserve envelope binding for at least one arm (J2 > 0 somewhere) | 125 | **+4,598.71** | **87.3%** |
| Reserve envelope fully slack for both arms (J2 = 0 both) | 120 | +666.58 | 12.7% |

**This is the dominant, quantified mechanism: 87.3% of the total diesel increase occurs in
cycles where the governed terminal/EBR reserve envelope is actively binding.** Mechanism:
`terminal_target_wh` is computed (by the R1/R2 formula) from the same lower trailing-6h solar
that Stage 8.1 forecasts, so Stage 8.1's value is higher more often (mean +1,946.7 Wh/cycle,
sum +476,937 Wh over 245 origins) and the resulting envelope
`e_stage2_target[23] = max(ebr_target_wh_list[23], terminal_target_wh)`
(`gap19_highs_native.py:151`) binds more often (nonzero shortfall in 125/245 Stage 8.1 cycles
vs. 98/245 baseline cycles). Because J2 (priority 3) is minimized strictly *before* J3
(priority 2), the solver spends diesel fuel to reduce that shortfall before it will accept
the shortfall to save fuel. The remaining 12.7% (666.58 L) occurs even when the reserve
envelope never binds at all for either arm — this is the pure direct energy-balance effect
(less solar forecast → bus-bar balance constraint, `gap19_highs_native.py:227-231`, needs
more diesel to meet ordinary demand, with no reserve-envelope contribution) — confirmed to
exist on its own (consistent with the 2024-06-19 single-origin case identified in the prior
R1 forensic report).

### Step 4 — battery charge/discharge: a secondary, consistent symptom, not an independent cause

| Metric (sum, 347 cycles) | Baseline | Stage 8.1 | Δ | % |
|---|---|---|---|---|
| Planned battery discharge (Wh) | 38,109,191.2 | 36,048,030.8 | −2,061,160.4 | −5.4% |
| Planned battery charge (Wh) | 41,330,317.3 | 38,711,815.7 | −2,618,501.6 | −6.3% |

Both charge and discharge fall together under Stage 8.1 — consistent with less solar being
available to charge the battery in the first place, and diesel partially substituting for
battery-supplied energy to meet demand and the (often higher) reserve target. This is a
consequence of Steps 0–3, not an independent causal channel.

### Step 5 — diesel dispatch, realized (t0) vs. planned

Baseline never dispatches diesel at the realized first hour across any of the 347 cycles
(`t0_fuel_consumed_l = 0.0`, all origins). Stage 8.1 dispatches diesel at t0 in 62/347
cycles, consuming 636.20 L realized (vs. baseline's 0.0 L) — consistent with Stage 8.1's
plans more frequently requiring diesel from hour 0, not only later in the 24h horizon.

---

## Summary: dominant mechanism ranking (quantified, not speculative)

1. **Terminal-reserve / J2 lexicographic-priority effect — dominant, ~87.3% of total Δ
   diesel (4,598.71 of 5,265.28 L)**, driven by Stage 8.1's own (more accurate, often lower)
   solar forecast raising the computed `terminal_target_wh` and triggering GAP19's
   strict J2-before-J3 priority.
2. **Direct bus-bar energy-balance effect — secondary but real, ~12.7% of total Δ diesel
   (666.58 L)**, present even with zero reserve-envelope involvement; the baseline minimum
   contribution from "less solar forecast → more diesel needed to meet ordinary demand"
   alone.
3. **Curtailment is not a cause or a trade-off partner of either mechanism above** —
   `corr ≈ 0.014` with diesel; it falls because there is less forecasted solar to curtail,
   independently of the diesel decision, which is computed first and separately under the
   strict lexicographic order.
4. **J1 (critical deficit) plays no role** — identically zero for both arms, always.
5. **Battery charge/discharge changes are a downstream symptom** of 1–2, not an independent
   cause.

## Confirmed facts vs. unresolved points

**Confirmed** (directly measured from R2 data and/or GAP19 source code, no speculation):
- Root cause is solar-forecast-only (wind/demand bit-identical, re-verified for R2).
- GAP19 uses strict lexicographic priorities, not weighted costs (code-confirmed).
- The 87.3% / 12.7% binding/non-binding split of the diesel delta (data-confirmed, exact
  figures from the 245-origin NORMAL-route subset).
- Baseline's solar forecast carries a large systematic over-prediction bias; Stage 8.1's
  does not (Q1 metrics, already computed, re-cited here).
- Curtailment and diesel deltas are not correlated (`0.014`) — rules out a direct trade-off.

**Unresolved** (would require a new, out-of-scope counterfactual run to establish precisely):
- The exact diesel liters attributable to the terminal-reserve mechanism *alone*, holding
  solar fixed (the 87.3%/12.7% split is an observational decomposition by binding status,
  not a controlled ablation of the reserve formula itself).
- Whether a different (still-unauthorized) terminal-reserve formula/margin would reduce or
  change this ratio — not tested.
- Whether Stage 8.1's diesel-higher plans would in fact be *more* correct in a true
  closed-loop (multi-hour) rollout, versus the single-step realized/planned split used
  throughout R1/R2 — this report traces mechanism within the existing single-step design,
  it does not extend it.

No parameters were tuned and no new experiment was run in producing this report.
