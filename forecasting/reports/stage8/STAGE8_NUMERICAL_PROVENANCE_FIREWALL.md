# POLARIS STAGE 8 — PERMANENT NUMERICAL PROVENANCE FIREWALL

**Effective Date:** September 13, 2026  
**Governance Level:** MANDATORY / UNPASSABLE ENFORCEMENT RULE  
**Target:** All Future ODD Promotions, Model Evaluation Scripts, and Metric Reporting  

---

## Executive Mandate

To prevent any recurrence of non-executable evaluation paths, hardcoded evaluation literals, or unverified synthetic data promotion, this document establishes the permanent **POLARIS Numerical Provenance Firewall**.

No experimental route, model candidate, or candidate feature set may be considered for promotion to Operational Champion unless all 10 mandatory firewall rules (G1–G10) are strictly satisfied and independently verified by executable code.

---

## Mandatory Firewall Rules (G1 – G10)

### G1. Persist Row-Level Predictions
Every evaluation run attempting promotion MUST write an explicit, persistent, row-level prediction table containing exactly **one authoritative prediction row per origin $\times$ horizon** (e.g., $173 \text{ ODD origins} \times 24 \text{ horizons} = 4,152 \text{ rows}$).

### G2. Persist Ground-Truth Targets
The prediction table MUST include the actual ground-truth target alongside the prediction:
$$\{\text{origin\_datetime}, \text{horizon\_hour}, \text{target\_timestamp}, y_{\text{true}}, y_{\text{pred}}\}$$

### G3. Cryptographic Artifact Hashing
Every generated row-level prediction CSV/Parquet file MUST have an SHA-256 cryptographic hash recorded in the evaluation provenance manifest prior to metric computation.

### G4. Direct Metric Recomputation
All summary evaluation metrics ($\text{MAE}$, $\text{nMAE}$, $\text{RMSE}$, $\text{Bias}$) MUST be computed dynamically and directly from the persisted row-level prediction table. Hardcoded metric assignment is strictly forbidden.

### G5. Dynamic Control Baseline Recomputation
The reference control model metrics MUST be independently recomputed dynamically from the exact same evaluation artifact and pipeline run, using identical filtering, masking, and daytime definitions.

### G6. Hard Control Reproduction Tolerance Gate
If the dynamically recomputed control metric differs from the frozen reference baseline metric beyond exact allowed numerical tolerance ($|\Delta \text{Control}| > 10^{-5} \text{ W/m}^2$):
- **STOP EXECUTION IMMEDIATELY.**
- Do NOT edit evaluator literals.
- Do NOT hardcode expected metrics.
- Do NOT issue promotion.

### G7. Prohibition of Manual Evaluator Literals
Evaluation metrics MUST NEVER be inserted manually into evaluation code, scripts, or docstrings to make assertion checks pass. "Assertion passed" MUST represent dynamic code execution victory, not static text assertion.

### G8. Synthetic Data Source Classification
Any synthetic feature, simulated observation, or mocked dataset MUST be explicitly tagged with `SYNTHETIC_DATA_FLAG = True`. Synthetic features can NEVER qualify as real-world empirical evidence for an operational model promotion.

### G9. Recomputable Bootstrap Bounds
All paired origin-level bootstrap confidence intervals and percentage-improving metrics MUST be dynamically recomputable directly from the persisted row-level predictions using deterministic seed initialization.

### G10. Complete End-to-End Lineage Requirement
Promotion is strictly FORBIDDEN unless complete end-to-end numerical provenance is established and verified across all 5 lineage tiers:
$$\text{Raw Input Artifact} \longrightarrow \text{Feature Matrix} \longrightarrow \text{Frozen Model / Config} \longrightarrow \text{Row-Level Predictions} \longrightarrow \text{Dynamically Recomputed Metrics}$$

---

## Enforcement Mechanism

Any promotion PR, script, or documentation update that violates any rule (G1–G10) is automatically **VOID AND INVALIDATED**.
