#!/usr/bin/env python3
"""
POLARIS — Candidate C.2 (Clear-Sky Ratio) Offline Validation Harness
File: scratch/demo_c2_boundary.py
"""

def _compute_boundary_clearsky_ratio(
    forecast_t23: float, 
    clearsky_t23: float, 
    clearsky_t24: float
) -> float:
    MIN_CLEARSKY_WM2 = 5.0
    
    # Safeguard 1: Nighttime/Sunrise protection
    if clearsky_t23 < MIN_CLEARSKY_WM2:
        fallback_kt = 1.0
        return max(0.0, fallback_kt * clearsky_t24)
        
    # Calculate Clear-Sky Index
    k_t = forecast_t23 / clearsky_t23
    
    # Safeguard 2: Lensing Cap
    k_t = min(k_t, 1.2)
    
    # Apply and Floor
    return max(0.0, k_t * clearsky_t24)

def run_edge_case_tests():
    print("=" * 70)
    print("TESTING C.2 BOUNDARY ESTIMATOR EDGE CASES")
    print("=" * 70)

    # 1. Standard Midday (Partly Cloudy)
    # Step 22 is 80% clear. Step 23 should naturally follow the curve down at 80%.
    res = _compute_boundary_clearsky_ratio(forecast_t23=400.0, clearsky_t23=500.0, clearsky_t24=450.0)
    print(f"[1] Midday (Kt=0.8):      Expected ~360.0 W/m2 | Got: {res:.1f} W/m2")
    assert abs(res - 360.0) < 0.1

    # 2. Sunset Terminator (The Danger Zone)
    # Step 22 has sun. Step 23 is pitch black. Persistence would have failed here.
    res = _compute_boundary_clearsky_ratio(forecast_t23=120.0, clearsky_t23=150.0, clearsky_t24=0.0)
    print(f"[2] Sunset Terminator:    Expected 0.0 W/m2    | Got: {res:.1f} W/m2")
    assert abs(res - 0.0) < 0.1

    # 3. Sunrise Terminator
    # Step 22 is pitch black. Step 23 sun breaches horizon. 
    # Kt is undefined at Step 22, so it must fall back to 1.0 Kt.
    res = _compute_boundary_clearsky_ratio(forecast_t23=0.0, clearsky_t23=0.0, clearsky_t24=60.0)
    print(f"[3] Sunrise Terminator:   Expected 60.0 W/m2   | Got: {res:.1f} W/m2")
    assert abs(res - 60.0) < 0.1

    # 4. Cloud-Edge Lensing (Explosive Scaling Trap)
    # Step 22 sees a massive reflection (Kt = 1.5). Step 23 must cap the Kt at 1.2.
    res = _compute_boundary_clearsky_ratio(forecast_t23=750.0, clearsky_t23=500.0, clearsky_t24=600.0)
    print(f"[4] Cloud-Edge Lensing:   Expected 720.0 W/m2  | Got: {res:.1f} W/m2 (capped at 1.2 * 600)")
    assert abs(res - 720.0) < 0.1
    
    # 5. Perfect Overcast
    # Step 22 is heavily clouded (Kt=0.1). Step 23 should scale down similarly.
    res = _compute_boundary_clearsky_ratio(forecast_t23=50.0, clearsky_t23=500.0, clearsky_t24=600.0)
    print(f"[5] Heavy Overcast:       Expected 60.0 W/m2   | Got: {res:.1f} W/m2")
    assert abs(res - 60.0) < 0.1

    print("\n[SUCCESS] All edge case boundary invariants passed.")
    print("=" * 70)

if __name__ == "__main__":
    run_edge_case_tests()
