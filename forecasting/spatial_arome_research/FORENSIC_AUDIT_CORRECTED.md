# FORENSIC AUDIT: CORRECTED FINDINGS
## Retracting Overconfident Causal Claims

**Date:** September 2026  
**Status:** Stress-tested and corrected  
**Scope:** Diagnostic investigation only (no training, no model changes)

---

## CRITICAL CORRECTION

My previous forensic report made **overconfident causal attributions** without proper quantification. This corrected version retracts those claims and provides a more honest assessment.

---

## WHAT WAS WRONG WITH THE PREVIOUS REPORT

### Previous Claim 1: "~4-5 W/m² from H9-H12 Regime"
**Classification (Before):** CONFIRMED  
**Classification (Now):** PLAUSIBLE but UNQUANTIFIED

**The Problem:**
- I showed: EVEN has 9.7 W/m² higher irradiance in H9-H12
- I claimed: This explains 4-5 W/m² of the 9.82 W/m² gap
- **Logical error:** Higher irradiance does NOT automatically make absolute MAE lower
  - If model error rate is constant, higher magnitude targets yield higher absolute errors
  - If model error rate is BETTER on higher-signal regimes, then maybe lower MAE
  - I showed ODD's model has 27.3% error in H9-H12 vs 29.4% rest
  - This suggests the model actually performs BETTER on H9-H12 (lower % error)
  - Therefore: even if EVEN has slightly higher H9-H12 irradiance, absolute MAE might be HIGHER not lower

**What Would be Needed:**
1. Evaluate the SAME model on both EVEN and ODD
2. Compute error rates (not just absolute MAE)
3. Show that regime distribution difference yields 4-5 W/m² gap
4. I have not done this rigorously

**Corrected Assessment:** The regime difference is REAL and PLAUSIBLE as a contributor, but the magnitude (~4-5 W/m²) is SPECULATIVE without proper quantification.

---

### Previous Claim 2: "~2-3 W/m² from Cloud Distribution"
**Classification (Before):** CONFIRMED  
**Classification (Now):** PLAUSIBLE but UNQUANTIFIED

**The Problem:**
- I showed: ODD has 3.3% higher cloud cover (statistically significant, p<0.001)
- I claimed: This contributes 2-3 W/m² to the gap
- **Logical error:** Statistical significance of a difference ≠ quantified causal impact
  - I did NOT segment EVEN and ODD by cloud regimes
  - I did NOT compute error rate differences within clear vs cloudy subsets
  - I did NOT weight by distribution mismatch
  - I merely observed that cloud cover differs

**What Would be Needed:**
1. Compute error rate (or MAE) for both EVEN and ODD within same cloud bins
2. Show that error changes with cloud cover at similar rate in both
3. Then compute: Σ(error_EVEN(cloud_i) - error_ODD(cloud_i)) * P(distribution mismatch)
4. I have not done this rigorously

**Corrected Assessment:** Higher cloud cover in ODD is plausible to increase error, but the magnitude (2-3 W/m²) is UNQUANTIFIED.

---

### Previous Claim 3: "~1-2 W/m² from Reconstruction Variance"
**Classification (Before):** PLAUSIBLE  
**Classification (Now):** UNRESOLVED

**The Discrepancy:**
- Phase 10 checkpoint reports: 26.3668 W/m² (EVEN control)
- My independent reconstruction: 24.7820 W/m² (1.58 W/m² better)

**Investigation:**
- Phase 10 states: "default hyperparameters (no sweep)"
- Phase 10 does NOT provide exact hyperparameter values
- My reconstruction likely used different defaults
- sklearn HGB is stochastic → random seed matters

**Why This is Unresolved:**
- I cannot explain the 1.58 W/m² difference from available artifacts
- Possible causes: random seed, hyperparameter defaults, sklearn version, stopping criteria
- **Artifact does not specify the exact hyperparameters used**

**Recommendation:** Use Phase 10's reported 26.3668 W/m² as the official EVEN control. The 1.58 W/m² discrepancy is UNRESOLVED and should not be used in attributions.

---

### Previous Claim 4: "The Gap is Explained"
**Classification (Before):** CONFIRMED  
**Classification (Now):** PARTIALLY EXPLAINED, NOT FULLY QUANTIFIED

**The Fundamental Problem:**
```
Gap = Official_Stage8_1(ODD=36.19) - Reconstructed_HGB(EVEN=26.37) = 9.82 W/m²

To explain this gap, I need to isolate:
  A) Regime contribution (data differences between EVEN and ODD)
  B) Algorithm contribution (differences in model architecture/training)

But I have TWO DIFFERENT MODELS:
  - Original Stage 8.1 (code unavailable, trained on unknown data, deployed on ODD)
  - Reconstructed HGB (different hyperparameters, trained on EVEN, not evaluated on ODD)

To isolate regime effect, I would need ONE of:
  ✗ Original_Stage8_1(EVEN) vs Original_Stage8_1(ODD)  → Original code unavailable
  ✗ Reconstructed_HGB(EVEN) vs Reconstructed_HGB(ODD) → Would use ODD for development (prohibited)
```

**What I Actually Showed:**
- EVEN and ODD have different data distributions (cloud, irradiance)
- These differences are PLAUSIBLE contributors to gap
- But the MAGNITUDE cannot be rigorously quantified from available data

**Corrected Assessment:** The gap is PARTIALLY EXPLAINED by plausible mechanisms (regime differences, possible algorithm differences), but a complete quantified decomposition is NOT POSSIBLE from the available artifacts without violating the development/test boundary.

---

## CORRECTED FINDINGS BY AUDIT DIMENSION

### ✓ Confirmed (No Change)
| # | Finding | Status | Confidence |
|---|---|---|---|
| 1 | No leakage to EVEN | CONFIRMED | High |
| 2 | ODD properly firewalled | CONFIRMED | High |
| 3 | Folds group by origin (0 mismatches) | CONFIRMED | High |
| 4 | All features causal (no future info) | CONFIRMED | High |
| 5 | Cloud cover difference (ODD higher, p<0.001) | CONFIRMED | High |
| 6 | H9-H12 irradiance difference (EVEN higher) | CONFIRMED | High |
| 7 | Seasonal distribution equivalent (p=0.91) | CONFIRMED | High |
| 8 | Day/night fraction equivalent | CONFIRMED | High |
| 9 | Temperature/humidity distributions equivalent (p>0.36) | CONFIRMED | High |
| 10 | Gap is real and measured (9.82 W/m²) | CONFIRMED | High |

### ⊗ Retracted (Over-Confident)
| # | Previous Claim | New Classification | Reason |
|---|---|---|---|
| 1 | "~4-5 W/m² from H9-H12 regime" | PLAUSIBLE but UNQUANTIFIED | Showed correlation, not causal mechanism |
| 2 | "~2-3 W/m² from cloud distribution" | PLAUSIBLE but UNQUANTIFIED | Showed difference, not error impact |
| 3 | "~1-2 W/m² from reconstruction variance" | UNRESOLVED | Cannot explain 1.58 W/m² discrepancy from artifacts |
| 4 | "The gap is explained" | PARTIALLY EXPLAINED | Regime is plausible but not quantified |

### ? Unresolved (Need More Data)
| # | Question | Status | Why |
|---|---|---|---|
| 1 | What is the exact regime contribution? | UNRESOLVED | Cannot evaluate same model on both splits |
| 2 | What is the exact algorithm contribution? | UNRESOLVED | Original Stage 8.1 code unavailable |
| 3 | Why is 26.3668 ≠ 24.7820? | UNRESOLVED | Exact hyperparameters not specified |
| 4 | Will EVEN candidates perform 10 W/m² worse on ODD? | UNRESOLVED | Depends on regime contribution (unquantified) |

---

## CORRECTED ANSWERS TO CORE QUESTIONS

### A. Is the 9.82 W/m² gap genuinely explained?

**Answer: PARTIALLY, NOT FULLY**

**What is established:**
- ✓ Gap is REAL and MEASURED
- ✓ EVEN and ODD have different data distributions
- ✓ These differences are PLAUSIBLE contributors to gap
- ✓ No leakage or fraud detected

**What is NOT established:**
- ✗ Quantified causal contribution of each factor
- ✗ Whether regime difference explains most, half, or little of gap
- ✗ Whether algorithm/hyperparameter differences dominate the gap

**Honest verdict:** The gap is EXPLAINED AT THE LEVEL OF PLAUSIBLE MECHANISMS, but NOT QUANTIFIED at the level needed for reliable predictions of candidate performance on ODD.

---

### B. Is 26.3668 W/m² trustworthy as the EVEN development control?

**Answer: YES, WITH IMPORTANT CAVEATS**

**What is trustworthy:**
- ✓ Properly constructed (5-fold OOF by origin)
- ✓ Leakage-safe (no ODD data)
- ✓ All features causal
- ✓ Valid for RELATIVE comparison between candidates on EVEN

**What is NOT trustworthy:**
- ✗ Direct transfer to ODD performance (gap is poorly characterized)
- ✗ Absolute performance claims without regime qualification
- ✗ The reconstruction is "approximate, not exact" (per checkpoints)

**Recommended use:**
- Use as baseline for comparing Candidates A vs B vs C on EVEN
- Do NOT claim EVEN performance will transfer to ODD
- Do NOT claim a candidate beating this by X W/m² will beat ODD champion by X W/m²

---

### C. Is the claimed ~10 W/m² EVEN→ODD penalty justified?

**Answer: NO, EXPLICITLY RETRACTED**

My previous report stated: *"Any candidate developed on EVEN will be biased toward peak-hour performance. Expect ~10 W/m² gap when moving to ODD."*

**Why this is unjustified:**
1. The 9.82 W/m² gap is MEASURED between two different models/splits
2. It is NOT proven to be a "regime penalty" specific to candidates
3. Claiming "expect ~10 W/m² worse on ODD" without proper attribution is OVERCONFIDENT
4. The gap could be entirely algorithm difference, entirely regime difference, or mixed

**Corrected claim:**
- ODD has harder conditions (more clouds, different irradiance profile)
- ODD performance is likely WORSE than EVEN gate performance
- The magnitude of this penalty is UNKNOWN (likely 5-10 W/m², but unquantified)
- Do NOT promise specific numbers

---

### D. Does the Phase 10 protocol need correction?

**Answer: NO**

**Assessment:**
- ✓ Phase 10 checkpoints are honest about reconstruction status ("approximate")
- ✓ Folds are properly constructed
- ✓ Gates (G1-G6) are appropriate for the reconstruction-level baseline
- ✓ No leakage occurred
- ✓ ODD remains firewalled

**Recommended additions (not corrections):**
- Add caveat: "The 26.3668 W/m² control represents EVEN-split performance. ODD performance is expected to be worse due to data regime differences, but the magnitude is unquantified."
- Clarify: "Gate results show relative improvement on EVEN. ODD performance cannot be predicted from EVEN gates alone."
- Document: "1.58 W/m² discrepancy between checkpoint (26.3668) and independent reconstruction (24.7820) is UNRESOLVED."

---

### E. Is it scientifically safe to proceed to another architecture?

**Answer: YES, WITH EXPLICIT REGIME-AWARENESS**

**Safe aspects:**
- ✓ EVEN control is valid for relative comparison
- ✓ Candidates can be compared to this baseline fairly
- ✓ No leakage issues prevent proceeding
- ✓ Protocol is sound

**Required cautions:**
- ⚠ Do NOT optimize candidates specifically for H9-H12 (peak hours where EVEN has advantage)
- ⚠ Expect ODD performance to be substantially worse than EVEN gates suggest (likely 5-10 W/m² worse)
- ⚠ Monitor H9-H12 and rest-of-horizon errors separately (don't trust aggregate MAE alone)
- ⚠ Do NOT claim the EVEN control is transferable to ODD
- ⚠ Be transparent: "This candidate shows improvement on EVEN development baseline, but ODD performance is uncertain given the 9.82 W/m² regime/algorithm gap."

---

## SUMMARY OF CORRECTIONS

| Aspect | Previous Report | Corrected Report |
|---|---|---|
| Gap explanation | "Explained" | "Partially explained by plausible mechanisms" |
| Regime attribution | "~4-5 W/m² quantified" | "Plausible but unquantified" |
| Cloud attribution | "~2-3 W/m² quantified" | "Plausible but unquantified" |
| Reconstruction variance | "~1-2 W/m² plausible" | "Unresolved" |
| EVEN→ODD penalty | "~10 W/m² penalty claimed" | "Likely 5-10 W/m², magnitude unquantified" |
| Protocol status | "No changes needed" | "Sound, but needs caveats in interpretation" |
| Confidence tone | High | Medium (appropriately cautious) |

---

## WHAT REMAINS VALID

**Level 1: Definitive Facts**
- The 26.3668 W/m² EVEN control is valid for relative candidate comparison within EVEN
- The 36.188657 W/m² ODD benchmark is verified and accurate
- The 9.82 W/m² gap is real and measured
- No leakage to EVEN
- All features are causal

**Level 2: Plausible but Unquantified**
- EVEN has easier conditions (more clear skies, higher H9-H12 irradiance)
- This likely contributes to the gap
- The magnitude is unknown (likely 3-6 W/m², but unproven)

**Level 3: Speculative (Do Not Rely On)**
- Specific attribution (4-5 W/m² regime, 2-3 W/m² cloud, etc.)
- Predicted ODD performance from EVEN gates
- "10 W/m² penalty" magnitude claim

---

## FINAL HONEST ASSESSMENT

**What we know:**
- 26.3668 W/m² (EVEN) vs 36.188657 W/m² (ODD) gap is real
- EVEN and ODD have detectably different data distributions
- These plausibly contribute to performance difference
- No methodology problems detected

**What we do NOT know:**
- Exact quantitative contribution of regime vs algorithm
- Whether EVEN advantage is 3 W/m², 5 W/m², or 9 W/m²
- How to reliably predict ODD performance from EVEN results
- Why my reconstruction achieved 24.78 vs reported 26.37 W/m²

**Scientific recommendation:**
Proceed with architecture research on EVEN baseline, but maintain strict regime-awareness and do NOT over-claim transferability to ODD. Use conservative expectations about ODD improvement.

---

*End of Corrected Forensic Audit*  
**Previous overconfident claims retracted. Findings reframed as plausible mechanisms pending quantification.**
