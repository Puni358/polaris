# STAGE 2 EBR LINEARIZATION AUDIT

## Mathematical Linearization of Stage 2 Reserve Deficit Objectives

This document details the mathematical linearization of Stage 2 piecewise linear penalty terms $\max(0, E_{\text{target}} - E)$.

---

## Mathematical Linearization

The governed Stage 2 energy-domain objective is:

$$J_2 = \sum_{t=0}^{H-1} \max\left(0, E_{\text{EBR,target}}(t) - E_{\text{reserve,available}}(t)\right) + \max\left(0, E_{\text{terminal,target}} - E(H)\right)$$

### Auxiliary Variable Introductions:
1. **Per-step EBR Shortfall Slack Variable**: $s_{\text{EBR}}(t) \ge 0$ for $t \in \{0, \dots, H-1\}$.
2. **Terminal Reserve Shortfall Slack Variable**: $s_{\text{term}} \ge 0$.

### Linear Inequality Constraints Added to Matrix $A$:
1. **EBR Reserve Shortfall Constraint**:
   $$s_{\text{EBR}}(t) \ge E_{\text{EBR,target}}(t) - E(t) \implies E(t) + s_{\text{EBR}}(t) \ge E_{\text{EBR,target}}(t)$$
2. **Terminal Reserve Shortfall Constraint**:
   $$s_{\text{term}} \ge E_{\text{terminal,target}} - E(H) \implies E(H) + s_{\text{term}} \ge E_{\text{terminal,target}}$$

### Linearized Stage 2 Objective Vector ($c_2$):
$$\min_{x, s} J_2 = \sum_{t=0}^{H-1} s_{\text{EBR}}(t) + s_{\text{term}}$$

---

## Compatibility Status

```text
STAGE2_LINEARIZATION = ESTABLISHED
```
The piecewise linear penalty is 100% linearizable using $H+1$ continuous non-negative slack variables ($s_{\text{EBR}}(t), s_{\text{term}}$) and is 100% compatible with native HiGHS MILP optimization.
