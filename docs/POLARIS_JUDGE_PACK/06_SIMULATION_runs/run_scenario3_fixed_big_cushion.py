#!/usr/bin/env python3
"""
Scenario 3 ("Fully Paranoid", clean recompute): EBR reserve policy ON, NO
deadband -- same base physics as the Scenario 2 script (which this file
imports), varying only reserve_deadband_wh. This supersedes the earlier
54,254 L number, which had 5 extra realism features (cold-derate, snow,
inverter clip, throttle, ramp) baked in and is therefore not comparable
to a clean Scenario 2 run.

Output: scratch/ui_dashboard_scenario3.csv
"""
import sys
sys.path.insert(0, "scratch")
from run_continuous_ui_rhc_scenario2 import run_continuous_rhc

if __name__ == "__main__":
    run_continuous_rhc(reserve_deadband_wh=0.0, output_csv="scratch/ui_dashboard_scenario3.csv", label="Scenario 3: EBR, no deadband (naive)")
