# 365D PRE-REGISTERED EXPERIMENTAL METRICS MATRIX

## Primary Metrics
1. Total Diesel Fuel Consumed ($F_{\text{total}}$ [L])
2. Absolute Fuel Difference ($\Delta F = F_{\text{POLARIS}} - F_{\text{Baseline}}$ [L])
3. Percentage Fuel Difference ($\% \Delta F$)

## Secondary Metrics
Diesel runtime ($h$), diesel starts, diesel generation ($kWh$), solar used ($kWh$), wind used ($kWh$), renewable curtailment ($kWh$), battery charge/discharge ($kWh$), SOC min/max/avg (%), unmet critical load ($kWh$, target = 0.0), total unmet load ($kWh$), ECD emergency count, governed relaxation count.

## Integrity Metrics
Future-truth access count (target = 0), state reset count (target = 0), timestamp violations (target = 0), power balance error (target $< 10^{-4}$ W), infeasible solves (target = 0), invalid dispatches (target = 0), twin advancement on invalid state (target = 0), first-action-only compliance (100%), bitwise reproducibility (100%).
