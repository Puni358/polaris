# Double-Counting Forensics Report

## 1. Proof of Single Shortfall Variable Architecture

1. In `gap19_highs_native.py` (lines 164–165):
   - Variable layout: base 360 + 24 $P_{\text{unmet\_crit}}$ + 24 $s_{J2} = 408$ total decision variables.
   - There is **no separate** terminal shortfall variable ($s_{\text{terminal}}$).
2. Linear constraints $288..311$:
   - $E_{\text{next}}[t] + s_{J2}[t] \ge E_{\text{stage2,target}}[t] + E_{\text{min,wh}}$ for $t \in [0, 23]$.
   - Single constraint array per timestep enforcing reserve shortfall against the pointwise envelope $E_{\text{stage2,target}}[t]$.
3. Objective vector $c_2$:
   - Linear penalty weight $1.0$ applied exclusively to $s_{J2}[t]$.
   - No secondary reserve penalty vector exists.

---

## 2. Verdict

```
SEPARATE_TERMINAL_SHORTFALL_VARIABLE = ABSENT (0)
INDEPENDENT_ADDITIVE_PENALTY = ABSENT (0)
UNIFIED_ENVELOPE_MODEL = CONFIRMED
NO_DOUBLE_COUNTING = ESTABLISHED
DOUBLE_COUNTING_FORENSICS_STATUS = PASS
```
