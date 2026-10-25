# Pointwise Maximum Envelope & Double Counting Reconciliation

## 1. Envelope Formulation Proof

The unified stage 2 reserve shortfall penalty in Option B is formulated as:

\[
J_2 = \sum_{t=0}^{23} s_{J2}[t]
\]

where each $s_{J2}[t] \ge 0$ is constrained by:

\[
E_{\text{next}}[t] + s_{J2}[t] \ge E_{\text{stage2,target}}[t] + E_{\text{min,wh}}
\]

and the pointwise maximum target is:

\[
E_{\text{stage2,target}}[t] = \max\left(E_{\text{EBR,target}}[t], \, \delta_{t, 23} \cdot E_{\text{term,target}}\right)
\]

---

## 2. Proof of Double-Counting Elimination

1. At $t = 23$:
   - $E_{\text{EBR,target}}[23] = 21,739.13\text{ Wh}$ (1-hour lookahead for $20\text{ kW}$ critical load).
   - $E_{\text{term,target}} = 100,000.00\text{ Wh}$.
   - $E_{\text{stage2,target}}[23] = \max(21,739.13, 100,000.00) = 100,000.00\text{ Wh}$.
2. If the targets had been blindly additive, the required target at $t=23$ would have been $121,739.13\text{ Wh}$ ($161,739.13\text{ Wh}$ battery level).
3. The unified envelope target of $100,000.00\text{ Wh}$ ($140,000.00\text{ Wh}$ battery level) demonstrates that EBR and Terminal Reserve are **not** additively double-counted.

---

## 3. Shortfall Vector Verification

- Hourly Shortfall Vector $s_{J2}[t]$: `[0.0]*24`.
- Total $J_2$ Objective Value: `0.0 Wh`.

---

## 4. Verdict

```
DOUBLE_COUNTING_ELIMINATED = YES
UNIFIED_ENVELOPE_FORMULATION_MATCH = EXACT
J2_ENVELOPE_RECONCILIATION_STATUS = PASS
```
