import os
import pandas as pd
import numpy as np
import pvlib

# ============================================================
# POLARIS — Clear-Sky GHI & Clear-Sky Index (kt) Calculation
#
# Station: SITES Nuolja Middle Station
# Latitude:  68.362074° N (LOCKED)
# Longitude: 18.738752° E (LOCKED)
# Elevation: Unconfirmed / Default (0 m)
# Timezone:  UTC+1 (CET) (LOCKED)
# ============================================================

LATITUDE = 68.362074
LONGITUDE = 18.738752
TIMEZONE = "Etc/GMT-1"  # CET (UTC+1 fixed offset)

DATA_FILE = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv"
OUTPUT_FILE = "/home/punith-bs/01polaris (Copy)/data/POLARIS_v0_1_clearsky_decomposition.csv"

def main():
    print("=" * 70)
    print("POLARIS — Clear-Sky Envelope & kt Computation")
    print("=" * 70)

    # 1. Load data
    print(f"\nLoading hourly SITES data from: {DATA_FILE}")
    df = pd.read_csv(DATA_FILE)
    df["TIMESTAMP"] = pd.to_datetime(df["TIMESTAMP"])

    print(f"Total rows loaded: {len(df)}")
    assert len(df) == 8784, f"Expected 8784 rows, got {len(df)}"

    # 2. Set up pvlib Location
    location = pvlib.location.Location(
        latitude=LATITUDE,
        longitude=LONGITUDE,
        tz=TIMEZONE,
        name="SITES Nuolja Middle Station"
    )

    # 3. Localize timestamps to CET (+01:00)
    times_localized = pd.DatetimeIndex(df["TIMESTAMP"]).tz_localize(TIMEZONE)

    # 4. Calculate solar position
    print("Computing solar position (elevation, zenith, azimuth)...")
    solpos = location.get_solarposition(times_localized)

    # Extract key variables
    solar_elevation = solpos["elevation"].values
    solar_zenith = solpos["zenith"].values

    # 5. Calculate clear-sky GHI using Ineichen model
    print("Computing clear-sky GHI (Ineichen-Perez model)...")
    clearsky = location.get_clearsky(times_localized, model="ineichen")
    clearsky_ghi = clearsky["ghi"].values

    # 6. Calculate clear-sky index kt = SW_IN / clearsky_ghi
    actual_sw_in = df["SW_IN"].values

    # Rules for kt calculation:
    # Night: solar_elevation <= 0 or clearsky_ghi < 1.0 W/m² -> kt = 0.0
    # Daytime: kt = actual_sw_in / clearsky_ghi, capped at 1.5 to prevent extreme artifacts
    kt = np.zeros_like(actual_sw_in)

    daytime_mask = (solar_elevation > 0) & (clearsky_ghi >= 1.0)
    kt[daytime_mask] = actual_sw_in[daytime_mask] / clearsky_ghi[daytime_mask]
    kt[daytime_mask] = np.clip(kt[daytime_mask], 0.0, 1.5)

    # 7. Assemble output dataframe
    output_df = pd.DataFrame({
        "TIMESTAMP": df["TIMESTAMP"].dt.strftime("%Y-%m-%d %H:%M:%S"),
        "actual_SW_IN": actual_sw_in,
        "clearsky_ghi": clearsky_ghi,
        "solar_elevation": solar_elevation,
        "solar_zenith": solar_zenith,
        "kt": kt
    })

    # 8. Data checks & summary
    print("\n" + "=" * 50)
    print("SUMMARY STATISTICS")
    print("=" * 50)
    print(f"Total hours:            {len(output_df)}")
    print(f"Daytime hours (el > 0):  {np.sum(solar_elevation > 0)}")
    print(f"Nighttime hours:        {np.sum(solar_elevation <= 0)}")
    print(f"Max actual SW_IN:       {actual_sw_in.max():.2f} W/m²")
    print(f"Max clearsky GHI:       {clearsky_ghi.max():.2f} W/m²")
    
    day_kt = kt[daytime_mask]
    print(f"Daytime kt mean:        {day_kt.mean():.4f}")
    print(f"Daytime kt median:      {np.median(day_kt):.4f}")
    print(f"Daytime kt min:         {day_kt.min():.4f}")
    print(f"Daytime kt max:         {day_kt.max():.4f}")

    # Check how often actual SW_IN <= clearsky_ghi during daytime
    normal_envelope = np.sum((actual_sw_in <= clearsky_ghi) & daytime_mask)
    total_daytime = np.sum(daytime_mask)
    pct_within = (normal_envelope / total_daytime) * 100 if total_daytime > 0 else 0
    print(f"Daytime hours within clear-sky envelope: {normal_envelope}/{total_daytime} ({pct_within:.1f}%)")

    # 9. Save file
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    output_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved clear-sky decomposition to: {OUTPUT_FILE}")
    print("Done!")

if __name__ == "__main__":
    main()
