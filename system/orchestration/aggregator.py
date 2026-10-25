import sys, os
from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
import os, json, hashlib
from pathlib import Path
from typing import Dict, Any

class CampaignAggregator:
    @staticmethod
    def aggregate_results(run_dir: Path, expected_cycles: int = 8784) -> Dict[str, Any]:
        cells = ["cell_a2", "cell_b"]
        cell_results = {}
        
        for c in cells:
            rec_file = run_dir / "cells" / c / "trajectory_records.json"
            if not rec_file.exists():
                # Allow fallback checking for legacy cell IDs
                alt_c = "cell_a" if c == "cell_a2" else "cell_2"
                rec_file = run_dir / "cells" / alt_c / "trajectory_records.json"
                if not rec_file.exists():
                    raise FileNotFoundError(f"Missing trajectory records for {c} at {rec_file}")
                
            with open(rec_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            records = data.get("records", [])
            if len(records) != expected_cycles:
                raise ValueError(f"Coverage violation in {c}: expected {expected_cycles} cycles, got {len(records)}")
                
            cell_results[c] = {
                "cell_id": c,
                "total_cycles": len(records),
                "cumulative_fuel_l": data.get("cumulative_fuel_l", 0.0),
                "cumulative_diesel_energy_kwh": data.get("cumulative_diesel_energy_kwh", 0.0),
                "integrity_counters": data.get("integrity_counters", {})
            }

        fuel_a2 = cell_results.get("cell_a2", {}).get("cumulative_fuel_l", 0.0)
        fuel_b = cell_results.get("cell_b", {}).get("cumulative_fuel_l", 0.0)

        diff_l = round(fuel_b - fuel_a2, 4)
        pct_diff = round((diff_l / fuel_a2 * 100.0), 2) if fuel_a2 > 0 else 0.0

        matrix_summary = {
            "primary_2cell_comparison": {
                "cell_a2_reactive_hybrid_baseline_fuel_l": fuel_a2,
                "cell_b_polaris_closed_loop_fuel_l": fuel_b,
                "absolute_diff_l": diff_l,
                "percentage_diff_pct": pct_diff
            },
            "cell_details": cell_results
        }

        # Save output matrix
        out_file = run_dir / "final" / "PAIRED_COMPARISON_MATRIX_RESULTS.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(matrix_summary, f, indent=2)

        return matrix_summary
