import numpy as np
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

