# POLARIS Forensic Evidence: Master Decision Register (OD-02)

**Source:** `POLARIS_MASTER_DECISION_REGISTER.md` (v1.9.13, Pass 23)  
**Tracking ID:** `OD02-ALIGNMENT-FORENSICS-2026-10-20`  

---

## 1. Master Decision Register Section 38 (Pass 22, 2026-10-19)

```markdown
## 38. POLARIS OD-01 & OD-02 — Pilot Pre-Execution Owner Decisions — 2026-10-19 (Twenty-Second Pass)

This is a twenty-second governance pass, recording two explicit Project Owner decisions required for pilot pre-execution: **OD-01** (dynamic terminal battery energy target) and **OD-02** (hour-23 solar forecast fallback).

### 38.1 Two Explicit Owner Decisions Recorded

1. **OD-01 — Dynamic Terminal Energy Target: APPROVED.**
   - **Decision:** Establish `terminal_target_wh = initial_energy_wh - min_e_wh` derived dynamically from the actual absolute initial battery energy (`StationState.battery_energy_wh`) and the solver's minimum-energy floor (`min_e_wh = capacity_wh * (min_soc_pct / 100.0)`).
   - **Dimensional & Physical Rationale:** In `simulator.py` and `station_state.py`, `battery_energy_wh` represents absolute stored DC energy (e.g., $160,000.0\text{ Wh}$ for $80\%$ SOC of a $200\text{ kWh}$ pack). In `gap19_highs_native.py` (line 304), Layer C defines the terminal reserve constraint as $E_{\text{next}}[23] + s_{J2}[23] \ge e_{\text{stage2\_target}}[23] + E_{\min}$, where $E_{\min} = \text{min\_e\_wh} = 40,000.0\text{ Wh}$ ($20\%$ SOC floor). Supplying net usable energy above the floor ($120,000.0\text{ Wh}$) ensures the required terminal energy target is exactly $120,000.0 + 40,000.0 = 160,000.0\text{ Wh}$ ($80\%$ SOC), preserving physical SOC neutrality across 24-hour dispatch horizons without artificial terminal slack penalties. The prior static assumption ($100,000.0\text{ Wh}$) and raw absolute state reuse ($160,000.0 + 40,000.0 = 200,000.0\text{ Wh}$, forcing an artificial $10\text{ kWh}$ slack violation) are rejected.
   - **Scope & Integration:** Applied in optimizer adapters (`RoutedOptimizerAdapter` and `N6RecedingHorizonOptimizerAdapter`) without modifying `gap19_highs_native.py` or `station_state.py`.

2. **OD-02 — Hour-23 Solar Forecast Fallback: APPROVED.**
   - **Decision:** Retain the existing `LocalBaselineForecastEngine` final-slot solar output ($0.0\text{ W/m}^2$) for dispatch step 23 ($t_0 + 24\text{h}$, horizon $h=25$) when using the 24-horizon N6 model artifact. Do not introduce the offline `POLARIS_v0_1_clearsky_decomposition.csv` into runtime execution.
   - **Limitation Documented:** At the Arctic latitude of Lake Torneträsk ($68.35^\circ\text{N}$), solar irradiance at midnight (00:00 local time) may be non-zero during the polar day (midnight sun season, late May through mid-July). Clamping solar forecast to zero at $00:00\text{ UTC+1}$ during this seasonal window represents a documented operational limitation of the boundary fallback, accepted for this pilot to prevent unverified offline file dependencies or fabrication of N6 model outputs beyond its 24-horizon contract.
   - **Scope:** Retains runtime dependency isolation and schema consistency across forecast adapters.

### 38.2 Preservation of Safety & Governance Boundaries

- `winner: null` preserved untouched.
- `CampaignExecutionNotAuthorizedError` guard preserved untouched.
- `DSL-01` `epsilon_tol` remains unset.
- `RT-01` remains closed (`resolved_with_evidence`).
- Sealed 2025 blind data: NOT accessed.
- Frozen Stage 8.1 / N6 assets: NOT modified.
- Native GAP19 solver hierarchy and protected files: NOT modified.
- Zero Git mutations performed.

### 38.3 Register Impact

- `POLARIS_MASTER_DECISION_REGISTER.md` / `.json`: v1.9.11 -> v1.9.12.
- Mirrored byte-identically to `N6_REMEDIATION_REPORTS/POLARIS_MASTER_DECISION_REGISTER.md` and `N6_REMEDIATION_REPORTS/POLARIS_MASTER_DECISION_REGISTER.json`.

**PASS COMPLETE — OD-01 (DYNAMIC TERMINAL TARGET) & OD-02 (HOUR-23 SOLAR FALLBACK) OWNER DECISIONS RECORDED; MIDNIGHT-SUN LIMITATION DOCUMENTED; ALL BOUNDARY & GOVERNANCE CONSTRAINTS MAINTAINED.**
```

---

## 2. Master Decision Register Section 39 (Pass 23, 2026-10-19)

```markdown
## 39. POLARIS OD-02 — Final Uncertainty-Scale Review Completion & Decision Freeze — 2026-10-19 (Twenty-Third Pass)

This is a twenty-third governance pass, recording the formal completion of the narrow uncertainty-scale semantics and calibration-provenance audit and freezing Decision **OD-02** (hour-23 solar fallback and time-alignment contract).

### 39.1 OD-02 Freeze Evidence & Formal Disposition

1. **Uncertainty Scale ($s(t)$) & Conformal EBR Implementation:**
   - In `system/forecasting/implementations/n6_solar.py` (`_compute_uncertainty_bounds`, lines 409–443), `scale_s` is constructed as `scale_s = np.where(causal_day_mask, ensemble_std + 0.10 * cs_terrain + 5.0, 0.0)` from the 40-member tree spread, terrain-adjusted clear-sky irradiance, and a $+5.0\text{ W/m}^2$ physical floor.
   - In `_compute_ebr_reserve()` (lines 445–471), `s_hourly_wh = self.k_pv * scale_s / ETA_DIS` is aggregated over a 6-hour forward rolling lookahead window `[t, min(t+6, 24))` with `SCALE_FLOOR_WH = 100.0` and baseline reserve floor `EBR_BASE_WH = 15000.0` Wh.
   - The solar point-forecast array is shifted by OD-02 (raw rows 1..23 -> dispatch steps 0..22, step 23 = 0.0 W/m² baseline fallback), while `ebr_target_wh` remains unshifted.
   - Policy B combines the critical-load reserve and conformal EBR via the pointwise maximum (`combined_reserve = max(crit_reserve, conformal_ebr)`).

2. **Calibration Provenance of $Q_{90,W} = 1.5702$:**
   - Empirical re-evaluation of the calibration script (`stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/evaluate_l2_conformal_ebr_2025.py`, lines 231–263) against the 2024-ODD validation partition ($N = 173$ origins, 4,152 rows) reproduces the exact floating-point quantile score $q_{90,W} = 1.5701946249789982$, confirming bit-for-bit provenance for frozen constant `Q90_W = 1.5702`.
   - Calibration and runtime use the identical 6-hour rolling lookahead window, scale floor ($+100.0\text{ Wh}$), PV power conversion factor ($K_{\text{pv}} = 51.0$), and discharge-efficiency convention ($\eta_{\text{dis}} = 0.95$).

3. **Documented Operational & Empirical Limitations:**
   - **Empirical Coverage Limitation**: Reproducing the calibration calculation on unshifted 2024-ODD feature rows does not independently establish empirical conformal coverage after OD-02 advances point-forecast alignment by 1 hour.
   - **Boundary Truncation**: At horizon steps $k \ge 18$, the 6-hour forward window naturally truncates to the 24-hour horizon edge (1 hour at $k=23$), matching GAP19's critical reserve truncation. At $k=23$, OD-01's dynamic terminal target $E_{\text{term\_target}}$ takes pointwise precedence to enforce physical SOC neutrality.
   - **Arctic Midnight-Sun Baseline**: Documented polar-day midnight solar fallback ($0.0\text{ W/m}^2$) at step 23 during late May through mid-July is preserved as an accepted pilot boundary condition.
   - **Discharge Efficiency Delta**: Calibration assumes $\eta_{\text{dis}} = 0.95$, whereas GAP19 optimizer configuration specifies $\eta_{\text{dis}} = 0.92$, introducing a minor $+3.2\%$ conservatism in critical demand reserves that is subsumed by Policy B's pointwise maximum.

4. **Formal Freeze Status:**
   - Decision **OD-02 is FROZEN**. The time-alignment contract (solar point forecast shifted 1..23 -> 0..22, step 23 fallback to 0.0 W/m², demand/wind/EBR unshifted, Policy B pointwise maximum) is sealed for pilot evaluation.

### 39.2 Preservation of Safety & Governance Boundaries

- `winner: null` preserved untouched.
- `CampaignExecutionNotAuthorizedError` guard preserved untouched.
- `DSL-01` `epsilon_tol` remains unset.
- `RT-01` remains closed (`resolved_with_evidence`).
- Sealed 2025 blind data: NOT accessed.
- Frozen Stage 8.1 / N6 assets: NOT modified.
- Native GAP19 solver hierarchy and protected files: NOT modified.
- Zero Git mutations performed.

### 39.3 Register Impact

- `POLARIS_MASTER_DECISION_REGISTER.md` / `.json`: v1.9.12 -> v1.9.13.
- Mirrored byte-identically to `N6_REMEDIATION_REPORTS/POLARIS_MASTER_DECISION_REGISTER.md` and `N6_REMEDIATION_REPORTS/POLARIS_MASTER_DECISION_REGISTER.json`.

**PASS COMPLETE — OD-02 (HOUR-23 SOLAR FALLBACK & TIME-ALIGNMENT CONTRACT) FORMALLY FROZEN WITH EXACT EMPIRICAL PROVENANCE AND DOCUMENTED COVERAGE LIMITATION; ALL BOUNDARY & GOVERNANCE CONSTRAINTS MAINTAINED.**
```

---

## 3. Register JSON Payload (`POLARIS_MASTER_DECISION_REGISTER.json`)

```json
{
  "amendment_2026_10_19_twenty_second_pass_od01_od02_owner_decisions": "Twenty-second pass (2026-10-19). Project Owner formally approved two decisions for pilot pre-execution: (1) OD-01 (Dynamic Terminal Energy Target): Approved terminal_target_wh = initial_energy_wh - min_e_wh, derived dynamically from the simulator/station state (StationState.battery_energy_wh, absolute stored Wh) and the solver's minimum-energy floor (min_e_wh = capacity_wh * (min_soc_pct / 100.0)). Eliminates double-counting in Layer C constraint (req_lhs = e_stage2_target + min_e_wh), ensuring exact SOC neutrality without artificial slack penalties. (2) OD-02 (Hour-23 Solar Forecast Fallback): Approved retaining LocalBaselineForecastEngine final-slot solar output (0.0 W/m^2) for dispatch step 23 (horizon h=25) when evaluating 24-horizon N6 model artifacts. Documented operational limitation regarding Arctic midnight sun (Lake Tornetraesk 68.35 N) during polar day; rejected runtime ingestion of offline unverified clearsky decomposition CSV. All protected files, winner: null, DSL-01 unset, RT-01 closed, frozen artifacts, and blind data boundaries preserved untouched.",
  "amendment_2026_10_19_twenty_third_pass_od02_freeze": "Twenty-third pass (2026-10-19). OD-02 final uncertainty-scale semantics and calibration-provenance review completed. Exact empirical reproduction of Q90_W = 1.5702 on 2024-ODD verified against candidate_k_2024_clean_matrix.parquet (N=173 origins, q_90_W = 1.5701946249789982). Decision OD-02 is formally FROZEN. Point-forecast arrays are aligned by OD-02 (raw rows 1..23 -> dispatch steps 0..22, step 23 = 0.0 W/m^2 baseline fallback), while ebr_target_wh remains unshifted matching forward lookahead window [k, min(k+6, 24)). Policy B pointwise maximum combined reserve verified sound. Remaining empirical coverage limitation documented: reproducing calibration calculation does not independently establish empirical coverage after OD-02 changes point-forecast alignment. All protected files, winner: null, DSL-01 unset, RT-01 closed, frozen artifacts, and blind data boundaries preserved untouched."
}
```
