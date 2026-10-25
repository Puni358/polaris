"""Extra read-only geometry test: last-light elevation and first/last-light midpoint vs solar noon. Non-eval months only."""
import sys, numpy as np, pandas as pd
sys.path.insert(0, sys.argv[2])
D = sys.argv[1]
from d7_geom import solar_elev_utc, LON
p = f"{D}/SITES_MET_ANS_NMS_20240101-20241231_L2_SH.csv"
lines = open(p, encoding='utf-8-sig').read().splitlines()
hdr = [i for i,l in enumerate(lines) if l.startswith("TIMESTAMP,")][0]
raw = pd.read_csv(p, skiprows=hdr, encoding='utf-8-sig'); raw["TS"] = pd.to_datetime(raw.TIMESTAMP)
x = raw[~((raw.TS >= "2024-04-29") & (raw.TS < "2024-09-03"))].copy()
x["date"] = x.TS.dt.date
lit = x[x.SW_IN >= 10]
g = lit.groupby("date").TS
fl, ll = g.min(), g.max()
for name, off in (("UTC", 0), ("UTC+1", 1)):
    e_l = solar_elev_utc(pd.DatetimeIndex(ll - pd.Timedelta(minutes=5) - pd.Timedelta(hours=off)))
    print(f"labels_{name}_median_elev_at_last_light_deg: {np.median(e_l):.2f}")
mid = fl + (ll - fl)/2
midh = mid.dt.hour + mid.dt.minute/60
# solar noon in UTC hours ~ 12 - LON/15 - EoT/60 ; compute numerically per day via elevation max
noon = []
for d in mid.index:
    t = pd.date_range(pd.Timestamp(d), periods=1440, freq="min")
    noon.append(t[np.argmax(solar_elev_utc(t))].hour + t[np.argmax(solar_elev_utc(t))].minute/60)
noon = np.array(noon)
print(f"days: {len(mid)}")
print(f"median_label_midpoint_h: {np.median(midh - 5/60):.2f}")
print(f"median_solar_noon_UTC_h: {np.median(noon):.2f} ; as UTC+1 label: {np.median(noon)+1:.2f}")
