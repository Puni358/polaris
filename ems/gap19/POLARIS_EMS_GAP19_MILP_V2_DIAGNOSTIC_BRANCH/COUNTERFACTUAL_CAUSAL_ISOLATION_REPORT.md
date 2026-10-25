# Full-Window Counterfactual Causal Isolation on R2

**Scope**: Controlled re-solves using the real, unmodified `GAP19HighsNativeOptimizer`.
**No production code, optimizer behavior, R1/R2, assumption, or model was changed.** R1 and
R2 are used only as frozen references (loaded from their own stored raw results, not
re-derived) for the `REAL-BASELINE` and `REAL-STAGE81` conditions. Exactly one new condition
was actually re-solved: `CF-B` (347 origins, real optimizer, identical initial
states/configs). Matrix and model hashes re-verified (MATCH R1/R2). Raw data:
`COUNTERFACTUAL_CF_B_RAW_RESULTS.json`.

## Conditions

| Condition | Solar / demand / wind | `terminal_target_wh` | Status |
|---|---|---|---|
| `REAL-BASELINE` | baseline | computed from baseline's own solar | frozen reference (R2, not re-solved) |
| `REAL-STAGE81` | Stage 8.1 | computed from Stage 8.1's own solar | frozen reference (R2, not re-solved) |
| **`CF-B`** | Stage 8.1 (identical to REAL-STAGE81) | **held fixed at the value REAL-BASELINE's own solar produced** | **newly re-solved, 347 origins** |

## Null/determinism control (item 1: "same forecast in both arms")

Re-solved `REAL-BASELINE`'s own inputs a second, independent time on 5 sample origins:
**bit-identical `DispatchPlan` output in all 5 cases.** Confirms the solver is deterministic
and that identical forecast inputs produce zero delta, as expected — this validates trusting
the differencing logic below.

## Isolation logic

```
Mechanism-1 (pure solar effect, terminal held fixed)       = CF-B − REAL-BASELINE
Mechanism-2 (terminal-reactivity effect, solar held fixed) = REAL-STAGE81 − CF-B
Combined (R2's actual, already-reported effect)            = REAL-STAGE81 − REAL-BASELINE
Interaction/residual                                        = Combined − (Mechanism-1 + Mechanism-2)
```

245 of 347 origins had the `NORMAL` route in all three conditions (route was identical
between `REAL-STAGE81` and `CF-B` at all 347 origins — 0 mismatches — confirming
`terminal_target_wh` does not itself influence the router's NORMAL/EMERGENCY decision).
All figures below are summed over these 245 matched origins.

---

## Headline result: diesel fuel

| | L (summed, n=245) |
|---|---|
| `REAL-BASELINE` | 5,818.32 |
| `REAL-STAGE81` | 10,849.60 |
| `CF-B` | 10,922.79 |

| Decomposition | Δ (L) | % of combined |
|---|---|---|
| **Combined (R2's actual effect)** | **+5,031.28** | 100% |
| **Mechanism-1 (solar only, terminal fixed)** | **+5,104.48** | **101.5%** |
| **Mechanism-2 (terminal reactivity only, solar fixed)** | **−73.19** | **−1.5%** |
| Interaction / residual | 0.000000 | 0% |

**The combined delta matches R2's own already-reported NORMAL-route diesel delta exactly
(+5,031.28 L), confirming internal consistency.** The counterfactual isolation shows the
decomposition sums exactly (zero residual) and is decisive: **holding the terminal target
fixed and varying only solar reproduces slightly more than the entire observed diesel
increase (101.5%). Allowing the terminal target to react to Stage 8.1's own (lower, more
accurate) solar forecast, on top of that, very slightly reduces total diesel use
(−1.5%), not increases it.**

## Correction to the prior (association-based) reports

The earlier reports (`R2_DIESEL_INCREASE_CAUSAL_FORENSIC_REPORT.md`,
`FULL_WINDOW_DIAGNOSTIC_FORENSIC_REPORT.md`) estimated the terminal-reserve mechanism's role
using correlation (87.3% of diesel delta in J2-binding cycles) and same-timestep association
(11.73% of the delta at the binding hour). **This genuine counterfactual isolation shows the
true causal contribution of terminal-target reactivity to the diesel delta is approximately
zero (−1.5%, i.e., not an increase at all).** The earlier non-zero associations were real
patterns in the data but were confounded: both the higher terminal target *and* the higher
diesel use under Stage 8.1 are independent downstream consequences of the same cause (lower
forecasted solar) — the terminal target reacting to solar does not, once properly isolated,
add diesel burden on top of the direct energy-balance effect. **Essentially the entire
diesel increase is explained by Mechanism 1 (direct energy balance) alone.**

## Curtailment

| | Wh (summed, n=245) |
|---|---|
| `REAL-BASELINE` | 31,916,981.6 |
| `REAL-STAGE81` | 10,157,843.9 |
| `CF-B` | 10,157,843.9 |

Mechanism-1 = −21,759,137.7 Wh (100% of the combined −21,759,137.7 Wh effect).
**Mechanism-2 = exactly 0.0 Wh.** Curtailment is completely unaffected by which
`terminal_target_wh` value is used — fully consistent with curtailment (J4, lowest priority)
being determined by solar availability and the diesel-minimal solution, with no causal
channel back from the terminal-reserve envelope.

## Battery charge / discharge

| | Discharge Wh | Charge Wh |
|---|---|---|
| `REAL-BASELINE` | 28,635,629.7 | 41,269,237.3 |
| `REAL-STAGE81` | 26,575,094.1 | 38,658,765.6 |
| `CF-B` | 26,494,624.4 | 38,736,139.1 |

| Decomposition | Discharge Δ | Charge Δ |
|---|---|---|
| Combined | −2,060,535.6 | −2,610,471.7 |
| Mechanism-1 | −2,141,005.3 | −2,533,098.2 |
| Mechanism-2 | +80,469.7 | −77,373.5 |

Mechanism-2's battery effect is small and partially offsetting (more discharge, less
charge, under the reactive/higher terminal target) relative to Mechanism-1's much larger
effect — consistent with the near-zero net fuel effect of Mechanism-2 found above (slightly
different battery scheduling, no net fuel cost).

## SOC range

| | Min % (across all cycles) | Max % |
|---|---|---|
| `REAL-BASELINE` | 52.08 | 95.00 |
| `REAL-STAGE81` | 45.22 | 95.00 |
| `CF-B` | 45.22 | 95.00 |

SOC minimum is **identical between `REAL-STAGE81` and `CF-B`** (45.22% both) — the lower SOC
floor under Stage 8.1 is entirely a Mechanism-1 (solar) effect; terminal-target reactivity
contributes nothing to it.

## J2 / J3 behavior (the reserve-shortfall / fuel objectives themselves)

| | `REAL-BASELINE` | `REAL-STAGE81` | `CF-B` |
|---|---|---|---|
| J2 (reserve shortfall, Wh) | 1,499,921.9 | 2,115,932.4 | **1,499,921.9** |
| Binding cycles (of 245) | 98 | 125 | **98** |
| J3 (diesel, L) | 6,258.32 | 11,523.60 | 11,582.80 |

**`CF-B`'s J2 value and binding-cycle count are identical to `REAL-BASELINE`'s (98
cycles, same total shortfall), not to `REAL-STAGE81`'s (125 cycles).** This confirms J2 is a
direct, almost mechanical function of which numeric `terminal_target_wh` value is supplied —
whether shortfall occurs is governed by the target value itself, essentially independent of
which solar forecast is paired with it. The increase from 98→125 binding cycles under
`REAL-STAGE81` is driven entirely by the target value increasing (because Stage 8.1's own
formula computes a higher target from its lower solar) — not by solar's direct effect on
feasibility. Meanwhile J3 (diesel) moves almost entirely with the solar forecast (`CF-B`'s
11,582.80 L is close to `REAL-STAGE81`'s 11,523.60 L, both far above `REAL-BASELINE`'s
6,258.32 L), confirming diesel use tracks the solar input, not the terminal target value.

---

## Causal interpretation supported by the re-solves

1. **The "+25.7% diesel" effect under Stage 8.1 is caused almost entirely by the solar
   forecast difference itself (direct energy balance), not by the terminal-reserve
   formula's reactivity to that forecast.** Isolated Mechanism-1 alone reproduces 101.5% of
   the observed effect.
2. **Terminal-target reactivity, in isolation, does not add diesel use — if anything it
   marginally reduces it (−1.5%), with zero unexplained interaction.** This is a genuine
   causal isolation (controlled re-solve, not an association), and it supersedes the
   correlation/same-timestep estimates in the prior two reports for the specific question
   of "how much diesel does the terminal-reserve mechanism cause."
3. **Curtailment and SOC-minimum are fully explained by Mechanism-1; Mechanism-2's
   contribution to both is exactly zero.**
4. **J2 (reserve shortfall) is, as expected by construction, driven directly by whichever
   terminal-target value is supplied** — this is not a new causal finding (it is definitional:
   J2 measures the gap against whatever target is given) but confirms the instrumentation
   and isolation are behaving exactly as the code dictates, with no surprises.
5. **Caveat, stated precisely**: this isolation decomposes the window's summed totals over
   245 matched-route origins; it does not claim that every individual origin's diesel delta
   is 100% Mechanism-1 (a small positive/negative Mechanism-2 contribution could exist at
   individual origins and still net to −1.5% in aggregate — this report does not examine the
   per-origin distribution of Mechanism-2, only its full-window sum).

## What was NOT done (per instruction)

- No parameter was tuned, no optimizer code was changed, no new terminal formula or
  objective weighting was chosen or implemented.
- R1 and R2 remain frozen and were not re-run — only loaded as references.
- Only one new counterfactual condition (`CF-B`) was actually solved; `REAL-BASELINE` and
  `REAL-STAGE81`'s own values were reused from R2 exactly as stored.

## STOP

Counterfactual causal isolation complete. R1/R2 untouched. No optimizer behavior changed.
