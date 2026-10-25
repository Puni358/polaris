# POLARIS — PHASE A + PHASE B + PHASE C-1 + PHASE C-2 SCIENTIFIC SYNTHESIS CHECKPOINT

**Date (UTC):** 2026-09-16 01:01:02+0000  
**Governance Status:** CONSOLIDATED SCIENTIFIC SYNTHESIS CHECKPOINT (ABC2)  
**Phases A, B, C-1, C-2 Status:** COMPLETE AND FROZEN  
**Phase C-3 Status:** NOT AUTHORIZED  
**ODD Status:** SEALED (0 rows accessed)  

---

## 1. Executive Summary & Governance Record

This document provides the consolidated, forensically audited scientific synthesis checkpoint spanning **Phase A** (Information Probe), **Phase B** (Local Causal-State Diagnostics), **Phase C-1** (Horizon-Decomposed Transmission Diagnostic), and **Phase C-2** (Frozen P1 Physical SW_IN Diagnostic).

- **Phase A:** COMPLETE + FORENSICALLY AUDITED (Frozen)  
- **Phase B:** COMPLETE + FORENSICALLY AUDITED (Frozen)  
- **Phase C-1:** COMPLETE + FORENSICALLY AUDITED (Authoritative Corrected Execution, Frozen)  
- **Phase C-2:** COMPLETE + FORENSICALLY AUDITED (Authoritative Execution, Frozen)  
- **ODD Firewall:** SEALED (0 rows accessed)  
- **Phase C-3 Authorization:** NOT AUTHORIZED  

---

## 2. Phase Summaries & Established Results

### Phase A — Information Probe
- **Population:** 104 eligible EVEN origins (604 daytime hours evaluated).
- **Inputs:** $P0$ (22 features) vs $P1$ (147 features).
- **Results:** $T1$ Volatility ($\Delta R^2 = +0.3098$, CI $[+0.0506, +0.5886]$), $T2$ Max Transition ($\Delta R^2 = +0.3052$, CI $[+0.0470, +0.5837]$), $T3$ Mean Transmission ($\Delta R^2 = +0.5988$, CI $[+0.3639, +0.8421]$), $T4$ Dropped/Unavailable.
- **Finding:** *M1 (information absent) is inconsistent with tested aggregate targets T1–T3. Frozen P1 contains nonlinear predictive information for aggregate future transmission statistics beyond P0.*

### Phase B — Local Causal-State Diagnostics
- **B1 Rank Diagnostic:** Champion point forecasts concentrate near the 5-neighbour local median (mean normalized rank $0.4459$, raw $2.2219/5$).
- **B2 Pinball Loss:** Champion $q=0.5$ loss ($0.1058$) is lower than crude 5-neighbour empirical median loss ($0.1267$, $\Delta = +0.0209$). *Dependence Caveat:* Reported $p < 0.0001$ treated 604 hourly observations as independent without origin clustering.
- **B3 Procedural Compromise:** B3 threshold was NOT frozen before computation. B3 is procedurally compromised and remains exploratory only.

### Phase C-1 — Horizon-Decomposed Transmission Diagnostic
- **Initial Execution:** Invalidated due to canonical fold indexing loop mismatch (`range(5)` vs 1-indexed folds 1..5). Preserved as historical invalid artifact (`PHASE_C1_HORIZON_DIAGNOSTIC.json`).
- **Authoritative Corrected Execution:** Separately authorized, executed via `scratch/run_phase_c1_horizon_diagnostic_corrected.py`, and forensically audited with PASS status (104 parent origins, 609 valid target cells).
- **Results ($k(t+h)$ GBDT $\Delta R^2$):** H7 ($+0.5146$), H8 ($+0.5317$), H9 ($+0.7013$), H10 ($+0.4718$), H11 ($+0.6373$), H12 ($+0.3037$). All 95% CIs exclude 0, permutation $p = 0.0010$ at all horizons.
- **Finding:** *Frozen P1 contains extractable predictive information for individual hourly transmission targets k(t+h) beyond P0.*

### Phase C-2 — Frozen P1 Physical SW_IN Diagnostic
- **Authoritative Execution:** Executed via `scratch/run_phase_c2_frozen_p1_physical_sw_in_diagnostic.py`, forensically audited with PASS status (15/15 checks).
- **Population & Targets:** 104 parent origins, 609 valid daytime target cells, physical $SW\_IN(t+h)$ in $\text{W/m}^2$.
- **Readout Specification:** $P0$ (22 features) vs $P1$ (147 features), GBDT (`max_depth=3`, `max_iter=200`, `learning_rate=0.05`, `min_samples_leaf=10`, `random_state=42`), canonical 5-fold OOF.
- **Results (Physical $SW\_IN$ $\Delta MAE$ in $\text{W/m}^2$):**
  - **H7:** $P0 \text{ MAE} = 77.82$, $P1 \text{ MAE} = 58.31$, $\Delta MAE = \mathbf{+19.51 \text{ W/m}^2}$, 95% Bootstrap CI $[+5.28, +34.05]$, $\Delta R^2 = +0.3203$
  - **H8:** $P0 \text{ MAE} = 96.34$, $P1 \text{ MAE} = 61.22$, $\Delta MAE = \mathbf{+35.12 \text{ W/m}^2}$, 95% Bootstrap CI $[+20.96, +49.89]$, $\Delta R^2 = +0.4858$
  - **H9:** $P0 \text{ MAE} = 111.58$, $P1 \text{ MAE} = 74.91$, $\Delta MAE = \mathbf{+36.67 \text{ W/m}^2}$, 95% Bootstrap CI $[+19.56, +53.99]$, $\Delta R^2 = +0.4435$
  - **H10:** $P0 \text{ MAE} = 123.02$, $P1 \text{ MAE} = 91.74$, $\Delta MAE = \mathbf{+31.28 \text{ W/m}^2}$, 95% Bootstrap CI $[+12.21, +50.69]$, $\Delta R^2 = +0.3627$
  - **H11:** $P0 \text{ MAE} = 147.25$, $P1 \text{ MAE} = 84.19$, $\Delta MAE = \mathbf{+63.05 \text{ W/m}^2}$, 95% Bootstrap CI $[+44.24, +82.09]$, $\Delta R^2 = +0.6550$
  - **H12:** $P0 \text{ MAE} = 137.18$, $P1 \text{ MAE} = 93.20$, $\Delta MAE = \mathbf{+43.99 \text{ W/m}^2}$, 95% Bootstrap CI $[+25.28, +62.79]$, $\Delta R^2 = +0.3782$
- **Inference & Audit:** 10,000 origin-level paired block bootstrap resamples, ordinary percentile CIs, 0 degenerate replicates. Permutation test removed due to statistical incoherence. Forensic audit **PASS**.

---

## 3. Comprehensive Scientific Evidence Matrix

| Phase | Scientific Question | Data / Population | Main Result | What is DEMONSTRATED | What is SUPPORTED / CONSISTENT WITH | What remains NOT ESTABLISHED | Governance Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **Phase A** | Does frozen P1 contain incremental predictive info for aggregate future transmission statistics beyond P0? | 104 EVEN origins (604 daytime hours) | GBDT ΔR² = +0.305 to +0.599 across T1-T3 (p < 0.0001) | P1 contains substantial nonlinear predictive info for aggregate future transmission statistics. | Inconsistent with M1 (information absent) for tested aggregate targets. | M2, M3, event timing, or Stage8.1 hourly error cause. | **FROZEN** |
| **Phase B** | Are Stage8.1 point predictions positioned central to local causal state neighbours? | 104 EVEN origins (604 daytime hours) | Normalized rank = 0.4459; Pinball loss Δ = +0.0209 (p < 0.0001, unclustered) | Champion point forecasts concentrate near 5-neighbour local median. | Consistent with conditional-median / hedging behavior under L1/pinball loss. | Proof of M3, proof of event timing, or B3 threshold validation (B3 compromised). | **FROZEN** |
| **Phase C-1** | Does frozen P1 provide incremental OOF predictive info for individual transmission targets k(t+h) beyond P0? | 104 EVEN origins (609 valid target cells) | GBDT ΔR² = +0.3037 to +0.7013 (p = 0.0010 at all horizons) | Frozen P1 contains extractable predictive info for individual hourly transmission targets k(t+h). | Inconsistent with M1 for individual transmission targets. | Stage8.1 representation inadequacy, head failure, M2, M3, timing, or physical SW_IN MAE reduction. | **FROZEN** |
| **Phase C-2** | Can a downstream readout on frozen P1 extract predictive info for physical SW_IN(t+h) beyond P0? | 104 EVEN origins (609 valid target cells) | GBDT ΔMAE = +19.51 to +63.05 W/m² (all 95% CIs exclude 0) | Frozen P1 contains extractable predictive info for physical SW_IN(t+h) beyond P0 under the specified GBDT readout. | Information demonstrated in C-1 for k(t+h) transfers into physical irradiance prediction. | Stage8.1 representation failure, head failure, loss failure, M2, M3, timing, or ODD performance. | **FROZEN** |

---

## 4. Evidence Chain Synthesis

1. **Phase A:** Established that frozen $P1$ contains nonlinear predictive information about aggregate future transmission statistics ($T1$–$T3$) beyond deterministic $P0$.
2. **Phase B:** Showed local causal-state diagnostics consistent with central positioning / conditional-median hedging under L1/pinball loss, but did not prove M3 or event timing.
3. **Phase C-1:** Demonstrated that the specified GBDT probe extracts incremental out-of-fold predictive information for individual normalized transmission targets $k(t+h)$ from $P1$ beyond $P0$.
4. **Phase C-2:** Demonstrated that the specified downstream GBDT readout also extracts incremental out-of-fold predictive information for physical surface solar irradiance $SW\_IN(t+h)$ from $P1$ beyond $P0$, achieving positive $\Delta MAE$ ($+19.51 \text{ to } +63.05 \text{ W/m}^2$) across all six horizons with bootstrap 95% CIs strictly excluding zero.

---

## 5. Critical Scientific Boundary & Firewall Statements

Phase C-2 demonstrates extractable physical $SW\_IN$ information in frozen $P1$ under the specified downstream GBDT readout.

It does **NOT** establish:
- Stage8.1 representation failure
- Stage8.1 readout head failure
- Loss-function failure
- Capacity limitations
- M2 (Model-Utilization Limitation)
- M3 (Point-Loss / Uncertainty Limitation)
- Event-timing uncertainty
- Out-of-distribution (ODD) performance improvements
- Superiority of any model on the official ODD benchmark

> **Direct Stage8.1 OOF Comparison Limitation:** Direct paired OOF comparison with Stage8.1 remains unavailable under existing frozen artifacts because no exact valid frozen Stage8.1 canonical GroupKFold OOF prediction artifact exists. Reconstruction is strictly prohibited.

---

## 6. The Resulting Scientific Question

The unresolved problem is no longer whether frozen $P1$ contains useful extractable predictive information (Phase A, C-1, and C-2 establish that it does).

The unresolved problem is **WHICH MECHANISM** explains why that information has not been demonstrated through the existing Stage8.1 forecasting system itself.

M2, M3, and event timing remain competing, unproven hypotheses. No hypothesis is selected or ranked as the explanation prior to explicit mechanistic discrimination.

---

## 7. Artifact Integrity & SHA-256 Provenance

### Authoritative Frozen Artifacts
| Artifact File | Description | SHA-256 Hash |
| :--- | :--- | :--- |
| `STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv` | Frozen Canonical Fold Assignments | `0cfc8002e6bf0e8ad11d9ec9832b45a1f085c9d435934a24a3c4edb6b51d62ad` |
| `INFORMATION_PROBE_ELIGIBLE_EVEN_ORIGINS.csv` | Frozen Eligible EVEN Origins | `d2beca0747bfe18a4541bdfc664afcd9e9af838f324ecbf586fbec82ea4da88e` |
| `PHASE_C1_HORIZON_DIAGNOSTIC_CORRECTED.json` | Authoritative Corrected C-1 Results (JSON) | `0e81f0051f04140b059c29e0ffef914d58404dd16259c4118eb0440e7ca52fb9` |
| `PHASE_C1_HORIZON_DIAGNOSTIC_CORRECTED.md` | Authoritative Corrected C-1 Results (MD) | `bd4efea996c8d436d60df543aeca5006960d148c085f6ec1bbb4f4c131689fb3` |
| `PHASE_C1_FORENSIC_INTEGRITY_AUDIT_CORRECTED.json` | Authoritative Corrected C-1 Audit (JSON) | `da9efe62360d5d3cb96fcfa69eee5a1e9d6afe63ed10a5228acbbffee35da35e` |
| `PHASE_C1_FORENSIC_INTEGRITY_AUDIT_CORRECTED.md` | Authoritative Corrected C-1 Audit (MD) | `d83ed20ae406398391e97850efec34f76e44a9aec13e7c30b92f407fe7047e9d` |
| `PHASE_C1_CORRECTION_AND_CLOSEOUT.json` | C-1 Correction & Closeout Record (JSON) | `c292e0150e3fad00b4c3c20e2eca43cc391aabb5170c5b3db2af4ce06d5dc32f` |
| `PHASE_C1_CORRECTION_AND_CLOSEOUT.md` | C-1 Correction & Closeout Record (MD) | `6e192e88da0e4b39667da4ea83d32e8f2d79c99087698b9a015edb1c1bf2e3b7` |
| `PHASE_C2_FROZEN_P1_PHYSICAL_SW_IN_DIAGNOSTIC.json` | Authoritative C-2 Results (JSON) | `4db3461ab6296afa644bfa466de639017c47fbfda66d88323c1d77f1ff5417ed` |
| `PHASE_C2_FROZEN_P1_PHYSICAL_SW_IN_DIAGNOSTIC.md` | Authoritative C-2 Results (MD) | `743ace7c386bd43646b14b67adf8a02a1841b5bb93f4b8131a1ba1e4f4bd863f` |
| `PHASE_C2_FORENSIC_INTEGRITY_AUDIT.json` | Authoritative C-2 Audit (JSON) | `4990db86221f5893e7fbad18122d03b51aed5c344bed1e6d15e310c8afd01bbd` |
| `PHASE_C2_FORENSIC_INTEGRITY_AUDIT.md` | Authoritative C-2 Audit (MD) | `34b98ae9a2bb3d6d1b6938588a23c7c1dcd439d33e6a64d3fb85d99c09bc85f5` |

### Historical Invalid Artifacts (Preserved Strictly for Auditability)
| Artifact File | Description | SHA-256 Hash |
| :--- | :--- | :--- |
| `PHASE_C1_HORIZON_DIAGNOSTIC.json` | Initial Invalid C-1 Results (Range(5) loop defect) | `6becb0e21567f3f4c86525a2105ce6cad84ee3fc2021ce16cce0a06f5a567c23` |
| `PHASE_C1_HORIZON_DIAGNOSTIC.md` | Initial Invalid C-1 Report | `98a22c27b7717f2b9af91b41c8bdc64ec044cfb3af30dc2a51ebbccf1298c619` |
| `PHASE_C1_FORENSIC_INTEGRITY_AUDIT.json` | Initial Invalid C-1 Audit | `52b5b97fa31f6b8c9faba0861485ae4e78b145add164c5fc34848c9f3650ed5a` |
| `PHASE_C1_FORENSIC_INTEGRITY_AUDIT.md` | Initial Invalid C-1 Audit Report | `3cd44c7eeff9e8e2ff7c9e24708219708a57c1f80a6e2030c3aa64112781d0f9` |

---

## 8. Next-Step Governance

- **Phase A:** FROZEN / CLOSED  
- **Phase B:** FROZEN / CLOSED  
- **Phase C-1:** FROZEN / CLOSED  
- **Phase C-2:** FROZEN / CLOSED  
- **Phase C-3 Authorization:** NOT AUTHORIZED  
- **ODD Firewall:** SEALED (0 rows accessed)  

1. No follow-up experiment is automatically authorized.
2. The ODD firewall remains 100% absolute.
3. Any future scientific experiment requires a separate pre-registered design and explicit human authorization.
4. Future work must focus on discriminating a specific mechanism rather than performing generic model or feature experimentation.

---

POLARIS PHASE A + PHASE B + PHASE C-1 + PHASE C-2 SYNTHESIS COMPLETE.
NO SECONDARY ANALYSIS AUTHORIZED.
ODD REMAINS SEALED.
