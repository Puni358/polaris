# The hard question: "Every model saves about the same diesel. Why?"

## The numbers (Page 4 · PROOF)
Same planner, same weather, same wind, same demand, zero load lost for all:
| Forecaster | Diesel | Lowest battery |
|---|---|---|
| Physical baseline | 26,859 L | 20.5% |
| Successor v2 | 26,992 L | 20.8% |
| Candidate K | 26,977 L | 22.5% |
| Candidate N1 | 26,985 L | 22.5% |
| **N6 (POLARIS)** | 26,890 L | **22.5%** |
All within 0.5%. The hard floor is 20%.

## The answer to say (30 seconds)
"The 30% saving comes from the **planner**, not from which forecaster feeds it. Compared with a controller that does not plan ahead, planning cuts fuel by 30%. Once any decent forecast is plugged in, the planner already knows when the sun comes back, so a better forecast moves fuel by less than 0.5%. And it re-plans every hour from the real battery, so small forecast mistakes get corrected before they cost fuel.
Where the better forecaster shows up is **safety**. With N6 the battery never went below 22.5%. With the physical baseline it touched 20.5%, half a point from the hard floor. So our forecaster does not save more fuel; it keeps more cushion. We tested this fairly and we report it as it came out."

## Why this happens (kid version)
- Most of the diesel is burned in the dark weeks. No forecaster can create sun that is not there; they all correctly say "dark".
- The forecasters differ by about 37 to 42 W/m² of average mistake. That is small next to the difference between a bright day and a dark one, so the plan comes out almost the same.
- The planner re-plans every hour, so a mistake is fixed in an hour.
- The baseline we compare with is already physics plus Chronos-2, a strong starting point. It is not a weak model.

## What NOT to say
- Do not say "our forecaster saves more diesel". It does not (the baseline burns 31 L less than N6, 0.1%).
- Do not say the 30% belongs to the forecaster.
- The reactive (38,405 L) comparison is against a controller without planning, a different controller; do not call it a forecaster comparison.

## If they push: "Then why build a better forecaster?"
1. It is 12% more accurate than the baseline on the blind year (36.79 vs 41.77 W/m²).
2. It gives the uncertainty that sizes the cushion.
3. Safer battery margin (22.5% vs 20.5%).
4. On a harder system (smaller battery, less wind) accuracy would matter more. We have not tested that, so we say "we expect", not "we proved".
