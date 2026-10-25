# POLARIS Governance Decision Record: Global Lower-Bound Certification (Planner-CF Study)

**Record ID:** `GOV-DECISION-LOWER-BOUND-CERTIFICATION-2026-10-06`
**Date (UTC):** 2026-10-06
**Status:** DECIDED — research governance. Production promotion UNAUTHORIZED. No real-data run has occurred.
**Relates to:** `experiments/EXP_PLANNER_CUSTOMER_FIRST_CONSISTENCY_PREREGISTRATION.md` (Amendment A1).
**Does not overwrite:** `experiments/POST_STAGE4_GOVERNANCE_DECISION_RECORD.md` (preserved as the prior decision, unchanged).

---

## 1. Scope

This record decides how the per-origin global relaxed lower bound is certified, aggregated and used for NG7 in the Planner-CF study. It decides no Planner-CF formulation change, no oracle change and no campaign authorization.

## 2. Decisions

**K1. Independence.** The 123 origins are independent 24-hour problems. State resets per origin. No coupling.

**K2. Admissible set.** The lower bound covers zero-unmet trajectories: full critical and non-critical service.

**K3. Accounting.** Primary fuel is realized diesel: 5 L/h when on, plus 0.00025 L/Wh, with 0 L per start. The 2 L per start is a secondary diagnostic only.

**K4. Relaxation.** The bound removes fuel inventory, the 10 kW diesel minimum, the reserve, and the terminal SOC requirement or value. It keeps SOC bounds (with the ±2 Wh margin), battery power, the diesel maximum, exclusivity, busbar balance and renewable availability.

**K5. NG7 rule.** Let `L` be the aggregate mathematical lower bound and `F_c` the realized 123-origin PC-Control fuel. NG7 triggers iff `L > 0.60 × F_c` (strict). NG7 remains NOT EVALUABLE until `F_c` exists. A failure to trigger NG7 does not establish reachability.

**K6. Tight-certification threshold.** The primary tight-certification threshold is an absolute primal–dual gap `≤ 0.01 L`. This threshold is a decision-precision rule. It is not a mathematical validity requirement.

**K7. Time limit and dual retention.**
- The real lower-bound run uses a 60-second time limit per origin.
- A finite valid dual is retained as `dual_L`, whether or not an incumbent exists.
- Status rules:
  - feasible incumbent, finite dual and gap ≤ 0.01 L → `CERTIFIED_TIGHT`;
  - finite dual with gap > 0.01 L, or with no incumbent → `LOWER_BOUND_AVAILABLE`, not tight-certified;
  - no finite dual → `BLOCKED_NO_DUAL`;
  - no feasible incumbent and no finite dual → `BLOCKED_NO_FEASIBLE_INCUMBENT`.
- A non-finite value is never fabricated or retained. The solver path does not manufacture `-inf`.

**K8. Aggregation.**
- The aggregate mathematical lower bound is `L = Σ_o d_o`, the sum of all finite valid per-origin dual bounds.
- An origin without a finite dual contributes zero as a conservative convention. It is explicitly counted as `BLOCKED_NO_DUAL`.
- Unproven analytic per-origin bounds are not used.
- Primal objectives are never used as lower bounds.
- An aggregate is not declared decision-complete unless every contribution NG7 requires is available and the inequality of K5 can be evaluated.

**K9. Rolling ORACLE-PHYS.** The rolling 24-hour perfect-foresight controller is an achievability benchmark. It is not a lower bound and cannot independently trigger NG7.

**K10. SOC margin.** The existing 2 Wh governance margin is kept. The physical formulation is not changed because of the executor clamp. The clamp is analytically inactive, since the charge and discharge limits already enforce the bounds.

## 3. Explicit statements

- **Lower-bound validity is not tight certification.** A finite valid dual is a valid lower bound even when its primal–dual gap exceeds 0.01 L.
- **Finite duals may contribute despite a gap above 0.01 L.** They enter `L` under K8.
- **No-dual origins are blocked.** They contribute zero under the conservative convention and are reported as `BLOCKED_NO_DUAL`.
- **No real run has occurred.** No real origin, no ORACLE-PHYS, no ORACLE-CTRL, and no Planner-CF campaign has been executed.

## 4. Non-admissions and unchanged items

- **Class B (equal-objective planner curtailment ties): not admitted.** This record does not admit them. G1 is unchanged.
- **Class C (terminal-hour fuel-boundary rows): not resolved.** The lower bound's relaxation of fuel inventory is not a resolution for the rolling benchmark, which keeps inventory.
- **G1: unchanged.** G1 still fails under the exact planned-charge rule.
- **Planner-CF formulation: unchanged.**
- **Production and frozen artifacts: unchanged.**

## 5. Rationale

- A finite dual is a valid lower bound regardless of its gap. The 0.01 L threshold controls how informative a non-trigger is, not whether a trigger is valid.
- Keeping a finite dual without an incumbent adds information without adding risk, since HiGHS reports `-inf` when no finite bound exists.
- The conservative aggregation uses only quantities that are mathematically valid. It does not invent a rule to make NG7 decidable.

## 6. Effect on certification and NG7

- **Certification:** only `CERTIFIED_TIGHT` produces `certification == "CERTIFIED"`. Every other status is `BLOCKED` for tight certification, but its valid lower bound is kept.
- **NG7:** not evaluable. It needs `F_c`, which requires the Planner-CF campaign. Until then no NG7 conclusion is drawn.

## 7. Authorization

This record does not authorize the real 123-origin lower-bound run. That run needs a separate explicit authorization, and its input and population hashes are frozen only immediately before it.

**Production promotion: none follows from this record.**
