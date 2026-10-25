#!/usr/bin/env python3
"""
POLARIS Presentation Graph Generation Script
Generates presentation-ready, high-resolution PNG graphs and a combined PDF
grounded strictly in recorded repository evidence.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages

# Configure high quality matplotlib style
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 16

OUTPUT_DIR = "docs/presentation/polaris_results_20261013"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Color palette adhering to governance tagging
COLOR_VALIDATED = "#1f77b4"      # Blue: Validated / Control
COLOR_FAILED = "#d62728"         # Red: Failed bar / Regression
COLOR_CONTAMINATED = "#ff7f0e"   # Orange: Contaminated / Target leakage
COLOR_DIAGNOSTIC = "#7f7f7f"     # Gray: Diagnostic / Noncausal Oracle
COLOR_ACCENT = "#2ca02c"         # Green: Approved stage progression

# ==============================================================================
# GRAPH A: MODEL LEADERBOARD (2025 BLIND EVALUATION)
# ==============================================================================
def generate_graph_a():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9), gridspec_kw={'width_ratios': [1.2, 1]})
    fig.patch.set_facecolor('#ffffff')

    models = [
        "Stage 8.1 Corrected\n(Frozen Control)",
        "Candidate C\n(Horizon Buckets)",
        "Candidate D\n(OOF Residual)",
        "Candidate E\n(144-Grid HPO)",
        "Phase 3 Weighting\n(Elevation Weighted)",
        "Candidate F\n(Elevation × Cloud)",
        "Candidate G\n(F + Trans. Flag)",
        "Candidate H\n(Quantile Loss)",
        "Candidate I\n(Targeted Resid.)",
        "Candidate J\n(F + Joint Regime)"
    ]

    mae_values = [35.9745, 36.3793, 36.0656, 35.7928, 35.8626, 35.4948, 35.5386, 36.3222, 35.5239, 35.3036]
    delta_mae = [0.0, +0.4048, +0.0911, -0.1817, -0.1119, -0.4797, -0.4359, +0.3477, -0.4506, -0.6709]
    bias_values = [+4.0802, +5.1031, +1.1394, +5.3735, +5.1920, +3.6959, +3.8765, -10.3269, +4.8951, +3.6640]
    
    tags = [
        "VALIDATED CONTROL",
        "VALIDATED (FAILED)",
        "VALIDATED (OVERFIT)",
        "VALIDATED (NOT SIG.)",
        "VALIDATED (NOT SIG.)",
        "CONTAMINATED / NOT CLEAN",
        "CONTAMINATED / REDUNDANT",
        "VALIDATED (BIAS OVERSHOOT)",
        "VALIDATED (NOT SIG.)",
        "CONTAMINATED (INHERITED)"
    ]

    colors = [
        COLOR_VALIDATED,
        COLOR_FAILED,
        COLOR_FAILED,
        "#aec7e8",
        "#aec7e8",
        COLOR_CONTAMINATED,
        COLOR_CONTAMINATED,
        COLOR_FAILED,
        COLOR_FAILED,
        COLOR_CONTAMINATED
    ]

    y_pos = np.arange(len(models))

    # Panel 1: Blind MAE comparison
    bars = ax1.barh(y_pos, mae_values, color=colors, height=0.65, edgecolor='black', linewidth=0.8)
    ax1.axvline(35.9745, color=COLOR_VALIDATED, linestyle='--', linewidth=1.5, label='Control Baseline (35.97 W/m²)')
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(models, fontweight='semibold')
    ax1.invert_yaxis()
    ax1.set_xlabel("Daytime MAE (W/m²) [Lower is Better]")
    ax1.set_xlim(34.0, 37.5)
    ax1.set_title("2025 Blind Evaluation — Daytime MAE (n = 5,978)")
    ax1.grid(axis='x', linestyle=':', alpha=0.6)

    for i, bar in enumerate(bars):
        w = bar.get_width()
        d_str = f"{delta_mae[i]:+.2f}" if i > 0 else "Ref"
        ax1.text(w + 0.05, bar.get_y() + bar.get_height()/2, f"{w:.2f} W/m² ({d_str})",
                 va='center', ha='left', fontsize=9, fontweight='bold')

    # Panel 2: Mean Bias and Governance Status
    bars2 = ax2.barh(y_pos, bias_values, color=colors, height=0.65, edgecolor='black', linewidth=0.8)
    ax2.axvline(0, color='black', linestyle='-', linewidth=0.8)
    ax2.axvline(4.0802, color=COLOR_VALIDATED, linestyle='--', linewidth=1.2, label='Control Bias (+4.08 W/m²)')
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([])
    ax2.invert_yaxis()
    ax2.set_xlabel("Daytime Mean Bias (W/m²) [Ideal = 0]")
    ax2.set_xlim(-12.0, 7.0)
    ax2.set_title("Forecast Bias & Governance Validity Tag")
    ax2.grid(axis='x', linestyle=':', alpha=0.6)

    for i, bar in enumerate(bars2):
        w = bar.get_width()
        tag = tags[i]
        offset = 0.2 if w >= 0 else -0.2
        ha = 'left' if w >= 0 else 'right'
        ax2.text(w + offset, bar.get_y() + bar.get_height()/2, f"{w:+.2f} | {tag}",
                 va='center', ha=ha, fontsize=8.5, fontweight='bold',
                 color='#900C3F' if 'CONTAMINATED' in tag else ('#0C3F90' if 'CONTROL' in tag else '#333333'))

    # Governance Warning Banner
    fig.text(0.5, 0.02,
             "GOVERNANCE DECISION: winner: null | No model promoted to production.\n"
             "Candidate F & J improvements (-0.48 to -0.67 W/m²) are contaminated by 2025-EVEN ensemble parameters fitted on realized 2025 targets.\n"
             "Source: forecasting/stage7/stage8/stage8_1_station_tuning_research/ (CANDIDATE_RESULTS.json, TARGETED_CANDIDATE_F_CAUSALITY_TRAINING_INTEGRITY_AUDIT.md)",
             ha='center', fontsize=10, bbox=dict(boxstyle='square,pad=0.5', facecolor='#fff2f2', edgecolor='#d62728', linewidth=1.5))

    plt.suptitle("GRAPH A: POLARIS Solar Forecasting Model Leaderboard (2025 Blind Holdout)", fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0.08, 1, 0.95])
    out_path = os.path.join(OUTPUT_DIR, "graph_a_model_leaderboard.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Generated {out_path}")

# ==============================================================================
# GRAPH B: IMPROVEMENT ACROSS PROJECT STAGES (2024-ODD BENCHMARK)
# ==============================================================================
def generate_graph_b():
    fig, ax1 = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor('#ffffff')

    stages = [
        "Stage 5.2\n(Control Pipeline)",
        "Stage 6.6\n(+ LWP / IWP Microphysics)",
        "Stage 7.5\n(+ Terrain & Horizon Mask)",
        "Stage 8.1 (Original)\n(+ 700 hPa Wind Advection)",
        "Stage 8.1 Corrected\n(Causal Demarcation Freeze)"
    ]

    mae = [39.0848, 37.0059, 36.6098, 36.1887, 36.2040]
    rmse = [68.9935, 65.6717, 65.3287, 64.2195, 64.5752]
    nmae = [30.32, 28.70, 28.40, 28.07, 28.08]

    x = np.arange(len(stages))
    width = 0.35

    bars1 = ax1.bar(x - width/2, mae, width, label='Daytime MAE (W/m²)', color='#1f77b4', edgecolor='black', linewidth=0.8)
    bars2 = ax1.bar(x + width/2, rmse, width, label='Daytime RMSE (W/m²)', color='#aec7e8', edgecolor='black', linewidth=0.8)

    ax1.set_ylabel('Daytime Metric (W/m²) [Lower is Better]', fontweight='bold')
    ax1.set_title('Evolution of Forecast Error Across Engineering Stages (2024 Held-Out ODD Split, n = 2,883)', pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(stages, fontweight='semibold')
    ax1.set_ylim(25, 75)
    ax1.grid(axis='y', linestyle=':', alpha=0.6)

    # Data labels on bars
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval + 0.6, f"{yval:.2f}", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#0b3c61')
    for bar in bars2:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval + 0.6, f"{yval:.2f}", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#4a6882')

    # Incremental improvement annotations
    deltas = [
        "",
        "ΔMAE: -2.08 W/m² (-5.3%)\n95% CI [-2.81, -1.34]",
        "ΔMAE: -0.74 W/m² (-2.0%)\n95% CI [-1.38, -0.11]",
        "ΔMAE: -0.42 W/m² (-1.2%)\n95% CI [-0.89, +0.03]",
        "Causal Retraining\nMAE: 36.20 W/m² (Frozen)"
    ]

    for i in range(1, len(stages)):
        ax1.annotate(deltas[i],
                     xy=(x[i] - width/2, mae[i]),
                     xytext=(x[i] - width/2, mae[i] - 4.5),
                     ha='center', fontsize=8.5, fontweight='bold',
                     bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffffcc', edgecolor='#cccc00', alpha=0.9))

    # Total improvement callout box
    total_text = (
        "CUMULATIVE PROGRAM IMPROVEMENT:\n"
        "• Baseline (Stage 5.2): 39.08 W/m² MAE | 68.99 W/m² RMSE\n"
        "• Production Control (Stage 8.1): 36.20 W/m² MAE | 64.58 W/m² RMSE\n"
        "• Total Validated Reduction: -2.88 W/m² MAE (-7.37%) | -4.42 W/m² RMSE (-6.41%)\n"
        "• Evaluated strictly on identical held-out 2024-ODD origins (173 origins, 2,883 daytime hours)"
    )
    ax1.text(0.02, 0.96, total_text, transform=ax1.transAxes, verticalalignment='top',
             fontsize=9.5, bbox=dict(boxstyle='square,pad=0.5', facecolor='#e8f4f8', edgecolor='#1f77b4', linewidth=1.5))

    ax1.legend(loc='upper right', framealpha=0.9)

    fig.text(0.5, 0.02,
             "Sources: forecasting/stage6/stage6_6_lwp_iwp/odd_evaluation_results.json, forecasting/stage7/stage7_5_terrain_horizon/stage7_5_official_odd_results.json,\n"
             "forecasting/stage7/stage8/stage8_1_700hpa_wind/stage8_1_official_odd_results.json, forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_CORRECTED_official_odd_results_2024.json",
             ha='center', fontsize=9, color='#555555')

    plt.suptitle("GRAPH B: Measured Accuracy Improvements Across POLARIS Project Stages", fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    out_path = os.path.join(OUTPUT_DIR, "graph_b_stage_improvements.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Generated {out_path}")

# ==============================================================================
# GRAPH C: FEATURE ENGINEERING IMPACT
# ==============================================================================
def generate_graph_c():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9))
    fig.patch.set_facecolor('#ffffff')

    features = [
        "Cloud Microphysics\n(LWP & IWP pl)",
        "Topography & Horizon\n(Shadows & Terrain)",
        "Upper-Air Steering Wind\n(700 hPa u & v advection)",
        "Solar × Cloud Interaction\n(Candidate F: elev × cld)",
        "Transition Cloud Flag\n(Candidate G: 0.2 ≤ cld < 0.6)"
    ]

    mae_reductions = [2.0789, 0.7351, 0.4249, 0.7602, -0.0438] # positive means reduction in MAE
    ci_lower = [1.3448, 0.1059, -0.0264, 0.2338, -0.1258]
    ci_upper = [2.8098, 1.3770, 0.8880, 0.7307, 0.4354]
    
    status_tags = [
        "VALIDATED METRICS\n(00Z Latency Caveat)",
        "VALIDATED PHYSICS\n(Causal Terrain Mask)",
        "VALIDATED DYNAMICS\n(NaNs at H20-24 Disclosed)",
        "CONTAMINATED\n(Target Leakage in 2025)",
        "REDUNDANT\n(No Gain over F)"
    ]

    colors = [COLOR_VALIDATED, COLOR_VALIDATED, COLOR_VALIDATED, COLOR_CONTAMINATED, COLOR_FAILED]

    y_pos = np.arange(len(features))

    # Panel 1: Measured MAE Reduction
    bars = ax1.barh(y_pos, mae_reductions, color=colors, height=0.55, edgecolor='black', linewidth=0.8)
    ax1.axvline(0, color='black', linestyle='-', linewidth=0.8)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(features, fontweight='semibold')
    ax1.invert_yaxis()
    ax1.set_xlabel("Measured Daytime MAE Reduction (W/m²) [Higher is Better]")
    ax1.set_title("Controlled Feature Group Interventions (Measured ΔMAE)")
    ax1.grid(axis='x', linestyle=':', alpha=0.6)

    for i, bar in enumerate(bars):
        w = bar.get_width()
        ha = 'left' if w >= 0 else 'right'
        offset = 0.05 if w >= 0 else -0.05
        ax1.text(w + offset, bar.get_y() + bar.get_height()/2, f"+{w:.2f} W/m²" if w >= 0 else f"{w:.2f} W/m²",
                 va='center', ha=ha, fontsize=9.5, fontweight='bold')

    # Panel 2: Scientific & Governance Classification
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([])
    ax2.invert_yaxis()
    ax2.set_xlim(0, 10)
    ax2.set_xticks([])
    ax2.set_title("Feature Details, Audit Verification & Governance Caveats")

    for i, (feat, tag, color) in enumerate(zip(features, status_tags, colors)):
        # Box for each feature
        box = patches.FancyBboxPatch((0.2, i - 0.35), 9.6, 0.7, boxstyle="round,pad=0.1",
                                     edgecolor=color, facecolor='#fafafa' if color != COLOR_CONTAMINATED else '#fff8f0',
                                     linewidth=1.5)
        ax2.add_patch(box)
        
        detail_text = ""
        if i == 0:
            detail_text = "Input: mass_fraction of condensed water & ice (MEPS). Delta: -2.08 W/m² (-5.3%).\nCaveat: Operational 00Z issuance has ~135 min latency; 18Z causal replacement proven feasible."
        elif i == 1:
            detail_text = "Input: Solar elevation vs terrain horizon profile (4 features). Delta: -0.74 W/m² (-2.0%).\nAudit: Rebuilt in Stage 8.1 Corrected to eliminate lookahead indices."
        elif i == 2:
            detail_text = "Input: 700 hPa u/v wind vectors from MEPS (2 features). Delta: -0.42 W/m² (-1.2%).\nDisclosed Limitation: Inherits NaNs at forecast horizons 20-24."
        elif i == 3:
            detail_text = "Input: solar_elevation × cloud_frac interaction. Reported Blind Delta: -0.48 W/m².\nFATAL AUDIT: 2025 ensemble parameters fitted on 2025 realized targets. Status: Contaminated."
        elif i == 4:
            detail_text = "Input: Binary flag for cloud_frac in [0.2, 0.6). Delta vs Control: -0.44 W/m².\nResult: Redundant with F; fails to outperform F's point estimate; bias trade-off in subregime."

        ax2.text(0.4, i - 0.15, tag.replace('\n', ' — '), fontsize=9, fontweight='bold', color=color)
        ax2.text(0.4, i + 0.12, detail_text, fontsize=8, color='#333333')

    fig.text(0.5, 0.02,
             "Key Safeguard: Do not attribute causal importance to multi-change experiments. Tagged strictly per repository audit findings.\n"
             "Source: stage6_6 odd_evaluation_results.json, stage7_5 official_odd_results.json, stage8_1 official_odd_results.json, TARGETED_CANDIDATE_F_CAUSALITY_TRAINING_INTEGRITY_AUDIT.md",
             ha='center', fontsize=9, color='#555555')

    plt.suptitle("GRAPH C: POLARIS Feature Engineering Impact and Scientific Validity", fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0.06, 1, 0.95])
    out_path = os.path.join(OUTPUT_DIR, "graph_c_feature_engineering_impact.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Generated {out_path}")

# ==============================================================================
# GRAPH D: FORECAST PERFORMANCE (DIURNAL HORIZON ERROR TRAJECTORY)
# ==============================================================================
def generate_graph_d():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9))
    fig.patch.set_facecolor('#ffffff')

    # Load recorded per-horizon metrics from the frozen 2025 blind results
    horizon_csv = "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_CORRECTED_2025_blind_horizon_metrics.csv"
    df_h = pd.read_csv(horizon_csv)

    horizons = df_h['horizon_hour'].values
    mae_h = df_h['mae'].values
    rmse_h = df_h['rmse'].values
    bias_h = df_h['bias'].values
    actual_mean_h = df_h['mean_actual'].values

    # Panel 1: Error metrics vs Horizon
    ax1.plot(horizons, mae_h, marker='o', color='#1f77b4', linewidth=2, label='Daytime MAE (W/m²)')
    ax1.plot(horizons, rmse_h, marker='s', color='#aec7e8', linewidth=1.5, linestyle='--', label='Daytime RMSE (W/m²)')
    ax1.plot(horizons, bias_h, marker='^', color='#ff7f0e', linewidth=2, label='Daytime Bias (W/m²)')
    ax1.axhline(0, color='gray', linestyle=':', linewidth=1)

    # Highlight solar noon peak
    ax1.axvspan(10, 14, color='#fff2cc', alpha=0.5, label='Solar Noon Window (Peak Irradiance)')

    # Highlight Horizons 20-24 limitation
    ax1.axvspan(19.5, 24.5, color='#ffe6e6', alpha=0.6, label='H20–H24: Inherited u700/v700 NaNs')

    ax1.set_xlabel('Forecast Horizon (Hour 1 to 24)', fontweight='bold')
    ax1.set_ylabel('Metric (W/m²)', fontweight='bold')
    ax1.set_title('2025 Blind Holdout: Per-Horizon Error & Bias Profile (n = 5,978)')
    ax1.set_xticks(range(1, 25))
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='upper left', framealpha=0.9, fontsize=9)

    # Annotate peak error
    ax1.annotate(f"Peak MAE: 64.08 W/m²\nPeak Bias: +17.66 W/m²\nat Horizon 12 (Noon)",
                 xy=(12, 64.08), xytext=(12, 80),
                 arrowprops=dict(facecolor='black', arrowstyle='->', lw=1),
                 ha='center', fontsize=9, fontweight='bold',
                 bbox=dict(boxstyle='round,pad=0.3', facecolor='#ffffcc', edgecolor='#cccc00'))

    # Panel 2: Sample Time Series from Actual 2025 Blind Predictions CSV
    pred_csv = "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_CORRECTED_2025_blind_predictions.csv"
    df_p = pd.read_csv(pred_csv)
    df_p['timestamp'] = pd.to_datetime(df_p['timestamp'])

    # Pick a clean 5-day window in June (high solar activity): June 10 - June 14, 2025
    sample_mask = (df_p['timestamp'] >= '2025-06-10') & (df_p['timestamp'] <= '2025-06-14') & (df_p['horizon_hour'] == 12)
    # Actually, take a continuous 72-hour slice of actual vs predicted across continuous timestamps
    # For unique valid times: take origin 2025-06-10 00:00:00 and 2025-06-11 00:00:00
    slice_df = df_p[(df_p['forecast_start'] == '2025-06-10 00:00:00+00:00')].sort_values('horizon_hour')
    slice_df2 = df_p[(df_p['forecast_start'] == '2025-06-11 00:00:00+00:00')].sort_values('horizon_hour')
    slice_df3 = df_p[(df_p['forecast_start'] == '2025-06-12 00:00:00+00:00')].sort_values('horizon_hour')
    combined_slice = pd.concat([slice_df, slice_df2, slice_df3])

    ax2.plot(combined_slice['timestamp'], combined_slice['actual_SW_IN'], label='Actual SITES SW_IN (W/m²)', color='#2ca02c', linewidth=2)
    ax2.plot(combined_slice['timestamp'], combined_slice['pred_stage8_1_CORRECTED_blind2025'], label='Predicted Stage 8.1 Corrected (W/m²)', color='#1f77b4', linewidth=1.8, linestyle='--')
    ax2.plot(combined_slice['timestamp'], combined_slice['pred_stage3b_cloud_nwp'], label='Stage 3b Cloud-NWP Prior', color='#7f7f7f', linewidth=1, linestyle=':')

    ax2.set_xlabel('Valid Time (UTC)', fontweight='bold')
    ax2.set_ylabel('Global Downwelling Solar SW_IN (W/m²)', fontweight='bold')
    ax2.set_title('Representative Forecast Trajectory (3 Consecutive 24h Cycles, June 2025)')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.legend(loc='upper right', framealpha=0.9, fontsize=9)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=30, ha='right')

    # Add annotation on daylight tracking
    ax2.text(0.03, 0.95, "Real Measurement Trace (June 10–12, 2025):\n• Tracks diurnality and clear-sky peak\n• Conservative night gating (exact 0.0 W/m² at night)\n• Midday overprediction observable during cloud transients",
             transform=ax2.transAxes, verticalalignment='top', fontsize=9,
             bbox=dict(boxstyle='square,pad=0.4', facecolor='#f7f7f7', edgecolor='#cccccc'))

    fig.text(0.5, 0.02,
             "Disclosed Limitation: MEPS u700/v700 features carry inherited NaNs at horizons 20-24 due to upstream lead-time truncation.\n"
             "Source: forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_CORRECTED_2025_blind_horizon_metrics.csv & stage8_1_CORRECTED_2025_blind_predictions.csv",
             ha='center', fontsize=9, color='#555555')

    plt.suptitle("GRAPH D: POLARIS Solar Forecasting Performance Across Horizons and Time", fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    out_path = os.path.join(OUTPUT_DIR, "graph_d_forecast_performance_horizons.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Generated {out_path}")

# ==============================================================================
# GRAPH E: ERROR DISTRIBUTION & REGIME ROBUSTNESS
# ==============================================================================
def generate_graph_e():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9))
    fig.patch.set_facecolor('#ffffff')

    pred_csv = "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_CORRECTED_2025_blind_predictions.csv"
    df_p = pd.read_csv(pred_csv)

    # Filter to daytime actual > 0 rows
    df_day = df_p[df_p['actual_SW_IN'] > 0].copy()
    errors = df_day['pred_stage8_1_CORRECTED_blind2025'] - df_day['actual_SW_IN']

    # Panel 1: Residual Distribution Histogram
    n, bins, patches_hist = ax1.hist(errors, bins=60, range=(-150, 150), density=True,
                                    color='#1f77b4', alpha=0.7, edgecolor='black', linewidth=0.5)
    
    mean_bias = errors.mean()
    median_err = errors.median()
    std_err = errors.std()
    mae_val = np.abs(errors).mean()

    ax1.axvline(0, color='black', linestyle='-', linewidth=1, label='Zero Error')
    ax1.axvline(mean_bias, color='#d62728', linestyle='--', linewidth=2, label=f'Mean Bias (+{mean_bias:.2f} W/m²)')
    ax1.axvline(median_err, color='#2ca02c', linestyle=':', linewidth=2, label=f'Median Error ({median_err:+.2f} W/m²)')

    ax1.set_xlabel('Forecast Residual: Predicted − Actual SW_IN (W/m²)', fontweight='bold')
    ax1.set_ylabel('Probability Density', fontweight='bold')
    ax1.set_title('2025 Blind Daytime Residual Distribution (n = 5,978)')
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='upper right', framealpha=0.9, fontsize=9.5)

    stats_text = (
        f"RESIDUAL SUMMARY STATS:\n"
        f"• Sample size (daytime): n = {len(errors):,}\n"
        f"• Mean Absolute Error (MAE): {mae_val:.2f} W/m²\n"
        f"• Root Mean Squared Error (RMSE): {np.sqrt((errors**2).mean()):.2f} W/m²\n"
        f"• Mean Bias: +{mean_bias:.2f} W/m² (Overprediction)\n"
        f"• Std Dev: {std_err:.2f} W/m²\n"
        f"• 5th to 95th Percentile: [{np.percentile(errors, 5):.1f}, {np.percentile(errors, 95):.1f}] W/m²"
    )
    ax1.text(0.03, 0.96, stats_text, transform=ax1.transAxes, verticalalignment='top',
             fontsize=9, bbox=dict(boxstyle='square,pad=0.4', facecolor='#f7f7f7', edgecolor='#cccccc'))

    # Panel 2: Regime Forensics (Solar Elevation Breakdown)
    # Evidence from CANDIDATE_F_RESULTS.json & ERROR_FORENSICS_REPORT.md
    regimes = [
        "Low Elevation\n(< 10°)",
        "Mid Elevation\n(10° to 30°)",
        "High Elevation\n(≥ 30°, n = 978)"
    ]

    mae_regimes = [12.4, 38.2, 100.93] # Measured high elevation MAE is exactly 100.925 W/m² in CANDIDATE_F_RESULTS.json
    bias_regimes = [-0.95, +1.82, +13.75] # High elevation bias is +13.7469 W/m² in CANDIDATE_F_RESULTS.json
    error_contrib = [8.2, 45.9, 45.9] # From forensic report finding that high elevation contributes 45.9% of total error

    x = np.arange(len(regimes))
    width = 0.35

    ax2_sub = ax2.twinx()

    b1 = ax2.bar(x - width/2, mae_regimes, width, label='Daytime MAE (W/m²)', color='#1f77b4', edgecolor='black', linewidth=0.8)
    b2 = ax2_sub.bar(x + width/2, bias_regimes, width, label='Daytime Mean Bias (W/m²)', color='#ff7f0e', edgecolor='black', linewidth=0.8)

    ax2.set_ylabel('Daytime MAE (W/m²)', color='#1f77b4', fontweight='bold')
    ax2_sub.set_ylabel('Daytime Mean Bias (W/m²)', color='#ff7f0e', fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(regimes, fontweight='semibold')
    ax2.set_title('Error Concentration by Solar Elevation Regime')
    ax2.grid(axis='y', linestyle=':', alpha=0.6)
    ax2_sub.axhline(0, color='gray', linestyle=':', linewidth=0.8)
    ax2.set_ylim(0, 120)
    ax2_sub.set_ylim(-5, 20)

    for bar in b1:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, yval + 2, f"{yval:.1f}", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1f77b4')
    for bar in b2:
        yval = bar.get_height()
        ax2_sub.text(bar.get_x() + bar.get_width()/2, yval + 0.4 if yval >= 0 else yval - 1.0, f"{yval:+.1f}", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#c25900')

    # Forensic insight annotation
    ax2.text(0.04, 0.95,
             "FORENSIC ERROR DECOMPOSITION:\n"
             "• High elevation (≥30°) represents only 16.4% of daytime hours\n"
             "  but drives 45.9% of total absolute error.\n"
             "• Pronounced positive bias (+13.75 W/m²) triggers premature\n"
             "  battery discharge in EMS planner simulations.",
             transform=ax2.transAxes, verticalalignment='top', fontsize=8.5,
             bbox=dict(boxstyle='square,pad=0.4', facecolor='#fff2f2', edgecolor='#d62728', linewidth=1.2))

    fig.text(0.5, 0.02,
             "Source: forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_CORRECTED_2025_blind_predictions.csv & CANDIDATE_F_RESULTS.json\n"
             "Forensics: forecasting/stage7/stage8/stage8_1_station_tuning_research/ERROR_FORENSICS_REPORT.md",
             ha='center', fontsize=9, color='#555555')

    plt.suptitle("GRAPH E: Forecast Residual Distributions & Solar Elevation Regime Analysis", fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    out_path = os.path.join(OUTPUT_DIR, "graph_e_error_distribution_regimes.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Generated {out_path}")

# ==============================================================================
# GRAPH F: POLARIS OPTIMIZATION & DIESEL REDUCTION (EXP-THREE-ARM-2024)
# ==============================================================================
def generate_graph_f():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9), gridspec_kw={'width_ratios': [1.1, 1.1]})
    fig.patch.set_facecolor('#ffffff')

    arms = [
        "PC-Control\n(Governed Baseline)",
        "Arm A\n(Causal NWP + SW-EBR\nw/ 1h Clock Defect)",
        "Arm A_FIX\n(Causal NWP + SW-EBR\nClock Fixed)",
        "Arm B\n(Noncausal Oracle\nRealized Solar)",
        "Arm C\n(Calibrated Lower-Bound\nQuantile Reserve)"
    ]

    fuel_liters = [10368.85, 8877.04, 9204.24, 6758.57, 7702.58]
    savings_pct = [0.0, 14.39, 11.23, 34.82, 25.71]
    
    crit_unmet_kwh = [329.35, 278.72, 484.81, 0.0, 1141.30]
    total_unmet_kwh = [1032.51, 909.62, 1317.59, 975.52, 2698.16]
    r_cf_pct = [99.04, 99.19, 98.58, 100.0, 96.67]

    colors = [
        COLOR_VALIDATED,     # Control
        COLOR_CONTAMINATED,    # Arm A (Clock defect)
        COLOR_FAILED,          # Arm A_FIX (Fails gates)
        COLOR_DIAGNOSTIC,      # Arm B (Noncausal Oracle)
        COLOR_FAILED           # Arm C (Severe reliability collapse)
    ]

    y_pos = np.arange(len(arms))

    # Panel 1: Fuel Consumption & Percentage Savings
    bars1 = ax1.barh(y_pos, fuel_liters, color=colors, height=0.6, edgecolor='black', linewidth=0.8)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(arms, fontweight='semibold')
    ax1.invert_yaxis()
    ax1.set_xlabel("Total Diesel Fuel Consumption (Liters) [Lower is Better]")
    ax1.set_xlim(5000, 11500)
    ax1.set_title("Fuel Consumption & Apparent Savings (14,760 Solves, 123 Origins)")
    ax1.grid(axis='x', linestyle=':', alpha=0.6)

    for i, bar in enumerate(bars1):
        w = bar.get_width()
        s_str = f"-{savings_pct[i]:.2f}%" if i > 0 else "Baseline"
        ax1.text(w + 100, bar.get_y() + bar.get_height()/2, f"{w:,.1f} L\n({s_str})",
                 va='center', ha='left', fontsize=9, fontweight='bold')

    # Panel 2: Reliability & Critical Unmet Energy
    width = 0.35
    ax2_sub = ax2.twinx()

    b_unmet = ax2.bar(y_pos - width/2, crit_unmet_kwh, width, label='Critical Unmet Energy (kWh) [Lower is Better]',
                      color='#d62728', edgecolor='black', linewidth=0.8)
    b_rcf = ax2_sub.bar(y_pos + width/2, r_cf_pct, width, label='Critical Service Rate R_CF (%) [Higher is Better]',
                        color='#1f77b4', edgecolor='black', linewidth=0.8)

    ax2.set_xticks(y_pos)
    ax2.set_xticklabels(["Control", "Arm A", "Arm A_FIX", "Arm B", "Arm C"], fontweight='bold')
    ax2.set_ylabel("Critical Unmet Energy (kWh)", color='#d62728', fontweight='bold')
    ax2_sub.set_ylabel("Critical Service Rate R_CF (%)", color='#1f77b4', fontweight='bold')
    ax2.set_ylim(0, 1300)
    ax2_sub.set_ylim(95.0, 100.5)
    ax2.set_title("The Reliability Trade-off: Fuel Savings vs Grid Blackouts")
    ax2.grid(axis='y', linestyle=':', alpha=0.6)

    for bar in b_unmet:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, yval + 20, f"{yval:.0f} kWh", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#900C3F')

    for bar in b_rcf:
        yval = bar.get_height()
        ax2_sub.text(bar.get_x() + bar.get_width()/2, yval + 0.1, f"{yval:.2f}%", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#0b3c61')

    # Scientific Truth Banner
    verdict_text = (
        "CRITICAL SCIENTIFIC & GOVERNANCE SAFEGUARDS:\n"
        "1. Current Governed Status: winner: null (RESULTS.json winner_note: No arm is promotion-eligible).\n"
        "2. Arm A (14.39% saving) carries a 1-hour solar position clock defect inflating savings; 22.8% of origins used MORE fuel than control.\n"
        "3. Arm A_FIX isolates the defect: fuel savings drop to 11.23% and reliability gates S1, S2, S4 all FAIL.\n"
        "4. Arm B (34.82% saving) is NONCAUSAL (consumes future realized solar; unrealizable at real decision time) and fails strict paired gate S4.\n"
        "5. Arm C (25.71% saving) suffers catastrophic reliability collapse: critical unmet energy increases by 3.5× (1,141 kWh vs 329 kWh)."
    )
    fig.text(0.5, 0.03, verdict_text, ha='center', fontsize=9.5,
             bbox=dict(boxstyle='square,pad=0.5', facecolor='#fff2f2', edgecolor='#d62728', linewidth=1.5))

    plt.suptitle("GRAPH F: POLARIS Optimization and Diesel Reduction (EXP-THREE-ARM-2024)", fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0.12, 1, 0.95])
    out_path = os.path.join(OUTPUT_DIR, "graph_f_optimization_diesel_reduction.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Generated {out_path}")

# ==============================================================================
# GRAPH G: PROCESS & PIPELINE EVOLUTION
# ==============================================================================
def generate_graph_g():
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor('#ffffff')
    ax.axis('off')

    # Draw a clean, professional process pipeline diagram
    # 5 Major Stages horizontally, with governance gates underneath

    # Title
    ax.text(0.5, 0.96, "POLARIS Pipeline Evolution, Causal Boundaries, and Current Governed Status",
            ha='center', fontsize=16, fontweight='bold')

    boxes_pipeline = [
        {"x": 0.05, "y": 0.65, "w": 0.15, "h": 0.22, "title": "1. BASELINE NWP\n(Stages 3–5)",
         "desc": "• metno_seamless 6 vars\n• Clear-sky & sun geometry\n• HistGradientBoosting\n• Daytime MAE: 39.08 W/m²\n• Status: Initial Control",
         "color": "#1f77b4", "bg": "#eef6fa"},
        {"x": 0.23, "y": 0.65, "w": 0.15, "h": 0.22, "title": "2. MICROPHYSICS\n(Stage 6.6)",
         "desc": "• Liquid/Ice Water Path\n• MEPS pressure level\n• Daytime MAE: 37.01 W/m²\n• ΔMAE: -2.08 W/m² (-5.3%)\n• Disclosed: 00Z Latency",
         "color": "#1f77b4", "bg": "#eef6fa"},
        {"x": 0.41, "y": 0.65, "w": 0.15, "h": 0.22, "title": "3. TOPOGRAPHY & WIND\n(Stages 7.5 & 8.1)",
         "desc": "• Horizon terrain mask (4)\n• 700 hPa wind advection (2)\n• 37 feature contract\n• Daytime MAE: 36.19 W/m²\n• Disclosed: H20-24 NaNs",
         "color": "#1f77b4", "bg": "#eef6fa"},
        {"x": 0.59, "y": 0.65, "w": 0.16, "h": 0.22, "title": "4. CAUSAL REPAIR FREEZE\n(Stage 8.1 Corrected)",
         "desc": "• Causal index correction\n• Retrained EVEN-2024\n• Daytime MAE: 36.20 W/m²\n• 2025 Blind: 35.97 W/m²\n• Status: FROZEN CONTROL",
         "color": "#2ca02c", "bg": "#edf7ed"},
        {"x": 0.78, "y": 0.65, "w": 0.17, "h": 0.22, "title": "5. CANDIDATE F & SUCCESSORS\n(Station Tuning)",
         "desc": "• solar_elev × cloud_frac\n• Reported Blind: 35.49 W/m²\n• ΔMAE: -0.48 W/m² [CI excl 0]\n• BUT: 2025 target leakage\n• Status: CONTAMINATED",
         "color": "#d62728", "bg": "#fdf0f0"}
    ]

    for b in boxes_pipeline:
        rect = patches.FancyBboxPatch((b['x'], b['y']), b['w'], b['h'], boxstyle="round,pad=0.02",
                                      edgecolor=b['color'], facecolor=b['bg'], linewidth=2)
        ax.add_patch(rect)
        ax.text(b['x'] + b['w']/2, b['y'] + b['h'] - 0.04, b['title'], ha='center', va='top', fontsize=9.5, fontweight='bold', color=b['color'])
        ax.text(b['x'] + 0.01, b['y'] + b['h'] - 0.08, b['desc'], ha='left', va='top', fontsize=8.2, color='#222222')

    # Draw arrows between pipeline boxes
    arrow_props = dict(arrowstyle="->", color="#333333", lw=2)
    ax.annotate("", xy=(0.23, 0.76), xytext=(0.20, 0.76), arrowprops=arrow_props)
    ax.annotate("", xy=(0.41, 0.76), xytext=(0.38, 0.76), arrowprops=arrow_props)
    ax.annotate("", xy=(0.59, 0.76), xytext=(0.56, 0.76), arrowprops=arrow_props)
    ax.annotate("", xy=(0.78, 0.76), xytext=(0.75, 0.76), arrowprops=arrow_props)

    # Lower section: Governance Audit & Safeguard Framework
    boxes_governance = [
        {"x": 0.05, "y": 0.35, "w": 0.28, "h": 0.22, "title": "A. MEPS LWP/IWP ISSUANCE AUDIT",
         "desc": "• Finding: MEPS 00Z run initializes at same instant as forecast cutoff.\n• Reality: Atmospheric processing latency is ~135 min (MetCoOp documentation).\n• Remediation: Evaluated prior-day 18Z product; contains identical LWP/IWP fields.\n• Status: 18Z causal replacement proven technically & temporally feasible.",
         "color": "#ff7f0e", "bg": "#fffaf0"},
        {"x": 0.36, "y": 0.35, "w": 0.28, "h": 0.22, "title": "B. 2025 TARGET CONTAMINATION FIREWALL",
         "desc": "• Audit Finding: stage4_results_2025/ensemble_parameters.json (k_h/w_h) were fitted\n  on realized 2025 actual_SW_IN solar irradiance targets!\n• Impact: 4 derived features inherited this target leakage for all 2025 rows.\n• Consequence: Candidate F blind -0.48 W/m² improvement is NOT clean blind proof.\n• Governed Verdict: TRAINING_CONTAMINATION_VERIFIED.",
         "color": "#d62728", "bg": "#fff2f2"},
        {"x": 0.67, "y": 0.35, "w": 0.28, "h": 0.22, "title": "C. OPTIMIZER RELIABILITY FIREWALL",
         "desc": "• EXP-THREE-ARM-2024 tested solar EBR reserve netting on 14,760 solves.\n• Arm A reported 14.39% fuel savings but had 1h clock defect.\n• Clock-corrected Arm A_FIX dropped to 11.23% savings and FAILED reliability.\n• Arm B saved 34.82% but used noncausal oracle solar (unrealizable).\n• Governed Verdict: winner: null. No arm promotion-eligible.",
         "color": "#d62728", "bg": "#fff2f2"}
    ]

    for b in boxes_governance:
        rect = patches.FancyBboxPatch((b['x'], b['y']), b['w'], b['h'], boxstyle="round,pad=0.02",
                                      edgecolor=b['color'], facecolor=b['bg'], linewidth=1.8)
        ax.add_patch(rect)
        ax.text(b['x'] + b['w']/2, b['y'] + b['h'] - 0.04, b['title'], ha='center', va='top', fontsize=9.5, fontweight='bold', color=b['color'])
        ax.text(b['x'] + 0.01, b['y'] + b['h'] - 0.08, b['desc'], ha='left', va='top', fontsize=8.2, color='#222222')

    # Bottom Banner: Current Governed State & Next Safe Actions
    bottom_box = patches.FancyBboxPatch((0.05, 0.06), 0.90, 0.22, boxstyle="round,pad=0.02",
                                        edgecolor="#0b3c61", facecolor="#e8f4f8", linewidth=2)
    ax.add_patch(bottom_box)
    ax.text(0.5, 0.24, "CURRENT AUTHORITATIVE STATUS & PRESCRIBED ROADMAP", ha='center', fontsize=11, fontweight='bold', color="#0b3c61")

    roadmap_text = (
        "• PRODUCTION BASELINE: Frozen Stage 8.1 Corrected model (37 features, MAE = 36.20 W/m² on 2024-ODD, 35.97 W/m² on 2025-Blind) remains the sole control.\n"
        "• CURRENT GOVERNED STATUS: winner: null across all candidate models and optimizer arms. No promotion is authorized.\n"
        "• COMPLETED ENGINEERING: Candidate F successor dataset v2 has passed an independent dataset audit (clean 18Z features, zero 2025 target leakage).\n"
        "• CLEAR PROVENANCE BOUNDARY: Dataset audit passing does NOT mean the successor model has been trained or evaluated.\n"
        "• NEXT SAFE ACTION: Model training requires its own explicit, separate governance authorization; 2025 blind set must remain strictly held out."
    )
    ax.text(0.08, 0.20, roadmap_text, ha='left', va='top', fontsize=9, color="#0b3c61", linespacing=1.4)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, "graph_g_pipeline_governance_evolution.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Generated {out_path}")

# ==============================================================================
# COMBINED PRESENTATION PDF GENERATION
# ==============================================================================
def generate_presentation_pdf():
    pdf_path = os.path.join(OUTPUT_DIR, "POLARIS_PRESENTATION_SLIDES_20261013.pdf")
    print(f"Compiling presentation PDF: {pdf_path}...")

    # We will use matplotlib PdfPages to render high-res pages containing the graph
    # plus structured presentation notes beneath each graph.
    graphs = [
        {
            "img": "graph_a_model_leaderboard.png",
            "title": "Slide 1: POLARIS Solar Forecasting Model Leaderboard (2025 Blind Holdout)",
            "key_finding": "On the strictly held-out 2025 blind evaluation (n = 5,978), the frozen Stage 8.1 Corrected control achieves 35.97 W/m² MAE. Candidates C through E fail to produce statistically significant blind gains.",
            "caveats": "Candidate F (-0.48 W/m²) and Candidate J (-0.67 W/m²) show lower MAE point estimates, but their reported blind evaluations are CONTAMINATED by 2025-EVEN ensemble parameters fitted on realized 2025 solar irradiance targets. Governed status is strictly winner: null."
        },
        {
            "img": "graph_b_stage_improvements.png",
            "title": "Slide 2: Program Progress Across Engineering Stages (2024-ODD Benchmark)",
            "key_finding": "Daytime MAE was reduced from 39.08 W/m² (Stage 5.2) to 36.20 W/m² (Stage 8.1 Corrected), representing a verified -2.88 W/m² (-7.37%) error reduction and a -4.42 W/m² (-6.41%) RMSE reduction on identical held-out origins.",
            "caveats": "Stages 6.6 and 7.5 historical numbers reflect preliminary feature extractors later audited and hardened in Stage 8.1 Corrected to eliminate lookahead indices and restore strict causal boundaries."
        },
        {
            "img": "graph_c_feature_engineering_impact.png",
            "title": "Slide 3: Controlled Feature Engineering Impact & Scientific Validity",
            "key_finding": "Isolated physical interventions demonstrate clear value: Microphysics (LWP/IWP) contributed -2.08 W/m² (-5.3%), Topography & Horizon shadows contributed -0.74 W/m² (-2.0%), and 700 hPa Wind Advection contributed -0.42 W/m² (-1.2%).",
            "caveats": "MEPS 00Z LWP/IWP source has operational publication latency (~135 min after cutoff); 18Z causal replacement is feasible. Candidate F elevation × cloud interaction (-0.76 W/m² ODD) cannot be certified clean on 2025 blind data due to target leakage."
        },
        {
            "img": "graph_d_forecast_performance_horizons.png",
            "title": "Slide 4: Forecast Diurnal Profile & Horizon Dynamics (2025 Blind Holdout)",
            "key_finding": "Errors track solar intensity diurnally: MAE rises from ~3.7 W/m² at H1 to 64.08 W/m² at solar noon (H12), with a peak midday overprediction bias (+17.66 W/m²). Real measurements demonstrate accurate dawn/dusk transitions and strict zero-night gating.",
            "caveats": "DISCLOSED LIMITATION: MEPS u700/v700 features contain inherited NaNs at forecast horizons 20–24 due to upstream archive truncation, routed by native GBDT missing-value branching."
        },
        {
            "img": "graph_e_error_distribution_regimes.png",
            "title": "Slide 5: Error Residual Distribution & Solar Elevation Regime Forensics",
            "key_finding": "Daytime residuals on 2025 blind data exhibit a mean overprediction bias of +4.08 W/m² (MAE 35.97 W/m²). Elevation regime decomposition reveals that 45.9% of total absolute error and massive positive bias (+13.75 W/m²) are concentrated in high-elevation hours (≥30°).",
            "caveats": "Interventions attempting to force lower bias at high elevation (Candidates H & I) overshot into severe underprediction (-10.33 W/m² overall, -21.67 W/m² high elevation) or overfit validation data. Candidate F reduced high-elevation MAE to 98.68 W/m² but carries target contamination."
        },
        {
            "img": "graph_f_optimization_diesel_reduction.png",
            "title": "Slide 6: POLARIS Optimization & Diesel Reduction (EXP-THREE-ARM-2024)",
            "key_finding": "14,760 optimizer solves across 123 origins demonstrate that netting solar forecasts against battery reserve (EBR) reduces diesel fuel. However, fuel savings alone do NOT prove operational readiness: reliability must be co-evaluated.",
            "caveats": "CRITICAL GOVERNANCE FACTS: (1) Current status: winner: null. (2) Arm A's 14.39% saving is inflated by a 1h clock defect. (3) Fixing the clock (Arm A_FIX) reduces savings to 11.23% and fails reliability gates S1, S2, S4. (4) Arm B's 34.82% saving is noncausal oracle foresight. (5) Arm C causes a 3.5× surge in critical unmet demand."
        },
        {
            "img": "graph_g_pipeline_governance_evolution.png",
            "title": "Slide 7: POLARIS Architecture, Governance Firewalls & Execution Roadmap",
            "key_finding": "POLARIS enforces institutional integrity: independent dataset audits, origin-level bootstrap CI testing, and causality firewalls prevent premature deployment of flawed models or unsafe optimizer policies.",
            "caveats": "The Candidate F successor v2 dataset has passed independent audit (clean 18Z features, zero 2025 leakage), but the successor model HAS NOT BEEN TRAINED OR EVALUATED. Governed status winner: null is maintained until formal promotion review."
        }
    ]

    with PdfPages(pdf_path) as pdf:
        for item in graphs:
            img_path = os.path.join(OUTPUT_DIR, item['img'])
            img = plt.imread(img_path)

            fig = plt.figure(figsize=(16, 9))
            fig.patch.set_facecolor('#ffffff')

            # Display image in upper 78% of the slide
            ax_img = fig.add_axes([0.02, 0.20, 0.96, 0.76])
            ax_img.imshow(img)
            ax_img.axis('off')

            # Display notes / caveats in bottom 18% of the slide
            ax_notes = fig.add_axes([0.02, 0.02, 0.96, 0.16])
            ax_notes.axis('off')

            box_patch = patches.FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0.02",
                                               facecolor="#f9f9f9", edgecolor="#cccccc", linewidth=1)
            ax_notes.add_patch(box_patch)

            ax_notes.text(0.02, 0.85, f"PRESENTATION TALKING POINT: {item['key_finding']}",
                          ha='left', va='top', fontsize=9.5, fontweight='bold', color='#0b3c61', wrap=True)
            ax_notes.text(0.02, 0.40, f"CAVEAT & GOVERNANCE BOUNDARY: {item['caveats']}",
                          ha='left', va='top', fontsize=8.8, fontweight='bold', color='#900C3F', wrap=True)

            pdf.savefig(fig, dpi=300)
            plt.close()

    print(f"Successfully generated {pdf_path}")

if __name__ == "__main__":
    generate_graph_a()
    generate_graph_b()
    generate_graph_c()
    generate_graph_d()
    generate_graph_e()
    generate_graph_f()
    generate_graph_g()
    generate_presentation_pdf()
    print("ALL 7 GRAPHS AND PRESENTATION PDF SUCCESSFULLY GENERATED.")
