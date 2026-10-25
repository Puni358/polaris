# POLARIS — R2 Solver Reproducibility Investigation (Prompt 3, READ-ONLY)

Scope: whether the real HiGHS solve used by `PlannerCFV1Optimizer`
(`experiments/stage4_planner_cf_consistency_2025/research_numerical_extractor_planner_cf_v1.py`)
is reproducible across environments. Does not cover R3/R4/R5. Nothing in
`experiments/exp_three_arm_2024/` was modified to produce this report; it is saved outside that
frozen package (see "Report destination" at the end) for exactly that reason.

## 1. Verdict

**No genuine cross-environment solver comparison has ever been performed in this project's
history.** This is a directly-confirmed fact, not an inference: the only other environment this
project has ever used (the "sandbox") explicitly **mocks `highspy.Highs` to raise** rather than
solving (`tests/conftest.py`'s `no_solver` autouse fixture, confirmed by its own description in
`experiments/exp_three_arm_2024/CHANGELOG.md:74`, and by `reports/PREP_CHECKS_OUTPUT.txt:3`'s own
header: *"highspy (import only; Highs mocked to raise)"*). The real solver has only ever actually
run in **one** environment — the device venv (Python 3.12.3, NumPy 2.5.2, highspy/HiGHS 1.15.1) —
across two events: the one real 14,760-solve experiment attempt
(`results/run_20261011T075716Z/`) and the Prompt 1/2 fixture tests added this process. **What is
assumed, not demonstrated:** that this solver's behavior would be identical in any other
environment. **What is genuinely demonstrated, but about a different computation entirely:** the
calibration step (`calibrate_arm_c.py`, a deterministic curve-fit/binning procedure with **no
MILP or HiGHS involvement**) was independently re-run in this same device venv and produced a
byte-for-byte identical `gamma_fit`/`quantiles` block to the original run performed under Python
3.13.16/NumPy 2.5.3 — a real, checked cross-environment reproducibility result, but **it says
nothing about the solver**, and must not be conflated with it.

## 2. Environment inventory

| Environment | Python | NumPy | pandas | pvlib | scipy | highspy | HiGHS core | Real solver ever run here? | Source |
|---|---|---|---|---|---|---|---|---|---|
| Device venv (this session) | 3.12.3 | 2.5.2 | 3.0.5 | 0.16.1 | — | **1.15.1** | **1.15.1** (`highspy.Highs().version()`, queried directly this turn) | **Yes** — the one real experiment attempt, plus the new fixture tests | directly queried, this session |
| "Sandbox" (prior session, referenced throughout governance docs) | 3.13.16 | 2.5.3 | 3.0.5 | 0.16.1 | 1.18.1 | **unrecorded** (no version string anywhere) | **unknown** | **No** — `highspy.Highs` mocked to raise | `experiments/exp_three_arm_2024/reports/PREP_CHECKS_OUTPUT.txt:3`, `HANDOVER.md:96,242`, `CHANGELOG.md:74` |

`requirements.txt` (repo root) pins only `contourpy, cycler, fonttools, kiwisolver, matplotlib,
numpy==2.5.2, packaging, pandas==3.0.5, pillow, pyparsing, python-dateutil, scipy==1.18.1,
seaborn, six` — **`highspy`/HiGHS, `pvlib`, and `pyyaml` are not pinned anywhere in version
control.** No `poetry.lock`, `Pipfile.lock`, or equivalent lockfile exists anywhere in the repo
(searched explicitly, none found). The device venv's `highspy==1.15.1` (confirmed via
`pip show highspy`) is therefore a fact about what happens to be installed right now, not a
version the project has committed to anywhere.

**The sandbox's `highspy`/HiGHS version cannot be recovered** — it was never recorded, and that
environment no longer exists for me to query. This is stated as a limitation, not guessed at.

## 3. Relevant code paths

All in `research_numerical_extractor_planner_cf_v1.py` (frozen, imported by path, never modified —
re-verified this session, hash `a8dd9fc7d84e3d2344ba4f99ba1b1cd0ec2165a83d8f7af438b69f8178815093`,
matching its manifest-listed value):
- HiGHS construction and options: lines 344-347 (`output_flag=False`, `threads=1`,
  `blend_multi_objectives=False`; no `time_limit` or MIP-tolerance option set anywhere).
- Objective priorities: line 85 (`PRIORITY` dict), lines 352-365 (`HighsLinearObjective` per
  objective, `abs_tolerance=rel_tolerance=0.0`).
- Single solve call: line 367 (`h.run()`).
- Termination/status handling: lines 368-372 (`h.getModelStatus()`, branch to
  `_infeasible_plan()` if not `kOptimal`), line 481 (`constraint_status="OPTIMAL"`, a hardcoded
  literal independent of the native status string), line 425 (`"solver_status": str(model_status)`
  — the native string, now also preserved as `solver_status_native` downstream in
  `experiments/exp_three_arm_2024/scripts/run_three_arm_2024.py:359`, added during the Prompt-1
  incident fix).
- `threads=1` (line 346) is the one explicit determinism-relevant setting found — single-threaded
  solving removes thread-scheduling nondeterminism as a variable, though it says nothing about
  cross-*version* determinism (different HiGHS builds can still legitimately return different, 
  equally-valid vertices for a degenerate LP/MILP, as already observed within a *single* 
  environment in Prompt 2's Fixture C).

## 4. Existing evidence — what it does and does not prove

| Test file | Real solver? | What it establishes | What it does NOT establish |
|---|---|---|---|
| `tests/test_planner_cf_v1.py` (24 tests) | Yes (device venv only) | Row construction, bus-balance identities, EMERGENCY-mode behavior, customer-first behavior, all in the device venv | Nothing about any other environment |
| `tests/test_planner_cf_v12.py` (18 tests) | Yes (device venv only) | Fuel-feasibility row interactions, tie-break admission rules, determinism of *repeated solves in the same environment* (`test_F5_repeated_solves_are_deterministic` — same-environment only, confirmed by reading its name and intent; it does not invoke a second environment) | Cross-environment reproducibility |
| `tests/test_planner_cf_v1_priority_scarcity.py` (3 tests, added Prompt 2) | Yes (device venv only) | Objective-priority enforcement under genuine scarcity, with independently hand-verified totals | Cross-environment reproducibility |
| `experiments/exp_three_arm_2024/tests/*` (396 passed) | **No** — `no_solver` fixture mocks `highspy.Highs` to raise in every one of these | Governance/authorization/telemetry-plumbing correctness | Anything about solver behavior at all |

**Observable metrics, confirmed available from the existing real-solver tests:** `plan.constraint_status`
(termination), `opt.last_objectives["J1".."J4"]` (objective values), all `DispatchPlan` fields
(decision variables: `load_served`, `battery_charge/discharge`, `diesel_power`,
`renewable_curtailment`, `unmet_load`, etc.), and per-step diagnostics (`mip_gap`,
`solver_status`) via `opt.last_diagnostics`. **Nothing here is currently blocked from
comparison** — the gap is entirely the *absence of a second real-solver environment to compare
against*, not a telemetry gap. Multiple-optima handling: already demonstrated necessary in
practice (Prompt 2, Fixture C) — any comparison protocol must compare objective *totals*, not
raw decision vectors, unless the instance is specifically constructed to have a unique optimum.

## 5. Reproducibility risks, ranked

1. **(Highest practical significance) No second real-solver environment has ever existed to compare against.** Every claim about cross-environment solver reproducibility in any prior governance document is, on inspection, either about calibration (not the solver) or simply absent. This is the dominant gap.
2. **`highspy`/HiGHS is entirely unpinned in version control.** A future environment rebuild could silently install a different HiGHS version with no record of what changed, and no lockfile would flag it.
3. **Degenerate optima are real and already observed within a single environment** (Prompt 2). Any future cross-environment comparison must be designed around this — comparing decision vectors directly would produce false "mismatches" even if both environments are behaving correctly.
4. **(Lower practical significance here) Thread count is pinned to 1**, removing one plausible nondeterminism source — this is a mitigating fact, not a residual risk.

## 6. Smallest next step — proposal only, not performed here

The narrowest test that would add real evidence: obtain or construct **one genuinely different
environment** (a different HiGHS/highspy build — even a different installed version on this same
machine, if one can be found or installed without altering the device venv currently bound to the
live calibration/execution hashes), and re-run the **existing** `tests/test_planner_cf_v1.py`,
`test_planner_cf_v12.py`, and `test_planner_cf_v1_priority_scarcity.py` unchanged against it,
capturing `constraint_status` and all five objective totals for each fixture. Compare objective
**totals** (not raw decision vectors, per the degenerate-optima finding above) within a tolerance
tied to HiGHS's own default MIP gap (observed ≈`9×10⁻⁵` relative, Prompt 2) rather than an
invented number. This is a test-execution step, not a production-code change, and is explicitly
**not performed in this prompt**.

## 7. Scope and integrity confirmation

**Files changed:** this report only, plus (earlier, Prompt 2) `tests/test_planner_cf_v1_priority_scarcity.py` — neither touches `experiments/exp_three_arm_2024/` or any frozen file.
**Commands run this prompt:** `cat requirements.txt`; a search for lockfiles (none found); `pip show highspy`; `highspy.Highs().version()` (constructs a `Highs` object and reads its version string — does **not** call `.run()`, add any row/variable, or solve anything); targeted greps across existing governance docs. No solver workload was executed, no MILP was solved, no experiment file was touched.
**Environments actually compared:** none — only one real-solver environment exists to inspect; this report states that limitation rather than inventing a second one.

### Report destination
Saved at `tests/R2_SOLVER_REPRODUCIBILITY_INVESTIGATION_2026-10-11.md` (repo root, next to the
Prompt 2 fixture file). No existing `reports/` convention unambiguously covers this topic:
`experiments/exp_three_arm_2024/reports/` is manifest-tracked inside the frozen package you've
explicitly protected in this prompt, and placing a new file there would (as happened once already
in this process) stale that package's manifest again; `experiments/stage4_planner_cf_consistency_2025/`
has no top-level `reports/` directory at all. Per your instruction not to create a new directory
tree when convention is unclear, this file was placed in the one existing, non-frozen location
already in use for this investigation (`tests/`) rather than inventing a new directory.
