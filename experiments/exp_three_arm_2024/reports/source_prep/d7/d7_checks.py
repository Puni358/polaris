"""D7 read-only timestamp verification on 2024 SITES + POLARIS 2024 weather file. No writes to repo."""
import sys, hashlib, numpy as np, pandas as pd
D = sys.argv[1]
LAT, LON = 68.36207412, 18.73875158
def sha(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()

def solar_elev_utc(ts_utc):
    # NOAA solar position (sufficient to ~1 min); ts_utc: DatetimeIndex naive UTC
    jd = ts_utc.to_julian_date().values
    jc = (jd - 2451545.0)/36525.0
    L0 = (280.46646 + jc*(36000.76983 + jc*0.0003032)) % 360
    M = 357.52911 + jc*(35999.05029 - 0.0001537*jc)
    e = 0.016708634 - jc*(0.000042037 + 0.0000001267*jc)
    Mr = np.radians(M)
    C = np.sin(Mr)*(1.914602 - jc*(0.004817+0.000014*jc)) + np.sin(2*Mr)*(0.019993-0.000101*jc) + np.sin(3*Mr)*0.000289
    tl = L0 + C
    om = 125.04 - 1934.136*jc
    lam = tl - 0.00569 - 0.00478*np.sin(np.radians(om))
    eps0 = 23 + (26 + ((21.448 - jc*(46.815 + jc*(0.00059 - jc*0.001813))))/60)/60
    eps = eps0 + 0.00256*np.cos(np.radians(om))
    dec = np.degrees(np.arcsin(np.sin(np.radians(eps))*np.sin(np.radians(lam))))
    y = np.tan(np.radians(eps/2))**2
    L0r = np.radians(L0)
    eot = 4*np.degrees(y*np.sin(2*L0r) - 2*e*np.sin(Mr) + 4*e*y*np.sin(Mr)*np.cos(2*L0r) - 0.5*y*y*np.sin(4*L0r) - 1.25*e*e*np.sin(2*Mr))
    mins = ts_utc.hour.values*60 + ts_utc.minute.values + ts_utc.second.values/60
    tst = (mins + eot + 4*LON) % 1440
    ha = np.where(tst/4 < 0, tst/4 + 180, tst/4 - 180)
    zen = np.degrees(np.arccos(np.sin(np.radians(LAT))*np.sin(np.radians(dec)) + np.cos(np.radians(LAT))*np.cos(np.radians(dec))*np.cos(np.radians(ha))))
    return 90 - zen

raw_p = f"{D}/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv"
lines = open(raw_p, encoding='utf-8-sig').read().splitlines()
hdr = [i for i,l in enumerate(lines) if l.startswith("TIMESTAMP,")][0]
meta = {l.split(":")[0]: l.split(":",1)[1].strip() for l in lines[:10] if ":" in l}
raw = pd.read_csv(raw_p, skiprows=hdr, encoding='utf-8-sig')
raw["TS"] = pd.to_datetime(raw["TIMESTAMP"])
out = {}
out["raw_sha256"] = sha(raw_p); out["raw_TIME_ZONE_header"] = meta.get("TIME ZONE"); out["raw_TIME_RESOLUTION"] = meta.get("TIME RESOLUTION")
out["raw_station"] = meta.get("TITLE"); out["raw_lat_lon"] = (meta.get("LATITUDE"), meta.get("LONGITUDE"))
d = raw["TS"].diff().dropna()
out["raw_rows"] = len(raw); out["raw_first_last"] = (str(raw["TS"].min()), str(raw["TS"].max()))
out["raw_duplicates"] = int(raw["TS"].duplicated().sum())
out["raw_step_counts"] = d.value_counts().head(5).astype(int).to_dict()
exp = pd.date_range(raw["TS"].min(), raw["TS"].max(), freq="10min"); out["raw_missing_stamps"] = int(len(exp.difference(raw["TS"])))
# DST checks: EU DST 2024-03-31 01:00 UTC and 2024-10-27 01:00 UTC; in a fixed UTC+1 file no gap/dup should appear
for day in ("2024-03-31", "2024-10-27"):
    s = raw[(raw["TS"] >= day) & (raw["TS"] < pd.Timestamp(day) + pd.Timedelta(days=1))]
    out[f"dst_{day}_rows"] = len(s); out[f"dst_{day}_dups"] = int(s["TS"].duplicated().sum())
out["raw_SW_IN_nan"] = int(raw.SW_IN.isna().sum())

# Hourly aggregation reproduction (handoff §7): mean of HH:00..HH:50 -> HH:00
hv = pd.read_csv(f"{D}/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv"); hv["TS"] = pd.to_datetime(hv["TIMESTAMP"])
out["hourly_sha256"] = sha(f"{D}/POLARIS_v0_1_SITES_Nuolja_2024_hourly_5var.csv"); out["hourly_rows"] = len(hv)
out["hourly_dups"] = int(hv["TS"].duplicated().sum()); out["hourly_missing"] = int(len(pd.date_range("2024-01-01","2024-12-31 23:00",freq="h").difference(hv["TS"])))
r = raw.set_index("TS")["SW_IN"]
agg_floor = r.groupby(r.index.floor("h")).mean()           # HH:00..HH:50 -> HH:00
agg_ceil = r.groupby(r.index.ceil("h")).mean()             # HH-1:10..HH:00 -> HH:00
m = hv.set_index("TS")["SW_IN"]
out["agg_floor_maxabs"] = float((agg_floor.reindex(m.index) - m).abs().max())
out["agg_ceil_maxabs"] = float((agg_ceil.reindex(m.index) - m).abs().max())

# Weather file linkage
w = pd.read_csv(f"{D}/POLARIS_v0_1_future_weather_forecasts_2024.csv"); w["TS"] = pd.to_datetime(w["timestamp"]); w["FS"] = pd.to_datetime(w["forecast_start"])
out["weather_sha256"] = sha(f"{D}/POLARIS_v0_1_future_weather_forecasts_2024.csv")
j = w.merge(hv[["TS","SW_IN"]], on="TS", how="left")
out["weather_actual_vs_hourly_maxabs"] = float((j.actual_SW_IN - j.SW_IN).abs().max()); out["weather_unmatched"] = int(j.SW_IN.isna().sum())
lead = (w["TS"] - w.FS)/pd.Timedelta(hours=1)
out["weather_lead_hours_set"] = sorted(set(lead.astype(int)))
out["weather_horizon_minus_lead"] = sorted(set((w.horizon_hour - lead).astype(int)))
out["weather_dups_(fs,h)"] = int(w.duplicated(["FS","horizon_hour"]).sum()); out["weather_ts_unique"] = bool(w["TS"].is_unique)
out["weather_years"] = sorted(set(w["TS"].dt.year)) ; out["weather_fs_hours"] = sorted(set(w.FS.dt.hour))
# t0 convention: t0 = fs-1h ; step k realized timestamp = rts[k] = fs+k ; planner targets at step k = t0+k+1 .. t0+k+24 = fs+k .. fs+k+23
out["step_alignment_note"] = "realized step k timestamp == fs+k == first planner target at step k (consistent)"

# Solar geometry test on NON-evaluation months (exclude 2024-04-29..2024-09-02), daytime 10-min data
nm = ~((raw["TS"] >= "2024-04-29") & (raw["TS"] < "2024-09-03"))
x = raw[nm & raw.SW_IN.notna()].copy()
res = {}
for name, off in (("labels_are_UTC", 0), ("labels_are_UTC+1", 1)):
    # 10-min period-ending: centre = label - 5 min ; convert to UTC
    t_utc = pd.DatetimeIndex(x["TS"] - pd.Timedelta(minutes=5) - pd.Timedelta(hours=off))
    el = solar_elev_utc(t_utc)
    x[name] = el
# sunrise-onset test: per day, first stamp with SW_IN >= 10 W/m2 after night; compare with elevation at that stamp
x["date"] = x["TS"].dt.date
on = x[x.SW_IN >= 10].groupby("date").head(1)
for name in ("labels_are_UTC", "labels_are_UTC+1"):
    res[f"{name}_median_elev_at_first_light_deg"] = round(float(np.median(on[name])), 2)
    res[f"{name}_frac_first_light_with_sun_below_-2deg"] = round(float((on[name] < -2).mean()), 3)
# lag scan: correlation of SW_IN with max(0,sin(elev)) assuming UTC labels, over lags
x = x.set_index("TS").sort_index()
best = None
el_utc = pd.Series(np.maximum(0, np.sin(np.radians(solar_elev_utc(pd.DatetimeIndex(x.index - pd.Timedelta(minutes=5)))))), index=x.index)
for lag in range(-120, 121, 10):  # minutes; positive lag = labels later than UTC
    s = pd.Series(np.maximum(0, np.sin(np.radians(solar_elev_utc(pd.DatetimeIndex(x.index - pd.Timedelta(minutes=5) - pd.Timedelta(minutes=lag)))))), index=x.index)
    c = np.corrcoef(x.SW_IN.values, s.values)[0,1]
    if best is None or c > best[1]: best = (lag, c)
    res[f"corr_lag_{lag:+d}min"] = round(float(c), 5)
res["best_lag_min"] = best[0]; res["best_corr"] = round(best[1], 5)
res["first_light_days"] = len(on)
# check the existing decomposition file used UTC+1 localization
dc = pd.read_csv(f"{D}/POLARIS_v0_1_clearsky_decomposition.csv"); dc["TS"] = pd.to_datetime(dc["TIMESTAMP"])
el1 = solar_elev_utc(pd.DatetimeIndex(dc["TS"] - pd.Timedelta(hours=1)))
el0 = solar_elev_utc(pd.DatetimeIndex(dc["TS"]))
res["decomposition_elev_maxabs_vs_UTC+1"] = round(float(np.abs(dc.solar_elevation - el1).max()), 3)
res["decomposition_elev_maxabs_vs_UTC"] = round(float(np.abs(dc.solar_elevation - el0).max()), 3)
out.update(res)
for k, v in out.items(): print(f"{k}: {v}")
