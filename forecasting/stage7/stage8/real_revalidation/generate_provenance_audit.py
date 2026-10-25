#!/usr/bin/env python3
import json
import shutil
from pathlib import Path

dest_dir = Path('/home/punith-bs/01polaris (Copy)/forecasting/stage7/stage8/real_revalidation')
brain_dir = Path('/home/punith-bs/.gemini/antigravity/brain/11d26e00-a045-428c-bdbb-e7c8fb7429cd')

audit_data = {
    'stage': 'STAGE 8 — ENEV METAR IMPLEMENTATION PROVENANCE & PROTOCOL AUDIT',
    'timestamp': '2026-09-13T19:35:00Z',
    'audit_type': 'PARSER & TIMESTAMP PROTOCOL AUDIT',
    'decision': 'IMPLEMENTATION-QUALIFIED / NOT YET SEALED',
    'timestamp_breakdown': {
        'total_benchmark_origins': 347,
        'exact_2350_utc_origins': 329,
        'exact_2350_utc_pct': 94.81,
        'earlier_report_substituted_origins': 18,
        'earlier_report_substituted_pct': 5.19,
        'earlier_breakdown': {
            '23:20_utc_substituted': 16,
            '22:50_utc_substituted': 2
        },
        'other_timestamp_origins': 0,
        'genuinely_missing_origins': 0
    },
    'parser_fallback_audit': {
        'fallback_range_search_triggered_origins': 18,
        'unparsed_default_branch_executions': 1,
        'silent_clear_conversions_count': 1,
        'silent_clear_details': [
            {
                'forecast_start': '2024-10-22 00:00:00+00:00',
                'report_timestamp': '2024-10-21 23:50:00+00:00',
                'raw_skyc1': '///',
                'raw_skyl1_ft': 3000.0,
                'raw_wxcodes': '-RA',
                'raw_metar': 'ENEV 212350Z AUTO 25017G34KT 220V310 9999 -RA ///030/// 10/08 Q0989 RERA RMK WIND 1400FT 24034G47KT',
                'erroneous_assignment': {'enev_cloud_cover_okta': 0.0, 'enev_cloud_base_m': 5000.0},
                'issue': 'Automated cloud layer code /// with rain -RA and cloud base 3000ft was silently converted into clear sky (0 okta, 5000m base)'
            }
        ]
    },
    'protocol_deviations_summary': [
        'Timestamp substitution: 18 origins (5.19%) used earlier reports (23:20 or 22:50 UTC) instead of strict 23:50 UTC matching or explicit missing handling.',
        'Silent clear fallback: 1 origin (0.29%) with /// sensor cloud code and -RA rain was unparsed and silently assigned 0 oktas / 5000m base.'
    ],
    'pre_registered_candidate_verification': {
        'candidate_features': ['enev_cloud_cover_okta', 'enev_cloud_base_m'],
        'control_features_count': 37,
        'candidate_features_count': 39,
        'feature_names_matched': True
    },
    'odd_firewall_status': {
        'odd_accessed': False,
        'odd_predictions_generated': False,
        'odd_metrics_computed': False,
        'odd_firewall_intact': True
    },
    'historical_even_metrics_preserved': {
        'control_even_mae': 37.620054,
        'candidate_even_mae': 37.687360,
        'delta_even_mae': 0.067307
    },
    'spatial_decoupling_interpretation': 'Plausible hypothesis for performance gap, pending clean resolution of implementation protocol deviations.',
    'minimal_required_corrections': [
        '1. Enforce strict exact 23:50 UTC matching. Flag absent 23:50 UTC reports explicitly as missing rather than substituting 23:20/22:50 reports.',
        '2. Update cloud cover parser to strip whitespace and parse sensor cloud code /// when skyl1 height is present (e.g. ///030 with rain).'
    ]
}

# Save JSON
json_dest = dest_dir / 'STAGE8_ENEV_IMPLEMENTATION_PROVENANCE_AUDIT.json'
json_brain = brain_dir / 'STAGE8_ENEV_IMPLEMENTATION_PROVENANCE_AUDIT.json'

with open(json_dest, 'w', encoding='utf-8') as f:
    json.dump(audit_data, f, indent=2)

shutil.copy2(json_dest, json_brain)

# Generate MD
md_content = """# STAGE 8 — ENEV METAR IMPLEMENTATION PROVENANCE & PROTOCOL AUDIT

**Audit Date:** 2026-09-13  
**Audit Status:** **IMPLEMENTATION-QUALIFIED / NOT YET SEALED**  
**ODD Firewall Status:** **INTACT (0 Reads / 0 Predictions / 0 Metrics)**  

---

## 1. Executive Summary & Audit Decision

A forensic provenance audit of the executed ENEV METAR EVEN experiment parser revealed **two protocol deviations** relative to the pre-registered experiment specification:

1. **Timestamp Substitutions (18 / 347 origins, 5.19%):** The parser used a 2-hour lookback window fallback (`sub.iloc[-1]`), substituting 23:20 UTC (16 origins) or 22:50 UTC (2 origins) reports when the exact 23:50 UTC report was absent in the IEM archive, rather than enforcing exact 23:50 UTC matching.
2. **Silent Clear Fallback (1 / 347 origins, 0.29%):** On `2024-10-22 00:00:00`, the report contained `skyc1 = ///` with rain `-RA` and cloud base `skyl1 = 3000.0` ft. Because `///` was not in the parsed layer list, it fell through to the `else` default branch, silently assigning `0.0` oktas (clear sky) and `5000.0` m base.

### Audit Decision: **`IMPLEMENTATION-QUALIFIED / NOT YET SEALED`**

The historical EVEN experiment result (+0.067 W/m² MAE degradation) is **implementation-qualified**. The rejection cannot be formally sealed until the protocol deviations are rectified.

---

## 2. Origin Timestamp Breakdown (347 Benchmark Origins)

| Category | Count | Percentage | Description / Action |
| :--- | :---: | :---: | :--- |
| **Exact 23:50 UTC Report** | **329** | **94.81%** | Strict causal match (10 min before t0) |
| **Earlier Report (23:20 UTC)** | **16** | **4.61%** | Substituted 23:20 report via parser lookback fallback |
| **Earlier Report (22:50 UTC)** | **2** | **0.58%** | Substituted 22:50 report via parser lookback fallback |
| **Other Timestamp (> 23:50 UTC)** | **0** | **0.00%** | None |
| **Genuinely Missing (No 2h report)** | **0** | **0.00%** | None |

---

## 3. Parser Fallback & Unparsed Branch Audit

### Unparsed Silent Clear Fallback Detail (1 Origin)

* **Forecast Start:** `2024-10-22 00:00:00+00:00`
* **Report Timestamp:** `2024-10-21 23:50:00+00:00`
* **Raw METAR:** `ENEV 212350Z AUTO 25017G34KT 220V310 9999 -RA ///030/// 10/08 Q0989 RERA RMK WIND 1400FT 24034G47KT`
* **Raw Fields:** `skyc1 = ///`, `skyl1 = 3000.0` ft, `wxcodes = -RA`
* **Erroneous Executed Value:** `enev_cloud_cover_okta = 0.0`, `enev_cloud_base_m = 5000.0` m
* **Physical Reality:** Active light rain (`-RA`) with automated cloud sensor code (`///`) and cloud base at 3000 ft (914.4 m). Silently converting this into clear sky (0 oktas, 5000 m) violated the mandate not to invent clear sky.

---

## 4. Pre-Registered Feature Inventory Verification

* **Control Features:** 37 Stage 8.1 champion features
* **Candidate Features:** 39 features (Control + `enev_cloud_cover_okta` + `enev_cloud_base_m`)
* **Feature Names Matched:** `VERIFIED`

---

## 5. Minimal Required Corrections

Before any re-execution, the parser must be updated with the following minimal corrections:
1. **Strict Timestamp Matching:** Strictly require exact 23:50 UTC matching. Flag absent 23:50 UTC origins explicitly as missing rather than silently substituting earlier 23:20/22:50 reports.
2. **Sensor Code & Whitespace Handling:** Strip whitespace from `skyc1` (handling `VV `) and parse `///` sensor cloud layer code when `skyl1` height is present (e.g. `///030` with rain).

---

## 6. Firewall & Governance Status

* [x] **ODD Firewall Intact:** 0 ODD reads, 0 ODD predictions, 0 ODD metrics evaluated.
* [x] **Historical EVEN Metrics Preserved:** Control EVEN MAE: 37.620054 W/m², Candidate EVEN MAE: 37.687360 W/m².
* [x] **No Rerun Triggered Automatically:** Pending minimal correction alignment.
* [x] **Spatial Decoupling:** Stated as a plausible interpretation, not a proven fact.
* [x] **Master Handoff & Route Registry:** Untouched.

---
*Audit completed by POLARIS Provenance Firewall System | 2026-09-13*
"""

md_dest = dest_dir / 'STAGE8_ENEV_IMPLEMENTATION_PROVENANCE_AUDIT.md'
md_brain = brain_dir / 'STAGE8_ENEV_IMPLEMENTATION_PROVENANCE_AUDIT.md'

with open(md_dest, 'w', encoding='utf-8') as f:
    f.write(md_content)

shutil.copy2(md_dest, md_brain)

print('Provenance audit saved to:')
print(' -', json_dest)
print(' -', json_brain)
print(' -', md_dest)
print(' -', md_brain)
