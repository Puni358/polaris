# POLARIS — Information Bottleneck Forensic Report

**Scope.** Read-only review of existing artifacts and an EVEN-only aggregation of the frozen `REAL_AROME_21X21_REPRODUCIBLE_CONTROL_PREDICTIONS.csv`. No model was trained, no route was changed, no data was fetched, and no ODD prediction rows were loaded or analysed. The protected ODD benchmark remains as stated in the brief.

## Finding

**Final classification: INFORMATION-LIMITED.**

The most likely remaining bottleneck is missing **forecast-time information about the local cloud field's future phase/evolution**—especially whether clouds will arrive, clear, deform, or change optical depth over the site during the sunlit part of the next day. It is not established as a universal theoretical lower bound, but it is the strongest conclusion supported by the available artifacts. The evidence does **not** support blaming insufficient model capacity, a generic static-feature representation failure, or the evaluation protocol.

## 1. Where the error is

The EVEN control's daytime absolute error rises from H01 `7.9 W/m²` to H07 `53.5`, peaks at H11 `80.8` (H12 `72.6`, H13 `65.2`), then falls with declining daylight. The dominant practical regime is therefore **H09–H15 / roughly 3–12 hours**, centred on the high-solar middle of the forecast day—not immediate nowcasting and not the late, low-energy horizons. The same artifact contains only 151–157 daytime rows at H11–H13; this is descriptive, not an origin-bootstrap significance claim.

Error is strongly solar-regime dependent: the existing residual audit reports MAE rising from `22.6 W/m²` at solar elevation 0–15° to `106.2 W/m²` at 30–45°. This is consistent with a cloud-state mismatch becoming costly when clear-sky potential is high, rather than a pure night/day or metric artefact.

## 2. What the artifacts do and do not show about information decay

- **Historical SW_IN:** it carries no reliable signed correction signal after conditioning: context-feature/residual correlations were `|r| < 0.08`; an EVEN OOF residual predictor degraded MAE by `+0.214 W/m²` (Stage 4.5).
- **NWP cloud state/radiation/wind:** there is useful baseline signal—otherwise the control would not work—but residual error remains concentrated in high-solar cloud-transition conditions. Ensemble spread and component disagreement predict *error magnitude*, not error direction; signed residual association is near zero (`ρ=0.0697` for ensemble-spread audit). They cannot identify the next cloud outcome for an MAE correction.
- **Local spatial state:** it contains a real but modest incremental association. Corrected 3×3 local-state incremental R² is `+0.0106` in H4–H6 (n=519, p=`6.34e-05`), `+0.0059` in H7–H12, `+0.0135` in H13–H18, and `+0.0140` in H19–H24. Higher-order temporal/structural spatial descriptors add ≤`0.0025` in these grouped analyses. This is evidence of **some** represented local information, not evidence that it is sufficient or operationally useful.
- **Terrain, LWP/IWP, and vertical/optical proxies:** the current artifacts show tested formulations were not robustly useful. They do not establish that the underlying physics is irrelevant.

A per-source, per-horizon information-decay curve for every listed source is **NOT IDENTIFIABLE FROM CURRENT ARTIFACTS**: there is no uniformly matched, EVEN-only per-horizon ablation archive for all of them.

## 3. State aliasing and predictability ceiling

Direct nearest-neighbour/matched-state trajectory-divergence results are **NOT IDENTIFIABLE FROM CURRENT ARTIFACTS**. No saved diagnostic compares near-identical complete causal states with their realised future SW_IN trajectories, so a quantitative irreducible conditional variance cannot honestly be estimated.

The indirect evidence nonetheless points in the same direction: hard cases occur across all NWP cloud regimes, forecast-time hard-case classification has only PR-AUC about `0.35` at a 7.28% base rate, and causal residual corrections fail out-of-fold. Adjacent within-origin residuals correlate about `r≈0.45`, while non-overlapping daily-origin residual persistence is approximately zero (`−0.049`); this is consistent with transient forecast phase errors rather than a stable, reusable bias.

## 4. Cloud evolution, scale, and alignment

The strongest candidate mechanism is **cloud timing/phase plus formation–dissipation/deformation**, not simple rigid cloud motion. In the causal AROME trajectory audit, whole-field persistence had mean NCC `0.5206`, estimated translation `0.5058`, 10-m wind `0.4259`, and 700-hPa wind `0.2818`; translation did not beat persistence beyond H1–H3. Its real upwind-cloud correlation with error (`ρ=−0.1075`) did not beat its randomized-vector null (`ρ=−0.1077`). Thus fixed advection is not the missing solution.

The likely unresolved scale is **local-to-mesoscale cloud evolution (roughly <10 to 100 km)** at **1–12 hours**, with greatest impact in H09–H15. The artifacts do not isolate a single kilometre scale, nor distinguish cloud optical depth from sub-grid structure conclusively. “Minutes” and “12–24 hours” as dominant missing scales are **NOT IDENTIFIABLE FROM CURRENT ARTIFACTS**.

## 5. Why model capacity is not the primary diagnosis

Increasing extraction/architecture complexity has repeatedly failed on EVEN data under matched controls:

- Local 3×3 spatial model: `+3.020 W/m²` MAE versus control; only 2/5 folds improved.
- Topology-preserving CNN–GRU: `+15.835 W/m²`; 0/5 folds improved.
- BiGRU: 0/5 folds improved and materially worse.
- Shared horizon-embedding MLP: mean `−0.356 W/m²`, but only 2/5 folds improved and worst degradation `+1.259 W/m²`.
- Disagreement-gated residual MLP: `+0.642 W/m²`; 1/5 folds improved.
- Residual/history correction: no robust MAE improvement.

This is enough evidence to make a generic “larger model” explanation unlikely. It does not prove no model can exploit any currently available signal; the small local-spatial associations and unstable shared-MLP result rule out that absolute claim.

## 6. Ranked bottlenecks

1. **Absent local cloud-evolution/phase information** — **strong, medium confidence; H09–H15; absent/unresolved.** Large high-solar errors, weak signed residual predictors, failure of rigid translation, and instability of residual corrections converge here.
2. **Limited fidelity of available cloud representation at local/mesoscale scale** — **moderate, medium confidence; H04–H18; partly absent and partly misrepresented.** Spatial state adds modest diagnostic information, but static neighbourhood and topology-preserving routes do not convert it into robust forecasts.
3. **Unresolved cloud optical/deformation/formation–dissipation process** — **moderate-to-weak, low confidence; 1–12 h; NOT IDENTIFIABLE as a unique mechanism.** Existing tests reject their particular proxies, not this physical process itself.
4. **Model extraction limitations** — **weak as primary cause, medium confidence; all horizons.** Some signal remains, but several materially different models fail, so this is secondary.
5. **Evaluation/split/metric defect** — **weak, medium confidence.** Grouped EVEN controls, causal audits, and consistent closed-route failures provide no evidence that the bottleneck is protocol-created.

## Decision

POLARIS is **INFORMATION-LIMITED** in the operative sense: its causal inputs do not reliably resolve the future local cloud trajectory that determines high-solar irradiance. The current record supports an operational predictability ceiling, not a proven physical lower bound. A full conditional-variance/aliasing estimate remains **NOT IDENTIFIABLE FROM CURRENT ARTIFACTS** and should not be inferred from the correlations above.

### Evidence artifacts

- `spatial_arome_research/REAL_AROME_21X21_REPRODUCIBLE_CONTROL_PREDICTIONS.csv` (EVEN-only control aggregation)
- `spatial_arome_research/CORRECTED_CAUSAL_LOCAL_SPATIAL_STATE_INFORMATION_AUDIT.json`
- `spatial_arome_research/CAUSAL_AROME_CLOUD_TRAJECTORY_CONSISTENCY_AUDIT.json`
- `spatial_arome_research/LOCAL_SPATIAL_3X3_EXPERIMENT_RESULTS.json`
- `spatial_arome_research/TOPOLOGY_PRESERVING_AROME_EVEN_TRAINING_RESULTS.json`
- `spatial_arome_research/PHASE10_FINAL_CLOSURE_CHECKPOINT.json`
- `stage4/stage4_5_residual_predictability/final_summary.txt`
- `stage4/stage4_6_causal_residual_audit/final_summary.txt`
