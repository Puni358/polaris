# POLARIS Pre-Execution Specification: Decision OD-02 Boundary Diagnostic

**Tracking ID:** `SPEC-2026-OD02-DIAG-01`  
**Reference Proposal:** `PROP-2026-OD02-DIAG-01`, Revision 2.1  
**Authoritative Governance Register:** `POLARIS_MASTER_DECISION_REGISTER.json` (v1.9.13, Pass 23)  
**Execution Clearance:** **Gate B.3 Complete — Gate C STRICTLY NOT AUTHORIZED**  
**Governance Invariants:** Decision `OD-02` frozen; `winner: null` preserved; 2025 blind data quarantined; `tau_cont` unset.

---

## 1. Evaluation Origins & Sampling Frame

### 1.1 Status of Evaluation Origins & Authoritative Partition
- **Authoritative Provenance:** Origins are drawn exclusively from the held-out `2024-ODD` validation partition ($N=173$ origins, 4,152 rows), ratified in `POLARIS_MASTER_DECISION_REGISTER.json` Section 39.1.2 (Pass 23) and `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv`.
- **Midnight-UTC Anchor:** All origins conform strictly to the mandatory midnight-UTC origin contract (`00:00:00` UTC). No sub-daily or midday origins exist.
- **Owner-Authorized Selection:** The Project Owner has authorized the explicit $N=10$ origin manifest below. Zero calendar dates were invented.

### 1.2 Stratification Structure & Verified Ten-Origin Manifest
The exploratory sampling frame is stratified across three distinct physical regimes observed at Lake Torneträsk ($68.35^\circ\text{ N}$):

1. **Regime A (Polar Day / Midnight Sun — 4 origins):**
   - *Physical Criterion:* Minimum solar elevation across all 24 horizons is strictly positive ($\alpha_{\min} > 0.0^\circ$). Sun remains continuously above the horizon for 24 hours/day. Tests whether non-zero solar potential at slot 23 ($t_0 + 24\text{h}$) alters battery scheduling at step 0 per MDR Section 38.1.2.
   - `2024-06-01T00:00:00Z` (ID 67): $\alpha_{\text{mid}} = +0.50^\circ$, range $[+0.50^\circ, +43.71^\circ]$
   - `2024-06-11T00:00:00Z` (ID 72): $\alpha_{\text{mid}} = +1.50^\circ$, range $[+1.50^\circ, +44.71^\circ]$
   - `2024-06-19T00:00:00Z` (ID 76): $\alpha_{\text{mid}} = +1.82^\circ$, range $[+1.82^\circ, +45.02^\circ]$
   - `2024-06-21T00:00:00Z` (ID 77): $\alpha_{\text{mid}} = +1.83^\circ$, range $[+1.83^\circ, +45.03^\circ]$ (Summer Solstice)

2. **Regime B (Dynamic Shoulder / Autumn Equinox — 3 origins):**
   - *Physical Criterion:* Significant daytime solar generation with true astronomical darkness at midnight ($\alpha_{\text{mid}} \le -6.0^\circ$, civil/nautical twilight or night). Tests diurnal battery charge/discharge transitions.
   - `2024-09-15T00:00:00Z` (ID 120): $\alpha_{\text{mid}} = -18.62^\circ$, range $[-18.74^\circ, +24.29^\circ]$
   - `2024-09-21T00:00:00Z` (ID 123): $\alpha_{\text{mid}} = -20.93^\circ$, range $[-21.09^\circ, +21.95^\circ]$
   - `2024-09-23T00:00:00Z` (ID 124): $\alpha_{\text{mid}} = -21.70^\circ$, range $[-21.88^\circ, +21.16^\circ]$ (Autumn Equinox)

3. **Regime C (Polar Night / Winter Minimum — 3 origins):**
   - *Physical Criterion:* Maximum solar elevation across all 24 horizons is strictly non-positive ($\alpha_{\max} \le 0.0^\circ$). Sun remains continuously at or below the horizon for all 24 hours. Establishes the physical zero-solar control baseline.
   - *Winter Origin Correction:* Legacy candidate `2024-01-25` reached $\alpha_{\max} = +2.61^\circ > 0^\circ$ and was rejected. Replaced by `2024-11-30T00:00:00Z` (ID 158) where $\alpha_{\max} = -0.25^\circ \le 0^\circ$.
   - `2024-11-30T00:00:00Z` (ID 158): $\alpha_{\text{mid}} = -43.17^\circ$, range $[-43.17^\circ, -0.25^\circ]$ (Polar Night Entry)
   - `2024-12-08T00:00:00Z` (ID 162): $\alpha_{\text{mid}} = -44.24^\circ$, range $[-44.24^\circ, -1.25^\circ]$ (Early December Polar Night)
   - `2024-12-22T00:00:00Z` (ID 169): $\alpha_{\text{mid}} = -45.01^\circ$, range $[-45.01^\circ, -1.85^\circ]$ (Winter Solstice Polar Night)
   *(Documented Alternate: `2024-12-30T00:00:00Z` [ID 173], range $[-44.75^\circ, -1.51^\circ]$.)*

---

## 2. Factorial Variant Specifications (V0 – V3)

The diagnostic evaluates four variants in an isolated One-Factor-At-A-Time (OFAT) factorial design:

```
                          ┌─────────────────────────────────────┐
                          │     Variant 0 (Frozen Baseline)     │
                          │ Solar: shifted + [0.0]              │
                          │ EBR:   unshifted                    │
                          └──────────────────┬──────────────────┘
                                             │
                   ┌─────────────────────────┴─────────────────────────┐
                   ▼                                                   ▼
┌─────────────────────────────────────┐             ┌─────────────────────────────────────┐
│  Variant 1 (EBR Alignment Shift)    │             │ Variant 2 (Terminal Solar Estimator)│
│ Solar: shifted + [0.0]              │             │ Solar: shifted + [Candidate Est]    │
│ EBR:   shifted by +1h (hypothetical)│             │ EBR:   unshifted                    │
└──────────────────┬──────────────────┘             └──────────────────┬──────────────────┘
                   │                                                   │
                   └─────────────────────────┬─────────────────────────┘
                                             ▼
                          ┌─────────────────────────────────────┐
                          │    Variant 3 (Combined Interaction) │
                          │ Solar: shifted + [Candidate Est]    │
                          │ EBR:   shifted by +1h (hypothetical)│
                          └─────────────────────────────────────┘
```

### 2.1 Variant 0 (Control Reference — Pure Frozen OD-02 Baseline)
- **Status:** **FULLY VERIFIED & PRODUCTION PARITY CONFIRMED**
- **Solar Generation:** Shift raw 24-step horizons $1 \dots 23 \to 0 \dots 22$; inject approved OD-02 fallback `0.0 W` at slot 23:
  $$\hat{P}_{\text{solar}}[0 \dots 22] = P_{\text{raw}}[1 \dots 23], \quad \hat{P}_{\text{solar}}[23] = 0.0\text{ W}$$
- **Solar Irradiance:** Shift raw horizons $1 \dots 23 \to 0 \dots 22$; inject fallback `0.0 W/m²` at slot 23.
- **Timestamps:** Advance by $+1\text{h}$: $[t_0, t_0+23\text{h}] \to [t_0+1\text{h}, t_0+24\text{h}]$.
- **Conformal EBR Trajectory:** **Strictly unshifted**. Preserved identically as computed by `N6SolarForecastEngine._compute_ebr_reserve()` indexing raw lookahead $[k, \min(k+6, 24))$.
- **Wind, Total Demand, Critical Demand:** **Strictly unshifted**.
- **GAP19 Policy B Pairing:** Pointwise maximum reserve envelope:
  $$E_{\text{stage2\_target}}[t] = \max(E_{\text{crit\_reserve}}[t], E_{\text{ebr}}[t])$$
- **Terminal Reserve Target ($E_{\text{term}}$):** Dynamic cycle-neutral target: $E_{\text{term}} = \text{initial\_e\_wh} - \text{min\_e\_wh}$.

### 2.2 Variant 1 (Proposed EBR Shift Perturbation Only)
- **Status:** **UNVERIFIED EXPERIMENTAL HYPOTHESIS — DISABLED BY DEFAULT**
- **Solar, Wind, Demand, Timestamps:** Identical to Variant 0.
- **Conformal EBR Trajectory:** Shifted forward by $+1\text{h}$ with persistence tail padding:
  $$E_{\text{ebr\_aligned}}[0 \dots 22] = E_{\text{ebr\_raw}}[1 \dots 23], \quad E_{\text{ebr\_aligned}}[23] = E_{\text{ebr\_raw}}[23]$$
- **Unresolved Limitations:** Repeating the final EBR value ($E[23] = E[22]$) is an ad-hoc heuristic without formal split-conformal calibration or 90% coverage guarantees for horizon 25.

### 2.3 Variant 2 (Proposed Terminal Solar Estimator Only)
- **Status:** **UNVERIFIED EXPERIMENTAL HYPOTHESIS — DISABLED BY DEFAULT**
- **EBR, Wind, Demand, Timestamps:** Identical to Variant 0.
- **Slot 23 Solar Fallback:** Replaces `0.0 W` with candidate estimator:
  - **Candidate 2A (Physics-Based Clear-Sky Continuation):**
    $$\hat{P}_{\text{solar}}[23] = \min(GHI_{\text{cs, terrain}}(t_0 + 24\text{h}) \cdot K_{\text{pv}}, P_{\text{inv, max}})$$
    - Inputs: Terrain-adjusted clear-sky irradiance $GHI_{\text{cs, terrain}}$ at $t_0 + 24\text{h}$ ($\text{W/m}^2$); plant conversion factor $K_{\text{pv}} = 51.0\text{ W}/(\text{W/m}^2)$ (unverified); inverter ceiling $P_{\text{inv, max}} = 60,000\text{ W}$.
    - Clipping: Bound strictly to $[0.0, 60000.0]\text{ W}$.
    - Blocker: Runtime `ForecastBundle` does not expose $GHI_{\text{cs, terrain}}$ at horizon 25; astronomical solar geometry is not computed online.
  - **Candidate 2B (Persistent Attenuation Extension):**
    $$\hat{P}_{\text{solar}}[23] = \min(\hat{k}_t[22] \cdot GHI_{\text{cs, terrain}}(t_0 + 24\text{h}) \cdot K_{\text{pv}}, P_{\text{inv, max}})$$
    - Inputs: Penultimate clearness index $\hat{k}_t[22] = \frac{\hat{SW}_{\text{IN}}[22]}{GHI_{\text{cs, terrain}}(t_0 + 23\text{h}) + \epsilon}$.
    - Blocker: Attenuation behavior under zero clear-sky conditions or terrain obstruction is undefined.

### 2.4 Variant 3 (Combined Factor Interaction)
- **Status:** **UNVERIFIED EXPERIMENTAL HYPOTHESIS — DISABLED BY DEFAULT**
- Evaluates Variant 1 (EBR shift) and Variant 2 (Terminal solar) simultaneously to measure non-linear interaction cross-terms.

---

## 3. Verified Facts vs. Unresolved Dependencies Matrix

| Variant / Subsystem | Implementation Status | Verified Source Facts | Unresolved Dependencies & Assumptions | Eligibility for Gate C |
| :--- | :--- | :--- | :--- | :--- |
| **Variant 0 (Baseline)** | **VERIFIED** | Matches production `adapters.py` lines 641–695 and `gap19_highs_native.py` exactly. | Zero code dependencies; requires only owner approval of origin timestamps. | **ELIGIBLE** (upon origin approval) |
| **Variant 1 (EBR Shift)** | **UNVERIFIED** | Slicing logic implemented in scratch harness. | Conformal coverage uncalibrated for persistence tail padding ($E[23]$). | **INELIGIBLE / DISABLED** |
| **Variant 2 (Solar Est)** | **UNVERIFIED** | Mathematical formula defined. | Missing online clear-sky irradiance at horizon 25; $K_{\text{pv}}$ unverified. | **INELIGIBLE / DISABLED** |
| **Variant 3 (Combined)** | **UNVERIFIED** | Combination logic implemented in scratch harness. | Inherits all unresolved dependencies of V1 and V2. | **INELIGIBLE / DISABLED** |

---

## 4. Outcome Metrics & Multi-Dimensional Classification

The diagnostic records outputs across four independent, orthogonal dimensions without collapsed or mutually exclusive states:

### Dimension 1: Solver Termination & Feasibility
- Status categories: `OPTIMAL`, `INFEASIBLE`, `UNBOUNDED`, `TIME_LIMIT`, `NUMERICAL_ERROR`, `INCONCLUSIVE`.
- Infeasibility rule: If a variant produces `INFEASIBLE`, first-action comparison and objective differences are recorded as `NOT_APPLICABLE`; feasibility failure is recorded as a primary finding.

### Dimension 2: First-Action ($u_0$) Comparison
- **Continuous Decision Vector ($u_{0, \text{cont}}$):**
  - Evaluated variables (9 continuous components):
    $$u_{0, \text{cont}} = \left( p_{\text{sol\_used}}[0], p_{\text{wind\_used}}[0], p_{\text{diesel}}[0], p_{\text{chg}}[0], p_{\text{dis}}[0], p_{\text{curt\_total}}[0], p_{\text{served}}[0], p_{\text{unmet}}[0], p_{\text{flex}}[0] \right)$$
  - Metric: Raw continuous delta vector $\Delta u_{0, \text{cont}} = u_{0, \text{cont}}^{(\text{var})} - u_{0, \text{cont}}^{(\text{base})}$.
  - Summary norm: Maximum absolute continuous difference:
    $$\|\Delta u_{0, \text{cont}}\|_\infty = \max_{j} \left| u_{0, \text{cont}, j}^{(\text{var})} - u_{0, \text{cont}, j}^{(\text{base})} \right|$$
  - **Schema Fidelity Safeguard (Curtailment):** Production `DispatchPlan` aggregates curtailment into `renewable_curtailment`. Component fields $p_{\text{curt, sol}}$ and $p_{\text{curt, wind}}$ are explicitly set to `None` (unavailable in schema) to prevent silent false zeros.
  - **Schema Fidelity Safeguard (Binaries):** Production `DispatchPlan` does not expose solver-internal binary columns ($u_{\text{diesel}}, v_{\text{start}}, u_{\text{chg}}, u_{\text{dis}}$). In accordance with Gate B.1 instructions, internal binaries are **not derived from power flows** and remain `None`; `binary_difference_detected` evaluates to `None` with `binary_availability = "UNAVAILABLE_IN_PUBLIC_SCHEMA"`.

### Dimension 3: Four-Tier Lexicographic Objective Variation ($\Delta J$)
- Evaluated components (matching GAP19 hierarchical solver stages):
  - $J_1$: Critical Load Deficit ($\text{Wh}$, Priority 4)
  - $J_2$: Governed Reserve Shortfall ($\text{Wh}$, Priority 3, combining critical and conformal EBR reserves)
  - $J_3$: Diesel Fuel Consumption ($\text{L}$, Priority 2)
  - $J_4$: Renewable Curtailment Penalty ($\text{Wh}$, Priority 1)
- Metric: Independent tier deltas $(\Delta J_1, \Delta J_2, \Delta J_3, \Delta J_4)$ without scalar collapse:
  $$\Delta J_k = J_k^{(\text{var})} - J_k^{(\text{base})}, \quad k \in \{1, 2, 3, 4\}$$
- Multi-objective status: Declared `IDENTICAL` only if $|\Delta J_k| \le \tau_{\text{obj}}$ ($10^{-4}$) for all four tiers; otherwise declared `DISTINCT`. A shift in reserve shortfall ($J_2$) or curtailment ($J_4$) with identical diesel fuel ($J_3$) is detected immediately.

### Dimension 4: Degeneracy & Solution Uniqueness
- **Binding Caveat:** Similar or identical objective values ($|\Delta J| \approx 0$) accompanying a changed first action ($\Delta u_0 \ne 0$) do **not** establish whether the action change was physically forced by the boundary condition or caused by solver degeneracy across alternative optimal vertices.
- Uniqueness status: Recorded as `UNIQUE_OPTIMUM_UNVERIFIED`.

---

## 5. Tolerance Governance

- **Continuous Tolerance ($\tau_{\text{cont}}$):** Left **STRICTLY UNSET** (`None`).
- **No Threshold Equivalence Claims:** Raw continuous deltas and $\|\Delta u_{0, \text{cont}}\|_\infty$ will be reported as continuous measurements in Watts. The harness will not declare actions "equivalent" or "non-equivalent" based on an unapproved threshold.

---

## 6. Execution Isolation & Security Controls

1. **Quarantined Scratch Execution:** All outputs, manifests, and solver logs will be written exclusively to `experiments/diagnostics/diag_od02_boundary_2024/`.
2. **Read-Only Data Ingestion:**
   - Ingestion restricted to approved 2024 historical files on the allow-list.
   - Pre-execution verification of input file SHA-256 hashes against pre-registered allow-lists.
3. **Quarantine Firewall vs. Physical Isolation:**
   - Token-based checks (rejecting `2025` and `blind` strings) serve as an **in-process defense-in-depth pre-filter**.
   - Token matching is **not presented as proof of physical filesystem isolation**.
   - Physical quarantine requires process-level sandboxing (e.g. read-only volume mounts excluding 2025 directories, or containerized execution boundaries). Under Gate B, zero filesystem reads exist in the harness code.
4. **Execution Manifest:** Immutable run manifest capturing Python environment, solver version, Git commit hash, input checksums, origin timestamps, and raw solution vectors.

---

## 7. Inferential Scope & Statistical Limitations

### 7.1 What the Proposed Diagnostic CAN Establish
- Proof of whether the GAP19 solver produces identical continuous dispatch allocations at step 0 under baseline OD-02 vs. perturbed inputs for the evaluated origins.
- Empirical quantification of the magnitude ($\text{W}$) of first-action sensitivity to terminal conditions.
- Direct measurement of whether terminal boundary conditions propagate to first-action variables under realistic constraint states.

### 7.2 What the Proposed Diagnostic CANNOT Establish
- **No Annual Performance / Diesel Claims:** Cannot establish annual fuel savings, cost reductions, or microgrid reliability metrics.
- **No Confirmatory Generalization:** $N=10$ origins serve strictly as an exploratory integration test and sensitivity probe; ten unchanged actions cannot prove general annual invariance across 8,760 hours.
- **No Degeneracy Proof:** Cannot prove that an action shift is physically forced rather than an alternative optimum without an authorized secondary tie-breaking protocol.
- **No Architectural Winner:** Cannot resolve whether Path A or Path B is superior; `winner: null` remains strictly frozen.

---

## 8. Technical Prerequisites & Verification Hierarchy

The diagnostic lifecycle enforces a strict separation across three verification levels:

1. **Level 1 — Metadata Verification (Completed under Gate B):**
   - Confirms origin timestamps, astronomical solar geometry, and schema compatibility using frozen partition indexes (`POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv`).
   - Does NOT run solvers, predictions, or simulations.

2. **Level 2 — Static Unit Testing (Completed under Gate B.3):**
   - Confirms harness transformation logic, bounds consistency, 4-tier objective extraction, production `GAP19HighsNativeOptimizer` interface wiring, and fail-closed firewall safeguards using synthetic in-memory mocks.
   - Does NOT invoke real solvers or load real dataset files.

3. **Level 3 — Diagnostic Execution (Requires Gate C Authorization):**
   - Invocation of production `GAP19HighsNativeOptimizer` on real historical origins.
   - **Gate C remains STRICTLY NOT AUTHORIZED.**
   - **Unresolved Technical Blockers for Gate C:**
     - *Variant 1:* Empirical coverage limitation of persistence tail padding ($E[23] = E[22]$) has no 90% conformal calibration at horizon 25.
     - *Variant 2:* Candidate solar estimators (2A clear-sky continuation, 2B persistent attenuation) require online clear-sky irradiance at horizon 25 and plant conversion factor $K_{\text{pv}}$, which are not available in runtime `ForecastBundle`.
     - *Variant 3:* Inherits all unresolved blockers of V1 and V2.
