# MILP Semantics Audit

```text
MILP_PRIORITY_SEMANTICS = ESTABLISHED
```

An isolated toy test on binary integer variables ($y \in \{0, 1\}$, Obj A: $\min y$ with priority 4, Obj B: $\min -y$ with priority 1) yielded $y = 0.0$.

This confirms that HiGHS priority sorting convention (`HIGHER_NUMBER_IS_HIGHER_PRIORITY`) holds identically for MILP integer variables.
