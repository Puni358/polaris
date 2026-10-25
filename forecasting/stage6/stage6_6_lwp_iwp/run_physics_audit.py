import requests
import numpy as np
import pandas as pd
import time
import json
import os

dates = ['2024-01-15', '2024-04-15', '2024-06-15', '2024-07-15', '2024-10-15']
p_levels_hpa = np.array([50, 100, 150, 200, 250, 300, 400, 500, 700, 800, 850, 925, 1000], dtype=float)
p_levels_pa = p_levels_hpa * 100.0
g = 9.80665

y_idx, x_idx = 760, 486

def fetch_var(url, var_name):
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                lines = r.text.split('\n')
                header = f'{var_name}.{var_name}'
                start = False
                vals = []
                for l in lines:
                    if header in l:
                        start = True
                        continue
                    if start:
                        if l.startswith(f'{var_name}.'):
                            break
                        if l.strip() and ',' in l:
                            val_str = l.split(',')[-1].strip()
                            vals.append(float(val_str))
                return np.array(vals)
        except Exception:
            time.sleep(1)
    return None

results = []

for d in dates:
    print(f"Processing date {d}...")
    date_str = d.replace('-', '/')
    tag_str = d.replace('-', '') + 'T00Z'
    
    url_ps = f'https://thredds.met.no/thredds/dodsC/meps25epsarchive/{date_str}/meps_det_sfc_{tag_str}.ncml.ascii?surface_air_pressure[0:1:23][0:1:0][760:1:760][486:1:486]'
    ps_pa = fetch_var(url_ps, 'surface_air_pressure')
    
    url_ql = f'https://thredds.met.no/thredds/dodsC/meps25epsarchive/{date_str}/meps_det_pl_{tag_str}.ncml.ascii?mass_fraction_of_cloud_condensed_water_in_air_pl[0:1:23][0:1:12][760:1:760][486:1:486]'
    ql_raw = fetch_var(url_ql, 'mass_fraction_of_cloud_condensed_water_in_air_pl')
    
    url_qi = f'https://thredds.met.no/thredds/dodsC/meps25epsarchive/{date_str}/meps_det_pl_{tag_str}.ncml.ascii?mass_fraction_of_cloud_ice_in_air_pl[0:1:23][0:1:12][760:1:760][486:1:486]'
    qi_raw = fetch_var(url_qi, 'mass_fraction_of_cloud_ice_in_air_pl')
    
    if ps_pa is not None and len(ps_pa) == 24 and ql_raw is not None and len(ql_raw) == 312 and qi_raw is not None and len(qi_raw) == 312:
        ql_data = ql_raw.reshape((24, 13))
        qi_data = qi_raw.reshape((24, 13))
        
        for h in range(24):
            ps = ps_pa[h]
            ql_profile = ql_data[h]
            qi_profile = qi_data[h]
            
            # 1. Naive LWP/IWP (all 13 pressure levels 50..1000 hPa)
            lwp_naive = 0.0
            iwp_naive = 0.0
            for k in range(12):
                dp = p_levels_pa[k+1] - p_levels_pa[k]
                lwp_naive += 0.5 * (ql_profile[k] + ql_profile[k+1]) * dp / g
                iwp_naive += 0.5 * (qi_profile[k] + qi_profile[k+1]) * dp / g
            lwp_naive_gm2 = lwp_naive * 1000.0
            iwp_naive_gm2 = iwp_naive * 1000.0
            
            # 2. Surface-aware LWP/IWP (truncating at ps)
            lwp_sa = 0.0
            iwp_sa = 0.0
            for k in range(12):
                p_top = p_levels_pa[k]
                p_bot = p_levels_pa[k+1]
                
                if p_bot <= ps:
                    dp = p_bot - p_top
                    lwp_sa += 0.5 * (ql_profile[k] + ql_profile[k+1]) * dp / g
                    iwp_sa += 0.5 * (qi_profile[k] + qi_profile[k+1]) * dp / g
                elif p_top < ps < p_bot:
                    w = (ps - p_top) / (p_bot - p_top)
                    ql_sfc = ql_profile[k] + w * (ql_profile[k+1] - ql_profile[k])
                    qi_sfc = qi_profile[k] + w * (qi_profile[k+1] - qi_profile[k])
                    dp = ps - p_top
                    lwp_sa += 0.5 * (ql_profile[k] + ql_sfc) * dp / g
                    iwp_sa += 0.5 * (qi_profile[k] + qi_sfc) * dp / g
                else:
                    pass
            lwp_sa_gm2 = lwp_sa * 1000.0
            iwp_sa_gm2 = iwp_sa * 1000.0
            
            results.append({
                'date': d,
                'lead_time_h': h,
                'surface_pressure_hpa': round(float(ps / 100.0), 2),
                'lwp_naive_gm2': round(float(lwp_naive_gm2), 4),
                'lwp_sa_gm2': round(float(lwp_sa_gm2), 4),
                'lwp_diff_gm2': round(float(lwp_naive_gm2 - lwp_sa_gm2), 4),
                'iwp_naive_gm2': round(float(iwp_naive_gm2), 4),
                'iwp_sa_gm2': round(float(iwp_sa_gm2), 4),
                'iwp_diff_gm2': round(float(iwp_naive_gm2 - iwp_sa_gm2), 4)
            })
    else:
        print(f"Failed to retrieve data for {d}: ps={ps_pa is not None}, ql={ql_raw is not None}, qi={qi_raw is not None}")

os.makedirs('forecasting/stage6/stage6_6_lwp_iwp', exist_ok=True)
df_res = pd.DataFrame(results)
df_res.to_csv('forecasting/stage6/stage6_6_lwp_iwp/surface_aware_vs_naive_comparison.csv', index=False)

print(f"Total records processed: {len(df_res)}")
if len(df_res) > 0:
    print("\n=== COMPARISON SUMMARY (NAIVE VS SURFACE-AWARE INTEGRATION) ===")
    summary = df_res.groupby('date').agg(
        ps_min_hpa=('surface_pressure_hpa', 'min'),
        ps_mean_hpa=('surface_pressure_hpa', 'mean'),
        ps_max_hpa=('surface_pressure_hpa', 'max'),
        lwp_naive_max=('lwp_naive_gm2', 'max'),
        lwp_sa_max=('lwp_sa_gm2', 'max'),
        lwp_diff_max=('lwp_diff_gm2', 'max'),
        iwp_naive_max=('iwp_naive_gm2', 'max'),
        iwp_sa_max=('iwp_sa_gm2', 'max'),
        iwp_diff_max=('iwp_diff_gm2', 'max')
    )
    print(summary.to_string())

    # Save JSON summary
    audit_json = {
        "surface_pressure_variable": {
            "variable_name": "surface_air_pressure",
            "standard_name": "surface_air_pressure",
            "long_name": "Surface Air Pressure",
            "units": "Pa",
            "dimensions": "(time, height0, y, x)",
            "missing_value": "1.0e30f",
            "nuolja_y_x": [760, 486],
            "nuolja_lat_lon": [68.355701, 18.763666],
            "surface_pressure_range_hpa": [float(df_res['surface_pressure_hpa'].min()), float(df_res['surface_pressure_hpa'].max())],
            "surface_pressure_mean_hpa": float(round(df_res['surface_pressure_hpa'].mean(), 2))
        },
        "vertical_domain": {
            "p_levels_hpa": [50, 100, 150, 200, 250, 300, 400, 500, 700, 800, 850, 925, 1000],
            "subterranean_levels": {
                "1000_hpa": "ALWAYS subterranean at Nuolja (p_sfc <= 952.2 hPa). ql and qi are 0.0 or fill, but naive trapezoid adds 75 hPa layer mass.",
                "925_hpa": "Subterranean when p_sfc < 925 hPa (e.g. low pressure systems). Truncation/interpolation required.",
                "850_hpa": "ALWAYS atmospheric above surface at Nuolja (p_sfc > 850 hPa)."
            }
        },
        "integration_method": {
            "physical_basis": "Hydrostatic balance dm = dp / g",
            "nature": "Discrete numerical trapezoidal approximation (NOT physically exact)",
            "surface_truncation_rule": "Integrate from p_top (50 hPa) down to p_sfc. Linearly interpolate q at p_sfc from nearest levels if p_sfc lies between discrete pressure levels. Zero weight to p > p_sfc."
        },
        "comparison_metrics": {
            "max_lwp_naive_gm2": float(round(df_res['lwp_naive_gm2'].max(), 4)),
            "max_lwp_sa_gm2": float(round(df_res['lwp_sa_gm2'].max(), 4)),
            "max_lwp_diff_gm2": float(round(df_res['lwp_diff_gm2'].max(), 4)),
            "max_iwp_naive_gm2": float(round(df_res['iwp_naive_gm2'].max(), 4)),
            "max_iwp_sa_gm2": float(round(df_res['iwp_sa_gm2'].max(), 4)),
            "max_iwp_diff_gm2": float(round(df_res['iwp_diff_gm2'].max(), 4))
        },
        "recommendation": "CONDITIONAL GO",
        "gating_conditions": [
            "Feature extraction MUST use surface-aware integration (surface_air_pressure from sfc product).",
            "No full extraction until integration pipeline incorporates surface pressure boundary truncation.",
            "Minimal candidate feature set: lwp_latest, iwp_latest, lwp_x_cloud (cloud_water_total dropped due to linear redundancy)."
        ],
        "explicit_confirmations": {
            "even_cv_ran": False,
            "odd_accessed": False,
            "full_extraction_launched": False,
            "stage_5_2_modified": False,
            "models_trained": False
        }
    }

    with open('forecasting/stage6/stage6_6_lwp_iwp/physics_audit_results.json', 'w') as f:
        json.dump(audit_json, f, indent=2)

    print("\nSaved physics_audit_results.json successfully.")
