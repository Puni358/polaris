# POLARIS — POST-ABC2 MECHANISM IDENTIFICATION LIMIT CHECKPOINT & SCIENTIFIC CLOSEOUT

**Date (UTC):** 2026-09-16 01:12:55+0000  
**Governance Status:** FINAL SCIENTIFIC CLOSEOUT & IDENTIFICATION LIMIT CHECKPOINT  
**Phases A, B, C-1, C-2 Status:** COMPLETE, FORENSICALLY AUDITED, AND FROZEN  
**C-3 Status:** REJECTED AS NON-IDENTIFYING / NOT AUTHORIZED  
**ODD Status:** SEALED (0 rows accessed)  

---

## 1. Final Scientific State: Signal Existence vs. Mechanism Identification

The POLARIS research project has established a rigorous, forensically audited evidence chain across four completed phases:

- **Phase A:** $P1 \to \text{GBDT} \to \text{Aggregate Future Transmission } (T1, T2, T3)$
  - *Result:* Demonstrated nonlinear predictive information in $P1$ beyond $P0$ ($p < 0.0001$).
- **Phase C-1:** $P1 \to \text{GBDT} \to k(t+h) \text{ Transmission Index } (H7\text{--}H12)$
  - *Result:* Demonstrated incremental out-of-fold predictive information for individual transmission targets ($p = 0.0010$).
- **Phase C-2:** $P1 \to \text{GBDT} \to \text{Physical } SW\_IN(t+h) \text{ Irradiance } (H7\text{--}H12)$
  - *Result:* Demonstrated incremental out-of-fold predictive information for physical irradiance across all six horizons ($\Delta MAE = +19.51 \text{ to } +63.05 \text{ W/m}^2$, all 95% CIs exclude 0).

> **Authoritative Core Finding:** *Useful predictive information exists in the frozen P1 causal state and is extractable under the specified downstream GBDT readout for both normalized transmission and physical surface irradiance.*

### Critical Distinction
$$\text{Signal Existence / Extractability} \quad \neq \quad \text{Mechanism Identification}$$

The evidence proves that $P1$ contains extractable predictive information, but it **does NOT identify the mechanism** explaining why that information was not previously demonstrated through the Stage8.1 forecasting system itself.

---

## 2. What ABC2 Does NOT Identify

The successful GBDT probe results in Phase C-1 and C-2 do **NOT** establish:
- Stage8.1 representation failure
- Stage8.1 readout-head failure
- Loss-function failure
- Capacity limitations
- **M2** (Model/Readout Utilization Limitation)
- **M3** (Point-Estimation / Uncertainty Limitation)
- **Event-Timing Uncertainty** as the cause of Stage8.1's performance gap
- Superiority on the official Out-of-Distribution (ODD) benchmark

The GBDT probes and Stage8.1 are distinct modeling systems with different architectures, objectives, losses, optimization procedures, and training dynamics. Probe extractability cannot be converted into a claim of Stage8.1 architectural failure.

---

## 3. Signal Existence $\neq$ Mechanism Identification

$$\text{P1 contains info} \implies \text{GBDT extracts info} \implies \text{Info transfers to physical } SW\_IN \implies \mathbf{Mechanism \, Unidentified}$$

The competing candidate mechanisms remain:
1. **M2 — Model / Readout Utilization Limitation:** Downstream head, loss, or optimization under-extracts represented state info.
2. **M3 — Point-Estimation / Uncertainty Limitation:** Distributional/hedging dynamics under L1 loss obscure expected point error reduction.
3. **Event-Timing Uncertainty:** Cloud transition timing phase noise limits instantaneous 1-hour point error reduction.

None of these hypotheses are ranked, selected, or proven under the current evidence.

---

## 4. Rejection of C-3 Temporal Aggregation & Direct Timing Probes

### C-3 Temporal Aggregation Rejection
The proposed *Temporal Window Aggregation Diagnostic* is formally **REJECTED AS NON-IDENTIFYING**. Target aggregation changes regression difficulty, target variance, and signal-to-noise ratio. Both M2 and Event-Timing Uncertainty predict greater relative improvement on aggregated targets; therefore, temporal aggregation cannot uniquely discriminate between them.

### Direct Timing Target Audit Rejection
Direct timing targets (e.g., $h^* = \text{argmin}_h k(t+h)$) evaluate whether transition timing is extractable from $P1$. However, successful or unsuccessful timing prediction does not establish whether timing uncertainty was the causal mechanism responsible for Stage8.1's point forecast gap.

---

## 5. Precise Identification-Limit Statement

> **"Direct observational discrimination among M2 (Model/Readout Utilization), M3 (Point-Loss/Uncertainty), and Event-Timing Uncertainty is not identifiable under the current frozen POLARIS artifacts, protocols, and permitted information sources."**

*Note: This statement defines a limitation of the current frozen artifacts and protocols. It does not make an unproven universal claim about all conceivable future experiments under potential future governance amendments.*

---

## 6. Hard Limitation: Missing Stage8.1 OOF Artifact

The official Stage8.1 champion model was fit on all 174 EVEN origins and lacks an exact valid 5-fold canonical GroupKFold EVEN OOF prediction artifact.
- Direct paired Stage8.1 OOF comparison is **unavailable**.
- Stage8.1 OOF reconstruction is **prohibited**.
- In-sample Stage8.1 predictions **cannot substitute** for OOF predictions.
- No synthetic or approximate Stage8.1 OOF artifact may be created.

---

## 7. Final Evidence Matrix

| Phase | Question | Main Result | What is DEMONSTRATED | What is SUPPORTED / CONSISTENT WITH | What remains NOT ESTABLISHED | Governance Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **Phase A** | Does frozen P1 contain incremental predictive info for aggregate future transmission statistics beyond P0? | GBDT ΔR² = +0.305 to +0.599 across T1-T3 (p < 0.0001) | P1 contains substantial nonlinear predictive info for aggregate future transmission statistics. | Inconsistent with M1 (information absent) for tested aggregate targets. | M2, M3, event timing, or Stage8.1 hourly error cause. | **FROZEN / CLOSED** |
| **Phase B** | Are Stage8.1 point predictions positioned central to local causal state neighbours? | Normalized rank = 0.4459; Pinball loss Δ = +0.0209 (p < 0.0001, unclustered) | Champion point forecasts concentrate near 5-neighbour local median. | Consistent with conditional-median / hedging behavior under L1/pinball loss. | Proof of M3, proof of event timing, or B3 threshold validation (B3 compromised). | **FROZEN / CLOSED** |
| **Phase C-1** | Does frozen P1 provide incremental OOF predictive info for individual transmission targets k(t+h) beyond P0? | GBDT ΔR² = +0.3037 to +0.7013 (p = 0.0010 at all horizons) | Frozen P1 contains extractable predictive info for individual hourly transmission targets k(t+h). | Inconsistent with M1 for individual transmission targets. | Stage8.1 representation inadequacy, head failure, M2, M3, timing, or physical SW_IN MAE reduction. | **FROZEN / CLOSED** |
| **Phase C-2** | Can a downstream readout on frozen P1 extract predictive info for physical SW_IN(t+h) beyond P0? | GBDT ΔMAE = +19.51 to +63.05 W/m² (all 95% CIs exclude 0) | Frozen P1 contains extractable predictive info for physical SW_IN(t+h) beyond P0 under specified GBDT readout. | Information demonstrated in C-1 for k(t+h) transfers into physical irradiance prediction. | Stage8.1 representation failure, head failure, loss failure, M2, M3, timing, or ODD performance. | **FROZEN / CLOSED** |
| **C-3 Audit** | Can M2, M3, and Event-Timing be observationally discriminated using current frozen artifacts? | Hard Identification Limit Encountered | Signal existence is proven, but mechanism discrimination is non-identifiable under current frozen artifacts. | Confirms necessity of explicit governance amendments for any future mechanism-attribution work. | Unique causal mechanism explaining Stage8.1 performance gap. | **CLOSED / REJECTED AS NON-IDENTIFYING** |

---

## 8. Final Contribution Statement

1. Systematically evaluated the solar irradiance forecasting problem under a locked, causally rigorous benchmark.
2. Evaluated candidate information sources and baseline architectures across canonical 5-fold cross-validation.
3. Demonstrated that the frozen Stage8.1 causal state P1 contains substantial extractable predictive information for aggregate transmission and individual hourly targets.
4. Showed that this predictive information is recoverable by a specified downstream GBDT readout for both normalized transmission index k(t+h) and physical surface irradiance SW_IN(t+h) (Phase C-2 ΔMAE +19.51 to +63.05 W/m²).
5. Established that available empirical evidence does NOT identify the specific mechanism (M2, M3, or Event-Timing) responsible for the performance discrepancy with the original Stage8.1 system.
6. Identified the absence of a canonical GroupKFold Stage8.1 OOF prediction artifact as a hard identification limitation for direct paired attribution.
7. Maintained 100% strict Out-of-Distribution (ODD) data isolation throughout the entire research and diagnostic program (0 rows accessed).

---

## 9. Future-Work Boundary & Closed Routes

Future work may theoretically revisit mechanism discrimination **only through a new, explicit governance amendment** that demonstrates a mathematically valid, non-confounded controlled comparison.

The following routes are **EXPLICITLY CLOSED** under current governance:
- Generic neural-network experimentation
- Arbitrary GBDT/model variants
- Feature sweeps
- Hyperparameter sweeps
- Additional spatial/NWP/satellite feature searches
- Temporal aggregation as a mechanism test
- Direct timing probes that cannot discriminate mechanisms
- Stage8.1 OOF reconstruction
- ODD experimentation

---

## 10. Authoritative Artifact Provenance & SHA-256 Hashes

### Authoritative Project Artifacts
| Artifact File | SHA-256 Hash |
| :--- | :--- |
| `STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv` | `0cfc8002e6bf0e8ad11d9ec9832b45a1f085c9d435934a24a3c4edb6b51d62ad` |
| `INFORMATION_PROBE_ELIGIBLE_EVEN_ORIGINS.csv` | `d2beca0747bfe18a4541bdfc664afcd9e9af838f324ecbf586fbec82ea4da88e` |
| `PHASE_C1_FORENSIC_INTEGRITY_AUDIT.json` | `52b5b97fa31f6b8c9faba0861485ae4e78b145add164c5fc34848c9f3650ed5a` |
| `PHASE_C1_FORENSIC_INTEGRITY_AUDIT.md` | `3cd44c7eeff9e8e2ff7c9e24708219708a57c1f80a6e2030c3aa64112781d0f9` |
| `PHASE_C1_HORIZON_DIAGNOSTIC_CORRECTED.json` | `0e81f0051f04140b059c29e0ffef914d58404dd16259c4118eb0440e7ca52fb9` |
| `PHASE_C1_HORIZON_DIAGNOSTIC_CORRECTED.md` | `bd4efea996c8d436d60df543aeca5006960d148c085f6ec1bbb4f4c131689fb3` |
| `PHASE_C1_FORENSIC_INTEGRITY_AUDIT_CORRECTED.json` | `da9efe62360d5d3cb96fcfa69eee5a1e9d6afe63ed10a5228acbbffee35da35e` |
| `PHASE_C1_FORENSIC_INTEGRITY_AUDIT_CORRECTED.md` | `d83ed20ae406398391e97850efec34f76e44a9aec13e7c30b92f407fe7047e9d` |
| `PHASE_C1_CORRECTION_AND_CLOSEOUT.json` | `c292e0150e3fad00b4c3c20e2eca43cc391aabb5170c5b3db2af4ce06d5dc32f` |
| `PHASE_C1_CORRECTION_AND_CLOSEOUT.md` | `6e192e88da0e4b39667da4ea83d32e8f2d79c99087698b9a015edb1c1bf2e3b7` |
| `PHASE_C2_FROZEN_P1_PHYSICAL_SW_IN_DIAGNOSTIC.json` | `4db3461ab6296afa644bfa466de639017c47fbfda66d88323c1d77f1ff5417ed` |
| `PHASE_C2_FROZEN_P1_PHYSICAL_SW_IN_DIAGNOSTIC.md` | `743ace7c386bd43646b14b67adf8a02a1841b5bb93f4b8131a1ba1e4f4bd863f` |
| `PHASE_C2_FORENSIC_INTEGRITY_AUDIT.json` | `4990db86221f5893e7fbad18122d03b51aed5c344bed1e6d15e310c8afd01bbd` |
| `PHASE_C2_FORENSIC_INTEGRITY_AUDIT.md` | `34b98ae9a2bb3d6d1b6938588a23c7c1dcd439d33e6a64d3fb85d99c09bc85f5` |
| `POLARIS_PHASE_ABC2_SCIENTIFIC_SYNTHESIS_CHECKPOINT.json` | `21e51c44798b8b0ca2fe243b332a42b9e51c7e0f437488c233fc46601dfd8cf0` |
| `POLARIS_PHASE_ABC2_SCIENTIFIC_SYNTHESIS_CHECKPOINT.md` | `0a9643826c80cff602b7c23c561425c880dcc1e26a46f3944eb341cbad03affe` |

### Historical Invalid Artifacts (Preserved Strictly for Auditability)
| Artifact File | SHA-256 Hash |
| :--- | :--- |
| `PHASE_C1_HORIZON_DIAGNOSTIC.json` | `6becb0e21567f3f4c86525a2105ce6cad84ee3fc2021ce16cce0a06f5a567c23` |
| `PHASE_C1_HORIZON_DIAGNOSTIC.md` | `98a22c27b7717f2b9af91b41c8bdc64ec044cfb3af30dc2a51ebbccf1298c619` |
| `PHASE_C1_FORENSIC_INTEGRITY_AUDIT.json` | `52b5b97fa31f6b8c9faba0861485ae4e78b145add164c5fc34848c9f3650ed5a` |
| `PHASE_C1_FORENSIC_INTEGRITY_AUDIT.md` | `3cd44c7eeff9e8e2ff7c9e24708219708a57c1f80a6e2030c3aa64112781d0f9` |

---

POST-ABC2 MECHANISM IDENTIFICATION LIMIT = FROZEN.
C-3 TEMPORAL AGGREGATION = REJECTED AS NON-IDENTIFYING.
NO EXPERIMENT EXECUTED.
ABC2 REMAINS FROZEN.
ODD REMAINS SEALED.
MECHANISM-DISCRIMINATION WORK = CLOSED UNDER CURRENT GOVERNANCE.
AWAITING HUMAN DECISION ON ANY FUTURE GOVERNANCE AMENDMENT.
