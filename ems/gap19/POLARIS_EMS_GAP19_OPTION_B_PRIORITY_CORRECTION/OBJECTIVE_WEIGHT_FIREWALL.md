# Objective Weight Firewall

## Firewall Declaration

The priority correction gate strictly isolates lexicographic priority ordering from objective coefficient vector definitions.

```text
OBJECTIVE_VECTORS_REQUIRE_CHANGE = NO
```

## Objective Coefficient Integrity Audit

The four objective vectors defined in `gap19_highs_native.py` remain mathematically accurate and untouched:

1. **$c_1$ (Critical Deficit Wh)**:
   - $c_1[\text{idx\_unmet\_crit} + t] = 1.0 \times dt$
2. **$c_2$ (EBR Reserve Shortfall Wh)**:
   - $c_2[\text{idx\_s\_ebr} + t] = 1.0$, $c_2[\text{idx\_s\_term}] = 1.0$
3. **$c_3$ (Diesel Fuel Consumption Liters)**:
   - $c_3[base + 7] = marg\_fuel\_l\_wh \times dt$
   - $c_3[base + 13] = base\_fuel\_l\_h \times dt$
   - $c_3[base + 14] = startup\_fuel\_l$
4. **$c_4$ (Renewable Curtailment Wh)**:
   - $c_4[base + 2] = 1.0 \times dt$, $c_4[base + 3] = 1.0 \times dt$

No modification of $c_1, c_2, c_3, c_4$ is authorized or required.
