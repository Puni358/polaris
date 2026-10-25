"""
Arm C calibration for EXP-THREE-ARM-2024 (research only). NOT RUN on real data during preparation.

Implements PROTOCOL.md section 4 ("Arm C details") as far as it is unambiguous, with every ambiguous or
unapproved choice taken from config/EXPERIMENT_CONFIG.json `arm_c_method`. A null or unapproved setting
is never replaced by a default: the pure functions raise, and `main()` refuses through preflight.
The six ambiguities and the recommended resolutions are in reports/CALIBRATION_AMBIGUITIES.md and
reports/DECISION_RESOLUTION_2026-10-11.md.

Procedure (as proposed, D5 PENDING):
  1. Calibration origins: 2024 forecast origins <= 2024-04-29 or >= 2024-09-02. Origins 2024-04-30 and
     2024-09-01 (buffers) and every evaluation origin 2024-05-01..2024-08-31 are rejected. Any non-2024
     row in the input aborts (PermissionError).
  2. Clear-sky GHI and solar elevation per target hour come from the unmodified causal_nwp_physics
     forecaster with the D7a label correction applied (sun evaluated at label - 1 h), i.e. exactly the
     geometry Arm C uses at run time. Daylight = elevation > 0 and clear-sky GHI > 0.
  3. gamma_hat: grid search minimizing daylight MAE of clear_sky * (1 - c)^gamma against actual_SW_IN.
     Selection is on forecast error only, never on diesel.
  4. Residuals r = actual - point (space per `residual_space`) on daylight hours, binned by solar
     elevation x forecast cloud fraction; alpha-quantile per bin (method per `quantile_method`).
  5. Bins with fewer than `min_origin_days_per_bin` distinct origins are handled per
     `insufficient_bin_policy`. Evaluation-window data are never used to fill a bin.

Deterministic: no random numbers; outputs depend only on inputs and configuration.
Does not open, import or derive anything from any 2025 file.
"""
import argparse
import hashlib
import json
import platform
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

_SCRIPTS = Path(__file__).resolve().parent
_REPO = _SCRIPTS.parents[2]
for _p in (str(_REPO), str(_SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from causal_cloud_lookup import assert_no_protected_dates  # noqa: E402

REQUIRED_COLUMNS = ("forecast_start", "horizon_hour", "timestamp", "fc_cloud_cover", "actual_SW_IN")
NUMPY_QUANTILE_METHODS = ("inverted_cdf", "averaged_inverted_cdf", "closest_observation",
                          "interpolated_inverted_cdf", "hazen", "weibull", "linear",
                          "median_unbiased", "normal_unbiased", "lower", "higher", "midpoint", "nearest")
QUANTILE_METHODS = NUMPY_QUANTILE_METHODS + ("split_conformal_lower",)
INSUFFICIENT_POLICIES = ("fail", "merge_lower_elevation", "merge_higher_elevation",
                         "merge_single_neighbour_else_lower")
BOUNDARY_RULES = ("left_closed", "right_closed", "closed_middle")
RESIDUAL_SPACES = ("ghi_w_m2", "pv_w")
TIE_RULES = ("smallest_gamma", "largest_gamma")


class CalibrationError(RuntimeError):
    pass


class InsufficientBinError(CalibrationError):
    pass


# ---------------------------------------------------------------------------- input selection
def _ts(s) -> pd.Timestamp:
    return pd.Timestamp(s)


def calibration_origin_filter(fs: pd.Series, window: Dict[str, Any]) -> pd.Series:
    last_before = _ts(window["last_origin_before_evaluation"])
    first_after = _ts(window["first_origin_after_evaluation"])
    buffers = {_ts(b) for b in window["excluded_buffer_origins"]}
    d = pd.to_datetime(fs)
    keep = (d <= last_before) | (d >= first_after)
    return keep & ~d.isin(list(buffers))


def assert_calibration_isolation(df: pd.DataFrame, evaluation: Dict[str, Any], window: Dict[str, Any]) -> None:
    """Fail closed if any evaluation-window or buffer origin, or any target timestamp inside the
    evaluation window, is present in calibration rows."""
    fs = pd.to_datetime(df["forecast_start"])
    ts = pd.to_datetime(df["timestamp"])
    e0, e1 = _ts(evaluation["first_origin"]), _ts(evaluation["last_origin"])
    eval_end = e1 + pd.Timedelta(hours=23)
    buffers = [_ts(b) for b in window["excluded_buffer_origins"]]
    if ((fs >= e0) & (fs <= e1)).any():
        raise PermissionError("calibration input contains evaluation-window origins")
    if fs.isin(buffers).any():
        raise PermissionError("calibration input contains excluded buffer origins")
    if ((ts >= e0) & (ts <= eval_end)).any():
        raise PermissionError("calibration input contains target hours inside the evaluation window")


def select_calibration_rows(weather_df: pd.DataFrame, evaluation: Dict[str, Any],
                            window: Dict[str, Any]) -> pd.DataFrame:
    missing = [c for c in REQUIRED_COLUMNS if c not in weather_df.columns]
    if missing:
        raise CalibrationError(f"weather input missing columns {missing}")
    assert_no_protected_dates(weather_df)  # PermissionError on any non-2024 row
    sub = weather_df[calibration_origin_filter(weather_df["forecast_start"], window)].copy()
    assert_calibration_isolation(sub, evaluation, window)
    validate_calibration_rows(sub)
    return sub.sort_values(["forecast_start", "horizon_hour"]).reset_index(drop=True)


def read_calibration_input(path, evaluation: Dict[str, Any], window: Dict[str, Any]) -> pd.DataFrame:
    """Two-pass read that never parses an excluded row's values.
    Pass 1 reads only forecast_start and timestamp, aborts on any non-2024 row, and selects the
    calibration-window line numbers. Pass 2 parses the value columns for those lines only, so
    evaluation-window and buffer rows (and their actual_SW_IN) are skipped by the CSV parser."""
    keys = pd.read_csv(path, usecols=["forecast_start", "timestamp"], dtype=str)
    assert_no_protected_dates(keys)  # PermissionError on any non-2024 row, before any value is parsed
    keep = calibration_origin_filter(keys["forecast_start"], window).to_numpy()
    skip = {i + 1 for i in np.flatnonzero(~keep)}  # +1: line 0 is the header
    rows = pd.read_csv(path, usecols=list(REQUIRED_COLUMNS), skiprows=lambda i: i in skip)
    if len(rows) != int(keep.sum()):
        raise CalibrationError("calibration rows changed between the two read passes")
    return select_calibration_rows(rows, evaluation, window)


def validate_calibration_rows(df: pd.DataFrame) -> None:
    if df.empty:
        raise CalibrationError("no calibration rows")
    if (pd.to_datetime(df["forecast_start"]).dt.strftime("%H:%M:%S") != "00:00:00").any():
        raise CalibrationError("calibration origins must start at 00:00 (origin-day = target calendar day)")
    if df.duplicated(["forecast_start", "horizon_hour"]).any():
        raise CalibrationError("duplicate (forecast_start, horizon_hour) rows")
    if pd.to_datetime(df["timestamp"]).duplicated().any():
        raise CalibrationError("duplicate target timestamps across origins")
    sizes = df.groupby("forecast_start").size()
    if (sizes != 24).any():
        raise CalibrationError(f"origins without 24 rows: {list(sizes[sizes != 24].index[:5])}")
    for col in ("fc_cloud_cover", "actual_SW_IN"):
        v = pd.to_numeric(df[col], errors="coerce").to_numpy(dtype=float)
        if not np.all(np.isfinite(v)):
            raise CalibrationError(f"non-finite values in {col}")
    c = df["fc_cloud_cover"].to_numpy(dtype=float)
    if (c < 0).any() or (c > 100).any():
        raise CalibrationError("fc_cloud_cover outside [0, 100]")
    if (df["actual_SW_IN"].to_numpy(dtype=float) < 0).any():
        raise CalibrationError("negative actual_SW_IN")
    lead = (pd.to_datetime(df["timestamp"]) - pd.to_datetime(df["forecast_start"])) / pd.Timedelta(hours=1)
    if not ((df["horizon_hour"].to_numpy() - lead.to_numpy()) == 1).all():
        raise CalibrationError("timestamp != forecast_start + (horizon_hour - 1) h")


# ---------------------------------------------------------------------------- geometry
GeometryFn = Callable[[str], Tuple[List[float], List[float]]]


def corrected_geometry_provider() -> GeometryFn:
    """Returns fn(forecast_start) -> (clear_sky_ghi[24], elevation_deg[24]) for targets fs .. fs+23 h,
    computed by the unmodified forecaster with the D7a label correction (sun at label - 1 h)."""
    from system.forecasting.implementations.causal_nwp_physics import CausalNwpPhysicsForecastEngine
    from system.schemas.station_state import StationState
    from solar_convention import apply_label_correction

    engine = CausalNwpPhysicsForecastEngine()
    wrapper = apply_label_correction(engine)

    def fn(forecast_start: str) -> Tuple[List[float], List[float]]:
        t0 = (pd.Timestamp(forecast_start) - pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        st = StationState(timestamp=t0, battery_soc_pct=50.0, battery_energy_wh=100000.0, diesel_running=False,
                          diesel_hours_running=0.0, last_observed_solar_irradiance=0.0,
                          last_observed_demand=15000.0, last_observed_wind_generation=4500.0)
        b = engine.predict(st, {"fc_cloud_cover": [0.0] * 24})  # cloud 0 -> irradiance = night-zeroed clear sky
        elev = wrapper.get_solarposition(pd.to_datetime(b.timestamps, utc=True))["elevation"].to_numpy()
        return list(b.solar_irradiance.point), [float(e) for e in elev]

    fn.engine = engine  # type: ignore[attr-defined]
    return fn


def attach_geometry(rows: pd.DataFrame, geometry: GeometryFn) -> pd.DataFrame:
    out = rows.copy()
    cs, el = [], []
    for fs, g in out.groupby("forecast_start", sort=True):
        c, e = geometry(fs)
        if len(c) != 24 or len(e) != 24:
            raise CalibrationError(f"geometry for {fs} is not 24 values")
        cs.extend(c)
        el.extend(e)
    out["clear_sky_ghi"] = cs
    out["elevation_deg"] = el
    out["cloud_frac"] = out["fc_cloud_cover"].astype(float) / 100.0
    out["daylight"] = (out["elevation_deg"] > 0.0) & (out["clear_sky_ghi"] > 0.0)
    if not np.all(np.isfinite(out[["clear_sky_ghi", "elevation_deg"]].to_numpy(dtype=float))):
        raise CalibrationError("non-finite geometry")
    return out


# ---------------------------------------------------------------------------- gamma
def point_ghi(clear_sky: np.ndarray, cloud_frac: np.ndarray, gamma: float, daylight: np.ndarray) -> np.ndarray:
    base = np.clip(1.0 - np.asarray(cloud_frac, dtype=float), 0.0, 1.0)
    val = np.asarray(clear_sky, dtype=float) * np.power(base, float(gamma))
    return np.where(np.asarray(daylight, dtype=bool), np.maximum(val, 0.0), 0.0)


def gamma_grid(spec: Dict[str, Any]) -> np.ndarray:
    n = int(round((spec["stop"] - spec["start"]) / spec["step"])) + 1
    return np.round(spec["start"] + spec["step"] * np.arange(n), 10)


def fit_gamma(rows: pd.DataFrame, grid: Sequence[float], tie_rule: Optional[str]) -> Dict[str, Any]:
    d = rows[rows["daylight"]]
    if d.empty:
        raise CalibrationError("no daylight calibration hours")
    cs, cf, act = (d["clear_sky_ghi"].to_numpy(float), d["cloud_frac"].to_numpy(float),
                   d["actual_SW_IN"].to_numpy(float))
    ones = np.ones(len(d), dtype=bool)
    maes = np.array([float(np.mean(np.abs(act - point_ghi(cs, cf, g, ones)))) for g in grid])
    best = float(maes.min())
    ties = [float(g) for g, m in zip(grid, maes) if m == best]
    if len(ties) > 1:
        if tie_rule not in TIE_RULES:
            raise CalibrationError(f"gamma tie between {ties} and no approved tie rule")
        chosen = min(ties) if tie_rule == "smallest_gamma" else max(ties)
    else:
        chosen = ties[0]
    return {"gamma_hat": chosen, "daylight_mae_at_gamma_hat": best, "n_daylight_hours": int(len(d)),
            "mae_by_gamma": {f"{g:.2f}": round(m, 6) for g, m in zip(grid, maes)}}


# ---------------------------------------------------------------------------- bins and quantiles
def dim_rule(rule: Any, dim: str) -> Optional[str]:
    """`bin_boundary_rule` is either one rule for both dimensions or {"elevation": ..., "cloud": ...}."""
    if isinstance(rule, dict):
        return rule.get(dim)
    return rule


def assign_bin(values: np.ndarray, edges: Sequence[float], rule: Optional[str]) -> np.ndarray:
    if rule not in BOUNDARY_RULES:
        raise CalibrationError(f"bin boundary rule unresolved or invalid: {rule!r}")
    e = np.asarray(edges, dtype=float)
    if np.any(np.diff(e) <= 0):
        raise CalibrationError("bin edges must be strictly increasing")
    v = np.asarray(values, dtype=float)
    if rule == "closed_middle":  # three bins only: [e0, e1), [e1, e2], (e2, e3]  (protocol "<0.2, 0.2-0.8, >0.8")
        if len(e) != 4:
            raise CalibrationError("closed_middle needs exactly three bins")
        idx = np.where(v < e[1], 0, np.where(v <= e[2], 1, 2))
        if np.any((v < e[0]) | (v > e[3])):
            raise CalibrationError("value outside the bin edges")
        return idx.astype(int)
    if rule == "left_closed":   # [lo, hi), top edge included in the last bin
        idx = np.searchsorted(e, v, side="right") - 1
        idx = np.where(v == e[-1], len(e) - 2, idx)
    else:                        # (lo, hi], bottom edge included in the first bin
        idx = np.searchsorted(e, v, side="left") - 1
        idx = np.where(v == e[0], 0, idx)
    if np.any((idx < 0) | (idx > len(e) - 2)):
        raise CalibrationError("value outside the bin edges")
    return idx.astype(int)


def alpha_quantile(r: np.ndarray, alpha: float, method: Optional[str]) -> float:
    if method not in QUANTILE_METHODS:
        raise CalibrationError(f"quantile method unresolved or invalid: {method!r}")
    r = np.sort(np.asarray(r, dtype=float))
    if r.size == 0:
        raise InsufficientBinError("empty bin")
    if method == "split_conformal_lower":
        k = int(np.floor(alpha * (r.size + 1)))
        if k < 1:
            raise InsufficientBinError(f"n={r.size} too small for a split-conformal {alpha} lower quantile")
        return float(r[k - 1])
    return float(np.quantile(r, alpha, method=method))


def residuals(d: pd.DataFrame, gamma: float, space: Optional[str], pv_fn: Callable[[float], float]) -> np.ndarray:
    if space not in RESIDUAL_SPACES:
        raise CalibrationError(f"residual space unresolved or invalid: {space!r}")
    pt = point_ghi(d["clear_sky_ghi"].to_numpy(float), d["cloud_frac"].to_numpy(float), gamma,
                   np.ones(len(d), dtype=bool))
    act = d["actual_SW_IN"].to_numpy(float)
    if space == "ghi_w_m2":
        return act - pt
    return np.array([pv_fn(a) for a in act]) - np.array([pv_fn(p) for p in pt])


def residual_space_diagnostic(rows: pd.DataFrame, gamma: float, pv_fn: Callable[[float], float]) -> Dict[str, Any]:
    """A5 evidence, computed at calibration time on calibration daylight rows only and recorded in the artifact:
    the number of hours where GHI-space and PV-space residuals are not proportional (the PV map is non-linear
    there, i.e. clipped). Zero means the A5 choice cannot change any quantile. Decides nothing."""
    d = rows[rows["daylight"]]
    pt = point_ghi(d["clear_sky_ghi"].to_numpy(float), d["cloud_frac"].to_numpy(float), gamma,
                   np.ones(len(d), dtype=bool))
    act = d["actual_SW_IN"].to_numpy(float)
    slope = float(pv_fn(1.0))  # W per W/m2 on the linear part of the map
    r_ghi = act - pt
    r_pv = np.array([pv_fn(a) for a in act]) - np.array([pv_fn(x) for x in pt])
    nonlinear = np.abs(r_pv - slope * r_ghi) > 1e-6 * max(1.0, float(np.max(np.abs(r_pv), initial=0.0)))
    return {"n_daylight_hours": int(len(d)), "n_hours_pv_map_nonlinear": int(nonlinear.sum()),
            "max_point_ghi_w_m2": float(np.max(pt, initial=0.0)), "pv_slope_w_per_w_m2": slope}


def quantile_table(rows: pd.DataFrame, gamma: float, method_cfg: Dict[str, Any],
                   pv_fn: Callable[[float], float]) -> Dict[str, Any]:
    alpha = float(method_cfg["alpha"])
    el_edges, cl_edges = method_cfg["elevation_bin_edges_deg"], method_cfg["cloud_bin_edges_fraction"]
    rule, qmethod = method_cfg["bin_boundary_rule"], method_cfg["quantile_method"]
    min_days, policy = int(method_cfg["min_origin_days_per_bin"]), method_cfg["insufficient_bin_policy"]
    space = method_cfg["residual_space"]

    d = rows[rows["daylight"]].copy()
    d["eb"] = assign_bin(d["elevation_deg"].to_numpy(), el_edges, dim_rule(rule, "elevation"))
    d["cb"] = assign_bin(d["cloud_frac"].to_numpy(), cl_edges, dim_rule(rule, "cloud"))
    d["r"] = residuals(d, gamma, space, pv_fn)
    n_el, n_cl = len(el_edges) - 1, len(cl_edges) - 1

    # group map: (eb, cb) -> pooled group id; starts as identity
    group = {(e, c): (e, c) for e in range(n_el) for c in range(n_cl)}
    merges: List[Dict[str, Any]] = []

    def members(g):
        return [k for k, v in group.items() if v == g]

    def origin_days(g):
        ks = members(g)
        m = np.zeros(len(d), dtype=bool)
        for e, c in ks:
            m |= (d["eb"].to_numpy() == e) & (d["cb"].to_numpy() == c)
        return int(d.loc[m, "forecast_start"].nunique()), m

    changed = True
    while changed:
        changed = False
        for g in sorted(set(group.values())):
            n_days, _ = origin_days(g)
            if n_days >= min_days:
                continue
            if policy not in INSUFFICIENT_POLICIES:
                raise InsufficientBinError(f"bin {g} has {n_days} origin-days < {min_days}; "
                                           f"insufficient_bin_policy unresolved ({policy!r})")
            if policy == "fail":
                raise InsufficientBinError(f"bin {g} has {n_days} origin-days < {min_days} (policy: fail)")
            els = sorted({e for e, _ in members(g)})
            lower, upper = els[0] - 1, els[-1] + 1
            if policy == "merge_lower_elevation":
                target_e = lower
            elif policy == "merge_higher_elevation":
                target_e = upper
            else:  # merge_single_neighbour_else_lower: an edge group has one neighbour; interior -> lower
                target_e = lower if lower >= 0 else upper
            if not (0 <= target_e < n_el):
                raise InsufficientBinError(f"bin {g} has {n_days} origin-days and no neighbour in policy direction")
            target = group[(target_e, g[1])]
            for k in members(g):
                group[k] = target
            merges.append({"from": list(g), "into": list(target), "origin_days_before_merge": n_days})
            changed = True
            break

    table = []
    for g in sorted(set(group.values())):
        n_days, m = origin_days(g)
        r_g = d.loc[m, "r"].to_numpy()
        q = alpha_quantile(r_g, alpha, qmethod)
        for e, c in members(g):
            own = (d["eb"].to_numpy() == e) & (d["cb"].to_numpy() == c)
            r_own = d.loc[own, "r"].to_numpy()
            # In-sample coverage diagnostics (PROTOCOL §4; A3 sparse-bin evidence). Recorded, never used to fit.
            table.append({"elevation_bin": e, "cloud_bin": c, "pooled_group": list(g),
                          "origin_days": n_days, "n_hours": int(m.sum()), "q_alpha": q,
                          "own_origin_days": int(d.loc[own, "forecast_start"].nunique()),
                          "own_n_hours": int(own.sum()),
                          "in_sample_coverage_pooled": float(np.mean(r_g >= q)),
                          "in_sample_coverage_own": float(np.mean(r_own >= q)) if r_own.size else None})
    table.sort(key=lambda t: (t["elevation_bin"], t["cloud_bin"]))
    return {"alpha": alpha, "quantile_method": qmethod, "residual_space": space,
            "elevation_bin_edges_deg": list(el_edges), "cloud_bin_edges_fraction": list(cl_edges),
            "bin_boundary_rule": rule, "min_origin_days_per_bin": min_days,
            "insufficient_bin_policy": policy, "merges": merges, "table": table}


def lower_bound(point: Sequence[float], elevation: Sequence[float], cloud_frac: Sequence[float],
                clear_sky: Sequence[float], qtable: Dict[str, Any]) -> List[float]:
    """s_hat = max(0, min(point, point + q(bin))) per target hour, in the table's residual space
    (the caller passes GHI or PV point values to match qtable['residual_space']). Night -> 0.
    Raises if a needed bin is absent; never fills from elsewhere."""
    if qtable.get("residual_space") not in RESIDUAL_SPACES:
        raise CalibrationError("quantile table has no valid residual space")
    lut = {(t["elevation_bin"], t["cloud_bin"]): t["q_alpha"] for t in qtable["table"]}
    el, cf, pt, cs = (np.asarray(x, dtype=float) for x in (elevation, cloud_frac, point, clear_sky))
    day = (el > 0.0) & (cs > 0.0)
    out = np.zeros(len(pt))
    if day.any():
        eb = assign_bin(el[day], qtable["elevation_bin_edges_deg"], dim_rule(qtable["bin_boundary_rule"], "elevation"))
        cb = assign_bin(cf[day], qtable["cloud_bin_edges_fraction"], dim_rule(qtable["bin_boundary_rule"], "cloud"))
        qs = []
        for e, c in zip(eb, cb):
            if (int(e), int(c)) not in lut:
                raise CalibrationError(f"no calibrated quantile for bin {(int(e), int(c))}")
            qs.append(lut[(int(e), int(c))])
        p = pt[day]
        out[day] = np.maximum(0.0, np.minimum(p, p + np.asarray(qs)))
    return out.tolist()


# ---------------------------------------------------------------------------- artifact
def build_artifact(rows: pd.DataFrame, cfg: Dict[str, Any], source_hashes: Dict[str, str],
                   geometry_note: str, pv_fn: Callable[[float], float]) -> Dict[str, Any]:
    m = cfg["arm_c_method"]
    flat = {k: (v["value"] if isinstance(v, dict) and "value" in v else v)
            for k, v in m.items() if not k.startswith("_")}
    grid_spec = m["gamma_grid"]
    fit = fit_gamma(rows, gamma_grid(grid_spec), flat.get("gamma_tie_rule"))
    qt = quantile_table(rows, fit["gamma_hat"], flat, pv_fn)
    rs_diag = residual_space_diagnostic(rows, fit["gamma_hat"], pv_fn)
    origins = sorted(rows["forecast_start"].unique())
    import pvlib  # recorded version only
    return {
        "experiment_id": cfg["experiment_id"],
        "artifact": "ARM_C_CALIBRATION",
        "created_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "method_config": m,
        "calibration_window": cfg["calibration_window"],
        "evaluation_window_excluded": cfg["evaluation"],
        "n_origins": len(origins), "first_origin": origins[0], "last_origin": origins[-1],
        "origins": origins,
        "geometry": geometry_note,
        "gamma_fit": fit,
        "quantiles": qt,
        "residual_space_diagnostic": rs_diag,
        "source_sha256": source_hashes,
        "software": {"python": platform.python_version(), "numpy": np.__version__,
                     "pandas": pd.__version__, "pvlib": pvlib.__version__},
        "deterministic": True,
    }


def write_artifact_exclusive(artifact: Dict[str, Any], path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(artifact, indent=2, sort_keys=True).encode()
    with open(path, "xb") as f:  # refuses to overwrite an existing artifact
        f.write(data)
    return hashlib.sha256(data).hexdigest()


def load_artifact(path: Path, cfg: Dict[str, Any]) -> Tuple[Dict[str, Any], str]:
    """Loads and validates a calibration artifact for Arm C. Raises on any provenance problem."""
    if not path.is_file():
        raise CalibrationError(f"calibration artifact missing: {path}")
    raw = path.read_bytes()
    art = json.loads(raw)
    if art.get("experiment_id") != cfg["experiment_id"] or art.get("artifact") != "ARM_C_CALIBRATION":
        raise CalibrationError("artifact identity mismatch")
    if art.get("method_config") != cfg["arm_c_method"]:
        raise CalibrationError("artifact was produced with a different arm_c_method configuration")
    if art.get("source_sha256", {}).get(cfg["paths"]["weather"]) != cfg["expected_sha256"]["inputs"][cfg["paths"]["weather"]]:
        raise CalibrationError("artifact source weather hash does not match the expected input hash")
    win, ev = cfg["calibration_window"], cfg["evaluation"]
    fs = pd.Series(art.get("origins", []))
    if fs.empty or not calibration_origin_filter(fs, win).all():
        raise CalibrationError("artifact lists origins outside the approved calibration window")
    d = pd.to_datetime(fs)
    if ((d >= _ts(ev["first_origin"])) & (d <= _ts(ev["last_origin"]))).any():
        raise CalibrationError("artifact used evaluation-window origins")
    g = art.get("gamma_fit", {}).get("gamma_hat")
    spec = cfg["arm_c_method"]["gamma_grid"]
    if not isinstance(g, float) or not (spec["start"] - 1e-9 <= g <= spec["stop"] + 1e-9):
        raise CalibrationError("gamma_hat missing or outside the grid")
    qt = art.get("quantiles", {})
    n_el = len(qt.get("elevation_bin_edges_deg", [])) - 1
    n_cl = len(qt.get("cloud_bin_edges_fraction", [])) - 1
    keys = {(t["elevation_bin"], t["cloud_bin"]) for t in qt.get("table", [])}
    if n_el < 1 or n_cl < 1 or keys != {(e, c) for e in range(n_el) for c in range(n_cl)}:
        raise CalibrationError("quantile table incomplete")
    if not all(np.isfinite(t["q_alpha"]) for t in qt["table"]):
        raise CalibrationError("non-finite quantile in table")
    return art, hashlib.sha256(raw).hexdigest()


# ---------------------------------------------------------------------------- CLI
def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Arm C calibration (requires a signed calibration authorization).")
    ap.add_argument("--repo", required=True, help="repository root")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    import preflight as pf
    cfg = pf.load_config(repo)
    rep = pf.PreflightReport("calibration")
    rep.extend("decisions", pf.check_decisions(cfg, pf.CALIBRATION_DECISIONS))
    rep.extend("arm_c_method", pf.check_arm_c_method(cfg))
    rep.extend("hashes", pf.check_hashes(repo, cfg))
    rep.extend("package_manifest", pf.check_package_manifest(repo))
    rep.extend("preregistration", pf.check_preregistration_frozen(repo))
    rep.extend("authorization", pf.check_authorization(repo, cfg, "calibration"))
    out = repo / cfg["paths"]["calibration_artifact"]
    if out.exists():
        rep.failures.append("[output] calibration artifact already exists; refusing to overwrite")
    if not rep.ok:
        print("CALIBRATION REFUSED (preflight failed):", file=sys.stderr)
        for f in rep.failures:
            print("  " + f, file=sys.stderr)
        return 2
    weather_rel = cfg["paths"]["weather"]
    rows = read_calibration_input(repo / weather_rel, cfg["evaluation"], cfg["calibration_window"])
    geom = corrected_geometry_provider()
    rows = attach_geometry(rows, geom)
    art = build_artifact(rows, cfg, {weather_rel: pf.sha256_file(repo / weather_rel)},
                         "causal_nwp_physics (unmodified) + solar_convention.LabelCorrectedLocation",
                         geom.engine._ghi_to_solar_power_w)
    digest = write_artifact_exclusive(art, out)
    print(f"calibration artifact written: {out} sha256={digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
