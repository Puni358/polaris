# Minimality Challenge Audit

## 7-Question Minimality Audit for Proposed Software Elements

### 1. `EMSControlRouter` (`system/control/router.py`)
- Question: Can existing runner carry this logic directly?
- Answer: Runner can call router, but isolating router in `system/control/router.py` preserves clean single-responsibility architecture.
- Minimality Verdict: **KEPT (MINIMAL NEW FILE)**.

### 2. `OptionDFallbackSolver` (`system/optimization/implementations/option_d.py`)
- Question: Can Option B solver execute Option D?
- Answer: No. Option B is an MPC MILP optimizer; Option D is a heuristic emergency fallback per DEC-004.
- Minimality Verdict: **KEPT (MINIMAL NEW FILE)**.

### 3. Additive `StationState` Fields
- Question: Are new fields required?
- Answer: No. `operating_mode="NORMAL"` already exists in schema.
- Minimality Verdict: **REMOVED (ZERO SCHEMA DELTA)**.

### 4. Additive `DispatchPlan` Fields
- Question: Are new fields required?
- Answer: No. Option D outputs map directly to existing `DispatchPlan` fields.
- Minimality Verdict: **REMOVED (ZERO SCHEMA DELTA)**.

### 5. Policy Override Knobs (`ebr_target_wh_override`, etc.)
- Question: Are override knobs required for Option D?
- Answer: No. Option D follows DEC-004 sealed rules cleanly.
- Minimality Verdict: **REMOVED (NO POLICY OVERRIDES)**.

---

## Final Minimality Score
- New Files: **2** (`router.py`, `option_d.py`)
- Schema Changes: **0**
- Protected Files Touched: **0**
