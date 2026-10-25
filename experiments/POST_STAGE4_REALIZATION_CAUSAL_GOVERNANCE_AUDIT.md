# POLARIS — Realization-Consistency Causal & Governance Audit

**Experiment ID:** `EXP-STAGE4-REALIZATION-CONSISTENCY-2025`  
**Date (UTC):** 2026-10-06  
**Audit Type:** Causal & Governance Audit (Read-Only Forensic Evaluation)  
**Status:** COMPLETE. No new campaign run. No production code modified. No results modified.  
**Authoritative Campaign Outcomes:**
- **Arm A (Current Realization):** Winner = **`Candidate_S`** (23.11% diesel reduction; 1,409.21 L saved). Candidate SW **FAILS Safety Gate 2** ($\Delta R_P = -0.5815\text{ pp}$ vs Control B).
- **Arm B (Plan-Consistent Diagnostic Realization):** Winner = **`Candidate_SW`** (23.77% diesel reduction; 1,351.33 L saved). Candidate SW **PASSES Safety Gate 2** ($\Delta R_P = +1.3220\text{ pp}$ vs Control B).
- **Audited Pre-Outcome Status:** **All 10 Audit Gates Passed (G1–G11)**.
- **Empirical Classification (Precedence Rule):** **`SAFETY-CHANGING`** (and ranking-changing).
- **Governance Audit Classification:** **`POLICY-DEPENDENT / GOVERNANCE BLOCK`**.

---

## 1. Executive Summary & Core Finding

The `EXP_STAGE4_REALIZATION_CONSISTENCY` experiment tested whether the planned-versus-realized battery charge mismatch materially changes POLARIS candidate safety or ranking.

The empirical answer is unambiguous: **YES, it is safety-changing and ranking-changing**.
However, this forensic and causal audit establishes the critical underlying mechanism:

1. **Arm B does NOT merely isolate a battery-charge accounting mismatch.** It introduces an entirely different, highly restrictive **Load-Service Priority Policy** across the entire microgrid.
2. **In Arm A (Load-First):** All connected customer demand (critical and non-critical) is served from available supply before surplus energy is routed into battery charging ($\text{Priority: Total Load} > \text{Battery Charge} > \text{Curtailment}$).
3. **In Arm B (Charge-Prioritized):** Critical demand is served first, but planned battery charging is explicitly prioritized from available supply *before* non-critical load ($\text{Priority: Critical Load} > \text{Battery Charge} > \text{Non-Critical Load} > \text{Curtailment}$).
4. **Control B's reliability collapses under Arm B:** Control B's proportional reliability plummets from **$83.8500\%$ down to $78.6555\%$** (a massive drop of **$-5.1945\text{ pp}$**, shedding an additional **$2,557.44\text{ kWh}$** of uncoordinated customer load).
5. **Candidate SW's apparent safety qualification under Arm B is an artifact of Control B's collapse:** Candidate SW does **NOT** serve more customer load under Arm B. Its own proportional reliability actually *degrades* from $83.2685\%$ down to $79.9774\%$ (shedding an additional $1,532.80\text{ kWh}$). Candidate SW only passes Gate 2 under Arm B because the Control B baseline degraded even further ($-5.19\text{ pp}$ vs $-3.29\text{ pp}$).
6. **Governance Rule:** Neither Candidate SW nor Candidate S can be declared the definitive operational winner based on Arm B. Arm B is confirmed to be an unapproved operational shedding policy. Production promotion remains **STRICTLY UNAUTHORIZED**.

---

## 2. Causal Anatomy: Arm A vs Arm B Mechanics

### 2.1 The Two Realization Priority Hierarchies

At every reoptimization hour $t$, available physical supply is:
$$S_{\text{avail}} = S_{\text{pv}} + W + \text{diesel}_{\text{realized}} + p_{\text{dis,realized}}$$
Total physical demand is $D$, partitioned into critical demand $D_c = \min(11600\text{ W}, D)$ and non-critical demand $D_{\text{nc}} = D - D_c$.

```
ARM A (Current / Physical Surplus):
  1. Served Load: s_tot = min(D, S_avail)
  2. Battery Charge: C = min(max(0, S_avail - D), Charge_Cap)
  3. Curtailment: curt = S_avail - s_tot - C
  --> Priority: Critical Load = Non-Critical Load > Battery Charging > Curtailment

ARM B (Plan-Consistent Diagnostic):
  1. Critical Load: s_c = min(D_c, S_avail)
  2. Battery Charge: C = min(P_c, max(0, S_avail - s_c), Charge_Cap)
  3. Flexible Load: F = min(P_f, max(0, S_avail - s_c - C))
  4. Non-Critical Load: n = min(D - D_c, max(0, S_avail - s_c - C - F))
  5. Curtailment: curt = S_avail - (s_c + n) - C - F
  --> Priority: Critical Load > Battery Charging > Flex > Non-Critical Load > Curtailment
```

### 2.2 The Root Cause in the Planning Model

Why did the optimizer plan battery charging $P_c$ that conflicted with total demand $D$ in the first place?

In `research_numerical_extractor.py`:
- Layer J1 (priority 4): Minimizes critical unmet load $\sum \text{unmet\_crit}(t)$.
- Layer J2 (priority 3): Minimizes reserve shortfall $\sum s_{J2}(t)$.
- Layer J3 (priority 2): Minimizes diesel fuel consumption.
- Layer J4 (priority 1): Minimizes renewable curtailment.
- **Non-critical load carries ZERO penalty in the objective function.**
- Balance constraint Layer B ties served power strictly to critical demand:
  $$p_{\text{served}}(t) + \text{unmet\_crit}(t) = \text{critical\_demand}(t)$$
  Total demand balance R4 ($p_{\text{served}} + p_{\text{unmet}} = p_{\text{dem}}$) forces all non-critical demand into $p_{\text{unmet}}(t)$.

**Causal Insight:** The MILP did not plan battery charging because it made a deliberate economic trade-off between battery charging and customer service. **The MILP planned battery charging because it was completely blind to non-critical load.** To the optimizer, non-critical demand does not exist as an electrical service obligation; it is shed by construction with zero penalty.

When Arm A executes, the physical microgrid serves all customers who have their switches turned on before charging the battery. When Arm B executes, the executor enforces the optimizer's non-critical shedding on the real grid, forcibly cutting off non-critical customers to push electrons into the battery.

---

## 3. Detailed Telemetry Evidence

### 3.1 Aggregate Comparative Metrics (29,520 Arm-Hours)

| Arm | Metric | Realization A (Load-First) | Realization B (Charge-Prioritized) | Difference ($B - A$) |
|---|---|---|---|---|
| **Control B** | Diesel Fuel (L) | 6,096.90 | 5,685.23 | **$-411.67\text{ L}$** |
| | Proportional Reliability ($R_P$) | 83.8500% | 78.6555% | **$-5.1945\text{ pp}$** |
| | Critical-First Reliability ($R_{\text{CF}}$) | 93.7538% | 93.9752% | $+0.2213\text{ pp}$ |
| | Unmet Load (kWh) | 7,797.27 | 10,354.71 | **$+2,557.44\text{ kWh}$** |
| | Curtailment (kWh) | 10,015.26 | 11,384.87 | $+1,369.61\text{ kWh}$ |
| | Diesel On-Hours | 442 | 389 | $-53\text{ h}$ |
| **Candidate S** | Diesel Fuel (L) | 4,687.69 | 4,750.83 | $+63.14\text{ L}$ |
| | Diesel Saving vs Control (%) | **23.11%** | 16.44% | $-6.67\text{ pp}$ |
| | Proportional Reliability ($R_P$) | 84.6726% | 80.4092% | **$-4.2635\text{ pp}$** |
| | Critical-First Reliability ($R_{\text{CF}}$) | 94.3945% | 94.5705% | $+0.1760\text{ pp}$ |
| | Unmet Load (kWh) | 7,428.47 | 9,469.69 | $+2,041.22\text{ kWh}$ |
| | Safety Gate 2 Status | **PASS (+0.82 pp)** | **PASS (+1.75 pp)** | Invariant |
| **Candidate SW** | Diesel Fuel (L) | 3,768.55 | 4,333.90 | **$+565.35\text{ L}$** |
| | Diesel Saving vs Control (%) | **38.19%** | **23.77%** | $-14.42\text{ pp}$ |
| | Proportional Reliability ($R_P$) | 83.2685% | 79.9774% | **$-3.2910\text{ pp}$** |
| | Critical-First Reliability ($R_{\text{CF}}$) | 94.0361% | 94.2706% | $+0.2345\text{ pp}$ |
| | Unmet Load (kWh) | 8,140.83 | 9,673.63 | $+1,532.80\text{ kWh}$ |
| | Safety Gate 2 Status | **FAIL ($-0.58\text{ pp}$)** | **PASS ($+1.32\text{ pp}$)** | **FLIPPED** |
| **Candidate S-L** | Diesel Fuel (L) | 5,280.24 | 5,229.27 | $-50.97\text{ L}$ |
| | Diesel Saving vs Control (%) | 13.39% | 8.02% | $-5.37\text{ pp}$ |
| | Proportional Reliability ($R_P$) | 85.0064% | 80.4890% | $-4.5175\text{ pp}$ |
| **Candidate SW-L**| Diesel Fuel (L) | 5,263.96 | 5,318.57 | $+54.60\text{ L}$ |
| | Diesel Saving vs Control (%) | 13.66% | 6.45% | $-7.21\text{ pp}$ |
| | Proportional Reliability ($R_P$) | 85.2411% | 80.5652% | $-4.6759\text{ pp}$ |

---

## 4. Why Control B Changes Substantially

In Control B, proportional reliability drops by **$-5.1945\text{ pp}$** (shedding 2,557.44 kWh of non-critical load).

The cause is clearly visible at **Hour 0 across all 123 origins**:
- Control B has unconditional 6-hour lookahead EBR ($EBR \approx 50\text{--}60\text{ kWh}$ plus 40 kWh buffer = $90\text{--}100\text{ kWh}$ target).
- Because initial stored energy is 100 kWh, and hour-0 critical deficit must be covered, the MILP plans a massive hour-0 diesel run and battery charge:
  $$\text{Mean Planned Charge } P_c = 36,684.70\text{ W (in 123/123 origins)}$$
- **Under Arm A:** Available supply (diesel + wind) is 45.5 kW. The executor serves the full 15.0 kW demand first ($100.0\%$ service, 0 unmet load). The residual 30.6 kW charges the battery. Proportional reliability at hour 0 is **$100.0\%$**.
- **Under Arm B:** The executor serves critical demand (11.6 kW) first. It then allocates 36.7 kW to battery charging ($C = 36.7\text{ kW}$). Total energy committed is $11.6 + 36.7 = 48.3\text{ kW}$, which exceeds available supply. Non-critical demand (6.3 kW) receives almost nothing. Unmet load at hour 0 is **$6,079.83\text{ W}$**!
- Proportional reliability at hour 0 for Control B collapses from **$100.0\%$ down to $66.03\%$** (a **$-33.97\text{ pp}$ collapse at hour 0**).

Across the full campaign, Control B under Arm B continuously refuses to use available diesel or renewable generation to serve non-critical load whenever a planned charge exists, shedding 2,557 kWh of load and reducing diesel by 411.67 L.

---

## 5. Why Candidate SW Changes from FAIL to PASS

The safety qualification flip of Candidate SW is fully explained by relative degradation rates:

1. **Under Arm A:**
   - Control B maintains high load service ($R_P = 83.8500\%$).
   - Candidate SW dispatches diesel conservatively, resulting in $R_P = 83.2685\%$.
   - Gate 2 margin: $\Delta R_P = 83.2685\% - 83.8500\% = -0.5815\text{ pp} < 0.00\text{ pp}$.
   - **Verdict:** **FAIL Gate 2 (Disqualified)**.

2. **Under Arm B:**
   - Control B is heavily penalized by its large uncredited EBR targets, causing massive non-critical shedding: $R_P$ crashes to **$78.6555\%$** ($-5.1945\text{ pp}$).
   - Candidate SW credits wind in its EBR formula ($\text{EBR}_{\text{SW}} = \max(0, \text{crit} - \text{solar} - \text{wind})$). At hour 0, wind is 7.0 kW, so SW's deficit is only 4.6 kW. SW plans battery charging in only 39 of 123 origins at hour 0 (mean planned charge 13.4 kW vs Control's 36.7 kW).
   - Consequently, Candidate SW sheds less non-critical load than Control B at hour 0 ($5,015\text{ W}$ vs $6,080\text{ W}$).
   - Overall, Candidate SW's $R_P$ drops by $-3.2910\text{ pp}$ (to $79.9774\%$).
   - Gate 2 margin: $\Delta R_P = 79.9774\% - 78.6555\% = \mathbf{+1.3220\text{ pp}} \ge 0.00\text{ pp}$.
   - **Verdict:** **PASS Gate 2 (Qualified)**.

**Key Finding:** Candidate SW's safety pass under Arm B is **NOT** because Candidate SW provided better reliability to customers. Its load shedding worsened by 1,532.80 kWh. It passed solely because Control B's reliability crashed even more severely under the new load-shedding policy.

---

## 6. Analysis of a Potential Third Realization Formulation (Formulation C)

Can a realization formulation be defined that preserves the optimizer's planned battery charging without arbitrarily imposing a new non-critical load-shedding policy?

### 6.1 Mathematical Formulation of the Dilemma

At any timestep where available supply $S_{\text{avail}}$ satisfies:
$$D_c \le S_{\text{avail}} < D + P_c$$
there is a physical deficit between simultaneous load service and battery charging:
$$\text{Deficit } \Delta_{\text{conflict}} = (D + P_c) - S_{\text{avail}} > 0$$

- **Arm A allocates 100% of the deficit to battery charging:**
  $$C = \max(0, S_{\text{avail}} - D), \quad n = D - D_c$$
  *(Policy: Unconditional load service; battery gets leftovers).*
- **Arm B allocates 100% of the deficit to non-critical load:**
  $$C = P_c, \quad n = \max(0, S_{\text{avail}} - D_c - P_c)$$
  *(Policy: Unconditional battery charging; customers get leftovers).*

### 6.2 Evaluation of Candidate "Formulation C" Alternatives

#### Candidate Formulation C1: Proportional Deficit Sharing
Allocate the available supply above critical load proportionally between planned charge $P_c$ and non-critical demand $D_{\text{nc}}$:
$$C = (S_{\text{avail}} - D_c) \cdot \frac{P_c}{P_c + D_{\text{nc}}}, \quad n = (S_{\text{avail}} - D_c) \cdot \frac{D_{\text{nc}}}{P_c + D_{\text{nc}}}$$
- *Evaluation:* While mathematically symmetric, this is also an arbitrary operational policy (50/50 slotted brownout). It neither honors the plan's exact charge nor provides full customer service.

#### Candidate Formulation C2: Literal Execution of Planned Served Load
Enforce $\text{served} = \min(P_{\text{serv}}, S_{\text{avail}})$.
- *Evaluation:* Because Layer B in the MILP binds $P_{\text{serv}} \le D_c$, this forces non-critical service to exactly 0.0 W in every hour across all arms. Proportional reliability drops to $\approx 64\%$ for all arms, destroying microgrid service.

### 6.3 Definitive Conclusion on Formulation Feasibility

**No unique, defensible realization formulation exists at the executor level.**

The reason is structural:
- Physics dictates only that $\sum \text{Inputs} = \sum \text{Outputs}$. Both Arm A and Arm B satisfy physical energy conservation and busbar balance to $10^{-6}\text{ W}$ (Gate G6 PASS).
- Deciding whether electrons should flow to customer appliances or into battery storage when supply is insufficient for both is the **fundamental definition of a Microgrid Operating Policy**.
- The conflict exists because the MILP was given an **incomplete objective contract**: it was never told the economic value of non-critical load ($V_{\text{LL, non-crit}}$). It was permitted to shed non-critical load for free.
- **An executor cannot resolve an economic trade-off that the planning model refused to price.**

---

## 7. Governance Verdict & Next Steps

### 7.1 Required Audit Classification
**`POLICY-DEPENDENT / GOVERNANCE BLOCK`**

- **Justification:** Candidate ranking and safety are strictly dependent on the microgrid's load-priority policy. Under a "Serve Customers First" policy (Arm A), Candidate S is the verified winner (23.11%) and Candidate SW is a safety failure. Under a "Charge Reserves First" policy (Arm B), Candidate SW is the winner (23.77%) and Candidate S is runner-up (16.44%).
- Because the microgrid system specification has not established whether non-critical customers may be browned out to meet reserve targets, this is a **governance policy block**, not a software bug.

### 7.2 Strict Operational & Research Boundaries
1. **Candidate SW is NOT the authorized winner.** Promoting SW based on Arm B would deploy an algorithm whose safety depends on degrading customer service by 1,532 kWh.
2. **Candidate S is NOT automatically authorized for production.** While Candidate S won under Arm A, its performance was evaluated under an executor that deviates from the optimizer's planned charging.
3. **Production code must remain completely untouched.**

### 7.3 Governance Decision Pathways for Next Phase

To permanently resolve this block, microgrid governance must make one of two policy determinations:

- **Policy Pathway 1 (Customer-First Grid):** Formally declare that microgrid load service has strict priority over battery charging. Non-critical load shedding is prohibited when generation is physically available.
  - *Result:* Realization A is confirmed as authoritative operational physics. Candidate S is confirmed as the Stage 4 winner (23.11%). Candidate SW is permanently retired due to Gate-2 safety violation.
- **Policy Pathway 2 (Demand-Response / Coordinated Grid):** Authorize planned non-critical load shedding for reserve management, but **price non-critical load in the optimizer objective**.
  - *Requirement:* Add a finite penalty term (e.g., $c_5 \cdot \text{unmet\_noncrit}(t)$) to the MILP objective so the optimizer weighs the true cost of shedding before choosing to charge.
  - *Execution:* Requires a new, formal preregistration and campaign. Cannot be decided retroactively.

---

## 8. Cryptographic Hashes of Record

| Artifact | Path | SHA-256 |
|---|---|---|
| **Preregistration MD** | `experiments/EXP_STAGE4_REALIZATION_CONSISTENCY_PREREGISTRATION.md` | `1e9077d4bb3f3828f7040a9fbd39a31e46308c547ce648a80c7579099124cf0b` |
| **Preregistration JSON** | `experiments/EXP_STAGE4_REALIZATION_CONSISTENCY_PREREGISTRATION.json` | `076279c227be7c8f866e90226adc719042c3ad7f9977161e5dad4b006a14bb8b` |
| **Arm B Executor** | `experiments/stage4_realization_consistency_2025/plan_consistent_realization.py` | `dea4b46b623e83fd7bc5428ef013a3b57b58af756f3397099a5863f6d59cbadd` |
| **Campaign Telemetry** | `experiments/stage4_realization_consistency_2025/STAGE4_REALIZATION_CONSISTENCY_TELEMETRY.csv` | `2ccc80687baadeeb2bca05b151b17c9349a21126d76e9fecb71f1cba870a20d9` |
| **Campaign Results** | `experiments/stage4_realization_consistency_2025/STAGE4_REALIZATION_CONSISTENCY_RESULTS.csv` | `87849c7cb882d9cfc21a17759a6abf8043050d47811768daae177250e05f5eb5` |
| **Comparison Report** | `experiments/stage4_realization_consistency_2025/STAGE4_REALIZATION_CONSISTENCY_COMPARISON.md` | `9bda9e9992ce332649a1cc1bc12906ac41727b616591f1696a6f5561b7f9621a` |
| **Safety Report** | `experiments/stage4_realization_consistency_2025/STAGE4_REALIZATION_CONSISTENCY_SAFETY_REPORT.md` | `e166924410ffd4cb361205fa91cd525f8dc66145602a1fb226e337591bb9b38e` |
| **Statistical Report** | `experiments/stage4_realization_consistency_2025/STAGE4_REALIZATION_CONSISTENCY_STATISTICAL_REPORT.md` | `3cbdf2eec8a037c5556648e2d6220f3be5155fbeb9e019c430195ddb41e85736` |
| **Execution Audit** | `experiments/stage4_realization_consistency_2025/STAGE4_REALIZATION_CONSISTENCY_EXECUTION_AUDIT.md` | `7aa0e85ee15e7acfad7760de998028a07dd190ef88e21ddf3c74887a1923d4b1` |
| **Audit JSON** | `experiments/stage4_realization_consistency_2025/STAGE4_REALIZATION_CONSISTENCY_AUDIT.json` | `328de18f46bdc88e9bab8d2cfe5120bc8114791377814792d23f34cbe1ede898` |
| **Manifest** | `experiments/stage4_realization_consistency_2025/STAGE4_REALIZATION_CONSISTENCY_EXECUTION_MANIFEST.json` | `12099a9503764fd7be36cf4080649721d4ce8186afa2cef11e08f9233bb3126e` |
