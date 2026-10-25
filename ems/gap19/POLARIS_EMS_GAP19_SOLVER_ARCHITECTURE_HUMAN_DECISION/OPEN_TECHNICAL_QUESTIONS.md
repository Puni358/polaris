# OPEN TECHNICAL QUESTIONS

## Open Technical Questions for Solver Engineering Teams

This document lists open technical questions that should be considered by human decision-makers and solver engineering teams when evaluating Option A vs Option B.

---

## Technical Questions Register

| # | Technical Question | Impact on Option A | Impact on Option B |
| :--- | :--- | :--- | :--- |
| **1** | Does the production environment permit installing third-party binary C++ wheels such as `highspy`? | None (Option A uses standard SciPy). | Critical (Option B requires `highspy` or private SciPy bindings). |
| **2** | Is Python function call overhead across 4 sequential solver passes ($\approx 5\text{--}10\text{ ms}$) acceptable within the station's 1-minute or 5-minute MPC step loop? | Minor (Acceptable for 1-min MPC). | Eliminates Python pass overhead. |
| **3** | How should intermediate stage tolerance locks ($\varepsilon_k$) be tuned for physical units ($\text{Wh}$ vs $\text{L}$)? | Managed directly in Python code per pass. | Passed as solver parameters (`abs_tol`, `rel_tol`). |
| **4** | What solver logging level is required for regulatory auditability of lexicographic passes? | High (Each pass emits independent SciPy result logs). | Requires parsing solver C++ output streams. |

---

## Neutral Guidance

Both options are mathematically capable of solving the GAP19 4-stage objective hierarchy under proper configuration. The choice depends on team preferences regarding dependency management vs orchestration control.
