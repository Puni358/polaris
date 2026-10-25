# LEXICOGRAPHIC MODE AUDIT

## Lexicographic vs Blended Mode Control Audit

This document details the empirical verification of `blend_multi_objectives` in `highspy`.

---

## 1. Option Control Verification

- Option Name: `blend_multi_objectives`
- Default Value: `True` (Blended mode)
- Explicit Lexicographic Control: `h.setOptionValue("blend_multi_objectives", False)`

---

## 2. Empirical Verification Evidence

On Toy MILP 02 ($x_1 + 3 x_2 \le 10$, $x_1, x_2 \in \mathbb{Z} \cap [0, 10]$):
- **Lexicographic Mode (`blend_multi_objectives = False`)**:
  - Result: $(x_1^*, x_2^*) = (10.0, 0.0)$
  - Priority 1 objective ($-x_1$) is optimized strictly first, forcing $x_1 = 10$.
- **Blended Mode (`blend_multi_objectives = True`)**:
  - Result: $(x_1^*, x_2^*) = (1.0, 3.0)$
  - Objectives $-x_1$ and $-10 x_2$ are blended into $-x_1 - 10 x_2$, yielding blended minimum at $(1, 3)$ with cost $-31.0$.

---

## Audit Verdict

```text
LEXICOGRAPHIC_MODE = CONFIRMED
```
Setting `blend_multi_objectives = False` explicitly forces HiGHS to execute strict lexicographic optimization rather than blended weighted sums.
