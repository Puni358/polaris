#!/usr/bin/env python3
"""
Scenario 4 ("Naive ML / No Safety Buffers"): real N6 ML rolling-horizon
forecast (NOT perfect foresight), EBR completely off (ebr_target_wh forced
to 0.0 every step -- no uncertainty buffer, no 15 kWh floor, no deadband),
GAP19 optimizer only.

Option D fallback is intentionally NOT wired in here: doing so honestly
requires the real EMSControlRouter + ECD, which fail closed to
UNKNOWN_INVALID without authorized real-station critical-load evidence
(an EVID-xx record). This project's own code documents that evidence as
"EXTERNAL_EVIDENCE_REQUIRED (EVID-02), unavailable" --
see system/scripts/run_synthetic_critical_load_scenario.py:137. Fabricating
an authorization here to force Option D to fire would misrepresent the
system's actual governance state, so this scenario stays GAP19-only, same
as Scenarios 1-3, for a clean and honest comparison.

Output: scratch/ui_dashboard_scenario4.csv
"""
import sys
sys.path.insert(0, "scratch")
from run_continuous_ui_rhc_scenario2 import run_continuous_rhc

if __name__ == "__main__":
    run_continuous_rhc(
        reserve_deadband_wh=0.0,
        output_csv="scratch/ui_dashboard_scenario4.csv",
        label="Scenario 4: N6 ML, EBR off (naive)",
        ebr_mode="off",
    )
