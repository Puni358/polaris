# POLARIS — INFORMATION PROBE FREEZE RECORD

**Date (UTC):** 2026-09-16T04:57:41Z  
**Status:** EXPERIMENT FROZEN PRIOR TO TARGET COMPUTATION  
**Preregistration Target:** `newhope/POLARIS_INFORMATION_PROBE_PREREGISTRATION.md`  

---

## 1. Cryptographic Hashes & Provenance

| Artifact | File Path | SHA-256 Hash |
| :--- | :--- | :--- |
| **Preregistration Document** | `newhope/POLARIS_INFORMATION_PROBE_PREREGISTRATION.md` | `f414b176bd0dec6a6abd4551df625120e99d095223595bf56b1295b2669a5f4d` |
| **Canonical Fold Assignment** | `STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv` | `0cfc8002e6bf0e8ad11d9ec9832b45a1f085c9d435934a24a3c4edb6b51d62ad` |
| **Preflight Audit Document** | `INFORMATION_PROBE_PREFLIGHT_AUDIT.md` | `9b5b292e10c57c239bd010915f0eb11a511855a882a89dfcdd4dfd1df36d7a4c` |

---

## 2. Reconciled Governance & Hit Criterion Rules

- **Original formal hit criterion:** At least 2 of 4 targets individually satisfy $\Delta R^2 \ge 0.03$ AND bootstrap 95% CI excludes zero.
- **T4 is unavailable/dropped** because genuine matching-fold Stage 8.1 EVEN OOF predictions cannot be reconstructed.
- **T1, T2, and T3 remain active** and may be computed and reported descriptively/inferentially.
- **With T4 unavailable, the original 2-of-4 formal hit criterion cannot be satisfied using only T1–T3.**
- **Do NOT declare a formal Section 9 hit based on 2 of 3 targets.**
- **Do NOT silently modify the decision rule.**
- Any future change to the formal decision rule would require an explicit methodological amendment made before inspecting target results.

---

## 3. Canonical Fold Assignment Specifications

- **Total EVEN origins assigned:** 174
- **Fold assignment scheme:** `sklearn.model_selection.GroupKFold(n_splits=5)` grouped by `forecast_start` across all EVEN origins prior to eligibility filtering.
- **Fold sizes:**
  - Fold 1: 35 origins
  - Fold 2: 35 origins
  - Fold 3: 35 origins
  - Fold 4: 35 origins
  - Fold 5: 34 origins
- **Polar-night handling:** Excluded origins retain their assigned fold label (1..5) but drop at eligibility evaluation.

---

## 4. Operational Boundaries

- **Target computation status:** NOT COMPUTED (0 targets)
- **Model fitting status:** NOT FITTED (0 models)
- **ODD access status:** ZERO ACCESS (0 rows)
- **Phase B status:** PENDING APPROVAL
- **Phase C status:** BLOCKED
