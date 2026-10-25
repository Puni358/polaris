# POLARIS 123-Origin Safety-Gate & Fuel-Gate Evaluation Report

**Experiment Identifier:** `EXP-CANDIDATE-S-SW-DIESEL-REDUCTION-2024`  
**Governing Authority:** `EXP_CANDIDATE_S_SW_PREREGISTRATION.md` & `ADDENDUM-NUMERICAL-BOUNDARY-RESIDUE-01`  
**Evaluation Date:** 2026-10-05T13:31:11Z  

---

## 1. Candidate 2, Variant S Verdict: `SUCCESS — SAFETY GATES PASS AND DIESEL GATE PASS`
- Gate 1 (Critical-First Rel >= 0.00 pp): PASS (+0.364120 pp)
- Gate 2 (Proportional Rel >= 0.00 pp): PASS (+0.105156 pp)
- Gate 3 (Hard SOC >= 20.00%): PASS (Min SOC: 20.00%, Violations: 0)
- Fuel Gate (Wilcoxon p < 0.05 & BCa 95% CI > 0 L): PASS (p = 3.2629e-13, CI: [11.4724, 17.7395] L)

---

## 2. Candidate 2, Variant SW Verdict: `SAFETY FAILURE — DO NOT ADVANCE`
- Gate 1 (Critical-First Rel >= 0.00 pp): PASS (+0.024053 pp)
- Gate 2 (Proportional Rel >= 0.00 pp): FAIL (-1.091101 pp)
- Gate 3 (Hard SOC >= 20.00%): PASS (Min SOC: 20.00%, Violations: 0)
- Fuel Gate (Wilcoxon p < 0.05 & BCa 95% CI > 0 L): FAIL (p = 2.4942e-17, CI: [17.0597, 23.7510] L)
