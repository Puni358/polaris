"""
EXP-THREE-ARM-2024 runner (research only). NOT RUN on evaluation data during preparation.

Modes (exactly one):
  --audit-budget  derive the expected optimizer-call count from the orchestration constants; no solver,
                  no forecaster, no optimizer is constructed.
  --preflight     run every fail-closed check and report; never executes anything.
  --execute       run the experiment ONLY if every preflight check passes. There is no override flag.

Arms (ARM_CONFIGS):
  PC-Control  governed EBR, causal-NWP forecaster with its legacy (1 h) solar-position behaviour.
  A           PC-SW, legacy forecaster. LEGACY_REPRODUCTION — KNOWN TIMESTAMP DEFECT.
  A_FIX       A with pvlib evaluated at label - 1 h (solar_convention.LabelCorrectedLocation). Nothing
              else differs: same cloud lookup, wind/demand forecasts, reserve inputs, optimizer, executor.
  B           PC-SW with realized SITES SW_IN as the solar forecast. NONCAUSAL, never eligible.
  C           PC-SW with the calibrated gamma_hat point forecast (corrected geometry) to the planner and the
              calibrated alpha lower bound to the EBR reserve; needs a validated calibration artifact.
Rule D is OFF in every arm (no Rule D code path exists in this runner).

Re-implements the per-origin loop of the Planner-CF campaign runner in
experiments/stage4_planner_cf_consistency_2025/ (its lines 101-178). That module is never imported,
because it loads the 2025 decomposition file; its file name is deliberately not written here so the
static guards can ban it outright. Changes from it, all deliberate:
  - cloud trajectory from causal_cloud_lookup.OriginCloudPackage (L1 fix) instead of the whole-file lookup;
  - reserve elevation from SolarElevationProvider(None) (pvlib, Etc/GMT-1), never a 2025 file;
  - per-arm forecaster as above; every optimize() call goes through a hard solve budget.
Frozen modules are imported by file path, never by adding 2025 folders to sys.path.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

_SCRIPTS = Path(__file__).resolve().parent
_PKG = _SCRIPTS.parent
_REPO = _PKG.parents[1]
for _p in (str(_REPO), str(_SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import preflight as pf  # noqa: E402
from causal_cloud_lookup import OriginCloudPackage, assert_no_protected_dates  # noqa: E402

STEPS_PER_ORIGIN = 24            # one optimize() call per step; no other optimize() call exists
OPTIMIZE_CALLS_PER_STEP = 1
HIGHS_RUNS_PER_OPTIMIZE = 1      # research_numerical_extractor_planner_cf_v1.py:344-367 (one h.run())
LEXICOGRAPHIC_LEVELS = 5         # J1 > J_NC > J2 > J3 > J4 inside that single run (:85)
CRITICAL_CEILING_W = 11600.0
TERMINAL_TARGET_WH = 100000.0

LABEL_CONTROL = "BASELINE — LEGACY GEOMETRY (DOCUMENTED 1 H SOLAR-POSITION ERROR)"
LABEL_A = "LEGACY_REPRODUCTION — KNOWN TIMESTAMP DEFECT"
LABEL_A_FIX = "DIAGNOSTIC — NOT PROMOTION-ELIGIBLE"
LABEL_B = "NONCAUSAL — DIAGNOSTIC — NOT DEPLOYABLE"
# C's label follows PROTOCOL_ADDENDUM_D7a_AMENDMENT_1.md (D10a, M9): PROTOCOL §7 classes C as a research-only
# candidate. Earlier label (D7a §1 as copied): "DIAGNOSTIC — NOT PROMOTION-ELIGIBLE (...)".
LABEL_C = "RESEARCH-ONLY CANDIDATE — NOT PROMOTION-ELIGIBLE (CALIBRATED POINT + LOWER-BOUND RESERVE)"

_COMMON = {"ebr": "variant_sw", "rule_d": False, "promotion_eligible": False}
ARM_CONFIGS: Dict[str, Dict[str, Any]] = {
    "PC-Control": {"solar_label_correction": False, "solar_forecast": "causal_nwp_gamma1", "ebr": "governed",
                   "ebr_solar": None, "rule_d": False, "causal": True, "promotion_eligible": False,
                   "result_label": LABEL_CONTROL},
    "A": {**_COMMON, "solar_label_correction": False, "solar_forecast": "causal_nwp_gamma1",
          "ebr_solar": "forecast_point", "causal": True, "result_label": LABEL_A},
    "A_FIX": {**_COMMON, "solar_label_correction": True, "solar_forecast": "causal_nwp_gamma1",
              "ebr_solar": "forecast_point", "causal": True, "result_label": LABEL_A_FIX},
    "B": {**_COMMON, "solar_label_correction": False, "solar_forecast": "realized_sw_in",
          "ebr_solar": "forecast_point", "causal": False, "result_label": LABEL_B},
    "C": {**_COMMON, "solar_label_correction": True, "solar_forecast": "calibrated_gamma_hat_point",
          "ebr_solar": "calibrated_lower_bound", "causal": True, "result_label": LABEL_C},
}
ARMS = tuple(ARM_CONFIGS)


class BudgetExceeded(RuntimeError):
    pass


class ArmInvalid(RuntimeError):
    pass


# ---------------------------------------------------------------------------- budget
def budget_audit(n_origins: int, cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    per_arm = n_origins * STEPS_PER_ORIGIN * OPTIMIZE_CALLS_PER_STEP
    total = per_arm * len(ARMS)
    rep = {
        "arms": list(ARMS), "n_arms": len(ARMS), "origins": n_origins, "steps_per_origin": STEPS_PER_ORIGIN,
        "optimize_calls_per_step": OPTIMIZE_CALLS_PER_STEP,
        "optimize_calls_per_arm": per_arm, "optimize_calls_total": total,
        "highs_run_calls_total": total * HIGHS_RUNS_PER_OPTIMIZE,
        "max_internal_lexicographic_subsolves_total": total * HIGHS_RUNS_PER_OPTIMIZE * LEXICOGRAPHIC_LEVELS,
        "repeat_check_calls": 0, "retry_calls": 0, "calibration_solver_calls": 0,
        "rule_d_subarm_calls": 0, "test_solver_calls": 0,
    }
    if cfg is not None:
        b = cfg["budget"]
        rep["configured_per_arm_ceiling"] = b["per_arm_ceiling"]
        rep["configured_total_ceiling"] = b["total_ceiling"]
        rep["reconciles"] = bool(b["per_arm_ceiling"] == per_arm and b["total_ceiling"] == total)
    return rep


class SolveBudget:
    def __init__(self, per_arm: int, total: int):
        self.per_arm, self.total = int(per_arm), int(total)
        self.counts: Dict[str, int] = {}
        self.used = 0

    def charge(self, arm: str) -> None:
        n = self.counts.get(arm, 0)
        if n + 1 > self.per_arm or self.used + 1 > self.total:
            raise BudgetExceeded(f"solve budget exhausted (arm {arm}: {n}/{self.per_arm}, total {self.used}/{self.total})")
        self.counts[arm] = n + 1
        self.used += 1


class BudgetedOptimizer:
    """Every optimize() is charged to the budget BEFORE the inner optimizer runs."""

    def __init__(self, inner: Any, budget: SolveBudget, arm: str):
        self._inner, self._budget, self._arm = inner, budget, arm

    def optimize(self, bundle, state, cfg):
        self._budget.charge(self._arm)
        return self._inner.optimize(bundle, state, cfg)

    def __getattr__(self, name):
        return getattr(self._inner, name)


# ---------------------------------------------------------------------------- frozen modules
def _load(name: str, rel: str):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, _REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_frozen() -> SimpleNamespace:
    """Imports the frozen research modules (adapter, Planner-CF v1, statistics, telemetry) by path."""
    return SimpleNamespace(
        s4a=_load("stage4_low_sun_adapter", "experiments/stage4_sw_low_sun_2025_holdout/stage4_low_sun_adapter.py"),
        stat=_load("planner_cf_statistics", "experiments/stage4_planner_cf_consistency_2025/planner_cf_statistics.py"),
        tel=_load("planned_execution_telemetry", "experiments/stage4_planner_cf_consistency_2025/planned_execution_telemetry.py"),
    )


def load_planner_class():
    return _load("research_numerical_extractor_planner_cf_v1",
                 "experiments/stage4_planner_cf_consistency_2025/research_numerical_extractor_planner_cf_v1.py").PlannerCFV1Optimizer


# ---------------------------------------------------------------------------- configs / state
def load_canonical_configs(repo: Path) -> Dict[str, Any]:
    """Same content as experiments/run_diesel_reduction_campaign.py:71-83 (hash-pinned), with absolute
    paths. That module is not imported: importing it creates a directory (its line 34)."""
    import yaml
    c = {}
    for k, f in (("battery", "battery.yaml"), ("diesel", "diesel.yaml"), ("solar_pv", "solar_pv.yaml"), ("loads", "loads.yaml")):
        with open(repo / "system" / "config" / f) as fh:
            c[k] = yaml.safe_load(fh)
    c["critical_demand_baseline_w"] = 11600.0
    c["terminal_target_wh"] = 100000.0
    return c


def make_initial_state(origin_ts: str):
    """Same values as experiments/run_diesel_reduction_campaign.py:86-97."""
    from system.schemas.station_state import StationState
    return StationState(timestamp=origin_ts, battery_soc_pct=50.0, battery_energy_wh=100000.0,
                        diesel_running=False, diesel_hours_running=0.0, last_observed_solar_irradiance=0.0,
                        last_observed_demand=15000.0, last_observed_wind_generation=4500.0,
                        diesel_fuel_remaining_liters=100.0, operating_mode="NORMAL")


# ---------------------------------------------------------------------------- data
def evaluation_origins(weather_df: pd.DataFrame, cfg: Dict[str, Any]) -> List[str]:
    ev = cfg["evaluation"]
    assert_no_protected_dates(weather_df)
    fs = weather_df["forecast_start"]
    starts = sorted(fs[(fs >= ev["first_origin"]) & (fs <= ev["last_origin"])].unique())
    if len(starts) != ev["expected_origins"]:
        raise RuntimeError(f"expected {ev['expected_origins']} evaluation origins, found {len(starts)}")
    days = pd.to_datetime(pd.Series(starts))
    if (days.dt.hour != 0).any() or (days.diff().dropna() != pd.Timedelta(days=1)).any():
        raise RuntimeError("evaluation origins are not consecutive days at 00:00")
    return list(starts)


def realized_inputs_for(weather_df: pd.DataFrame, forecast_start: str):
    """Same as the Planner-CF campaign runner, lines 191-200 (realized solar from the weather file's actual_SW_IN,
    synthetic wind and demand for h = 1..24)."""
    sub = weather_df[weather_df["forecast_start"] == forecast_start].sort_values("horizon_hour")
    if len(sub) != 24:
        raise RuntimeError(f"origin {forecast_start} has {len(sub)} rows, expected 24")
    rs = sub["actual_SW_IN"].astype(float).tolist()
    rts = [ts.replace(" ", "T") + "Z" for ts in sub["timestamp"].tolist()]
    rw = [max(0.0, round(4500.0 + 5000.0 * math.sin(h * math.pi / 6.0), 2)) for h in range(1, 25)]
    rd = [max(10000.0, round(15000.0 + 3000.0 * math.cos(h * math.pi / 12.0), 2)) for h in range(1, 25)]
    return rs, rw, rd, rts


def _parse_iso(ts: str) -> pd.Timestamp:
    t = pd.Timestamp(ts.replace("Z", "+00:00") if ts.endswith("Z") else ts)
    return t.tz_localize("UTC") if t.tzinfo is None else t


# ---------------------------------------------------------------------------- forecasters
class ArmForecaster:
    """Returns (bundle_for_planner, solar_w_for_ebr, info) for one decision. Wind, demand and timestamps
    always come from the unmodified causal_nwp_physics engine (LocalBaselineForecastEngine channels)."""

    def __init__(self, arm: str, sites_hourly: Optional[Dict[pd.Timestamp, float]] = None,
                 calibration: Optional[Dict[str, Any]] = None):
        from system.forecasting.implementations.causal_nwp_physics import CausalNwpPhysicsForecastEngine
        self.arm, self.spec = arm, ARM_CONFIGS[arm]
        self.engine = CausalNwpPhysicsForecastEngine()
        self.wrapper = None
        if self.spec["solar_label_correction"]:
            from solar_convention import apply_label_correction
            self.wrapper = apply_label_correction(self.engine)
        if self.spec["solar_forecast"] == "realized_sw_in":
            if not sites_hourly:
                raise ArmInvalid("arm B needs the SITES hourly lookup")
            self.sites = sites_hourly
        if self.spec["solar_forecast"] == "calibrated_gamma_hat_point":
            if calibration is None:
                raise ArmInvalid("arm C needs a validated calibration artifact")
            self.gamma = float(calibration["gamma_fit"]["gamma_hat"])
            self.qtable = calibration["quantiles"]

    def _rebuild(self, base, irr: List[float], gen: List[float], meta: Dict[str, Any]):
        from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
        return ForecastBundle(schema_version="1.0.0", origin_timestamp=base.origin_timestamp, horizon_hours=24,
                              timestamps=list(base.timestamps),
                              solar_irradiance=TimeseriesForecast(irr, irr, irr, "W/m^2"),
                              solar_generation=TimeseriesForecast(gen, gen, gen, "W"),
                              wind_generation=base.wind_generation, demand=base.demand,
                              metadata={**dict(base.metadata), **meta})

    def predict(self, state, cloud: List[float]):
        base = self.engine.predict(state, {"fc_cloud_cover": list(cloud)})
        kind = self.spec["solar_forecast"]
        if kind == "causal_nwp_gamma1":
            return base, list(base.solar_generation.point), {}
        if kind == "realized_sw_in":
            labels = [pd.Timestamp(t.replace("Z", "")) for t in base.timestamps]
            try:
                irr = [float(self.sites[t]) for t in labels]
            except KeyError as e:
                raise ArmInvalid(f"arm B: realized SW_IN missing for {e}")
            gen = [self.engine._ghi_to_solar_power_w(x) for x in irr]
            b = self._rebuild(base, irr, gen, {"status": "NONCAUSAL_PERFECT_FORESIGHT_DIAGNOSTIC_ONLY", "arm": "B"})
            return b, gen, {}
        if kind == "calibrated_gamma_hat_point":
            import calibrate_arm_c as cal
            clear = self.engine.predict(state, {"fc_cloud_cover": [0.0] * 24})
            cs = np.asarray(clear.solar_irradiance.point, dtype=float)
            elev = self.wrapper.get_solarposition(pd.to_datetime(base.timestamps, utc=True))["elevation"].to_numpy()
            cf = np.asarray(cloud, dtype=float) / 100.0
            day = (elev > 0.0) & (cs > 0.0)
            pt_ghi = cal.point_ghi(cs, cf, self.gamma, day)
            pt_pv = [self.engine._ghi_to_solar_power_w(x) for x in pt_ghi]
            ghi_space = self.qtable["residual_space"] == "ghi_w_m2"
            if ghi_space:
                lb = cal.lower_bound(pt_ghi, elev, cf, cs, self.qtable)
                lb_pv = [self.engine._ghi_to_solar_power_w(x) for x in lb]
            else:
                lb = lb_pv = cal.lower_bound(pt_pv, elev, cf, cs, self.qtable)
            b = self._rebuild(base, [float(x) for x in pt_ghi], pt_pv, {"arm": "C", "gamma_hat": self.gamma})
            # Coverage record for horizon index 0 (the hour this step executes), PROTOCOL §4 diagnostic.
            # Forecast-side values only; the realized value is attached by run_origin after execution.
            extras = {"c_target_timestamp_h0": base.timestamps[0], "c_daylight_h0": bool(day[0]),
                      "c_elevation_bin_h0": None, "c_cloud_bin_h0": None,
                      "c_point_h0": float(pt_ghi[0] if ghi_space else pt_pv[0]), "c_lower_bound_h0": float(lb[0]),
                      "c_residual_space": self.qtable["residual_space"]}
            if day[0]:
                rule = self.qtable["bin_boundary_rule"]
                extras["c_elevation_bin_h0"] = int(cal.assign_bin(
                    elev[:1], self.qtable["elevation_bin_edges_deg"], cal.dim_rule(rule, "elevation"))[0])
                extras["c_cloud_bin_h0"] = int(cal.assign_bin(
                    cf[:1], self.qtable["cloud_bin_edges_fraction"], cal.dim_rule(rule, "cloud"))[0])
            return b, [float(x) for x in lb_pv], extras
        raise ArmInvalid(f"unknown solar forecast kind {kind}")


def arm_ebr(arm: str, s4a, crit_w: List[float], solar_w: List[float], wind_w: List[float]) -> List[float]:
    if ARM_CONFIGS[arm]["ebr"] == "governed":
        return s4a.compute_governed_ebr(crit_w)
    return s4a.compute_variant_sw_ebr(crit_w, solar_w, wind_w)


# ---------------------------------------------------------------------------- one origin
def run_origin(*, arm: str, origin_index: int, forecast_start: str, weather_df: pd.DataFrame,
               forecaster: ArmForecaster, optimizer, executor, router, elevation_provider, frozen,
               configs: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    from system.research.route_mode_propagation import propagate_route_mode
    from system.research.research_critical_demand_adapter import adapt_critical_demand_vector
    rs, rw, rd, rts = realized_inputs_for(weather_df, forecast_start)
    pkg = OriginCloudPackage(weather_df, forecast_start)
    t0 = (pd.Timestamp(forecast_start) - pd.Timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    state = make_initial_state(t0)
    bat = configs["battery"]
    e_min = float(bat.get("capacity_wh", 200000.0)) * float(bat.get("min_soc_pct", 20.0)) / 100.0
    eta_dis = float(bat.get("discharge_efficiency", 0.92))
    recorder = frozen.tel.ExecutedHourRecorder()
    hourly: List[Dict[str, Any]] = []
    for step in range(STEPS_PER_ORIGIN):
        cloud, held = pkg.trajectory(_parse_iso(state.timestamp))
        bundle, ebr_solar_w, c_cov = forecaster.predict(state, cloud)
        _, route = router.evaluate_and_route(state, bundle, configs)
        planning_state = propagate_route_mode(state, route)
        crit_w = adapt_critical_demand_vector(CRITICAL_CEILING_W, bundle.demand.point)
        wnd_w = list(bundle.wind_generation.point)
        elev = elevation_provider.get_elevation_vector(bundle.timestamps)
        ebr = arm_ebr(arm, frozen.s4a, crit_w, ebr_solar_w, wnd_w)
        step_cfg = dict(configs)
        step_cfg["critical_demand_w"] = crit_w
        step_cfg["ebr_target_wh"] = ebr
        step_cfg["terminal_target_wh"] = TERMINAL_TARGET_WH
        e_start = state.battery_energy_wh
        soc_before = state.battery_soc_pct
        plan = optimizer.optimize(bundle, planning_state, step_cfg)
        if plan.constraint_status not in ("OPTIMAL", "FEASIBLE"):
            raise ArmInvalid(f"{arm} optimizer status {plan.constraint_status} at origin {forecast_start} step {step}")
        diag0 = optimizer.last_diagnostics[0] if getattr(optimizer, "last_diagnostics", None) else {}
        res = executor.execute_step(state, plan, {"timestamp": rts[step], "actual_SW_IN": float(rs[step]),
                                                  "actual_wind_generation": float(rw[step]),
                                                  "actual_demand": float(rd[step])}, step_index=0)
        if res.busbar_energy_balance_error_w > 1e-3:
            raise ArmInvalid(f"{arm} busbar error {res.busbar_energy_balance_error_w} W at step {step}")
        d_real = res.demand_realized_w
        d_crit = min(CRITICAL_CEILING_W, d_real)
        s_tot = res.served_load_w
        recorder.record_resolve(origin_id=origin_index, arm=arm, step=step, planned_rows=optimizer.last_planned,
                                e_start_wh=e_start, pv_real_w=res.solar_realized_w, wind_real_w=res.wind_realized_w,
                                d_c_real_w=d_crit, e_min_wh=e_min, eta_dis=eta_dis)
        hourly.append({
            "origin_id": origin_index, "forecast_start": forecast_start, "hour": step, "timestamp": rts[step],
            "arm": arm, "result_label": ARM_CONFIGS[arm]["result_label"], "route": route,
            "optimizer_received_mode": planning_state.operating_mode,
            "solver_status": plan.constraint_status,
            "solver_status_native": str(diag0.get("solver_status", plan.constraint_status)),
            "em_rows_built": int(getattr(optimizer, "last_em_rows_built", 0)),
            "actual_solar": res.solar_realized_w, "actual_wind": res.wind_realized_w,
            "actual_demand": d_real, "critical_demand": d_crit, "served_load": s_tot,
            "unmet_load": res.unmet_load_w, "critical_served_first": min(d_crit, s_tot),
            "critical_served_prop": s_tot * (d_crit / d_real) if d_real > 0 else 0.0,
            "diesel_power": res.diesel_realized_w, "diesel_fuel": res.diesel_fuel_consumed_l,
            "diesel_fuel_remaining_l": res.diesel_fuel_remaining_l,
            "battery_charge": res.battery_charge_realized_w, "battery_discharge": res.battery_discharge_realized_w,
            "soc_before": soc_before, "soc_after": res.realized_soc_pct,
            "e_after_wh": float(res.next_state.battery_energy_wh),
            "curtailment": res.curtailment_w, "busbar_balance_error_w": res.busbar_energy_balance_error_w,
            "ebr_target_wh": ebr[0], "j2_shortfall_wh": diag0.get("j2_shortfall_wh", 0.0),
            "held_cloud_hours": int(held), "solar_elevation_t1_deg": float(elev[0]),
        })
        if c_cov:  # Arm C only: realized value in the calibration's residual space, same hour (after execution)
            if c_cov["c_target_timestamp_h0"] != rts[step]:
                raise ArmInvalid(f"C coverage record misaligned: {c_cov['c_target_timestamp_h0']} != {rts[step]}")
            act = (float(rs[step]) if c_cov["c_residual_space"] == "ghi_w_m2"
                   else float(forecaster.engine._ghi_to_solar_power_w(float(rs[step]))))  # same map as the bound
            hourly[-1].update(c_cov, c_actual_h0=act)
        state = res.next_state
    return hourly, recorder.as_dicts()


# ---------------------------------------------------------------------------- validity
REQUIRED_NUMERIC = ("unmet_load", "diesel_fuel", "soc_after", "critical_demand", "critical_served_first",
                    "critical_served_prop", "served_load", "e_after_wh")


def validate_run(hourly: pd.DataFrame, origins: List[str], arms=ARMS) -> List[str]:
    """Returns problems; an empty list is required before any result can be evaluated."""
    probs = []
    n_exp = len(origins) * STEPS_PER_ORIGIN
    for arm in arms:
        sub = hourly[hourly["arm"] == arm] if "arm" in hourly.columns else hourly.iloc[0:0]
        if len(sub) != n_exp:
            probs.append(f"{arm}: {len(sub)} hourly rows, expected {n_exp}")
            continue
        if sub.duplicated(["origin_id", "hour"]).any():
            probs.append(f"{arm}: duplicate (origin, hour) rows")
        if sorted(sub["forecast_start"].unique()) != sorted(origins):
            probs.append(f"{arm}: origin set differs from the evaluation population")
        if not sub["solver_status"].isin(["OPTIMAL", "FEASIBLE"]).all():
            probs.append(f"{arm}: non-optimal solver status present")
        vals = sub[list(REQUIRED_NUMERIC)].to_numpy(dtype=float)
        if not np.all(np.isfinite(vals)):
            probs.append(f"{arm}: non-finite values in required columns")
    return probs


# ---------------------------------------------------------------------------- preflight
def _pvlib_elev_utc(idx_utc):
    import pvlib
    loc = pvlib.location.Location(68.362074, 18.738752, tz="UTC")
    return loc.get_solarposition(pd.DatetimeIndex(idx_utc))["elevation"].values


def full_preflight(repo: Path, cfg: Dict[str, Any], mode: str) -> Tuple[pf.PreflightReport, Optional[Dict[str, Any]], Optional[str]]:
    """mode is 'preflight' (main --preflight) or 'execute' (execute()); there is no default. Only mode 'execute'
    requires the `execution` section (scope EXECUTE_EXPERIMENT); a preflight-only authorization never satisfies it."""
    if mode not in pf.AUTHORIZATION_MODES:
        raise ValueError(f"unknown preflight mode {mode!r}")
    rep = pf.PreflightReport(mode)
    rep.extend("decisions", pf.check_decisions(cfg, pf.EXECUTION_DECISIONS))
    rep.extend("gates", pf.check_gates(cfg))
    rep.extend("arm_c_method", pf.check_arm_c_method(cfg))
    rep.extend("arms", pf.check_arms(cfg, ARM_CONFIGS))
    rep.extend("hashes", pf.check_hashes(repo, cfg))
    rep.extend("package_manifest", pf.check_package_manifest(repo))
    rep.extend("preregistration", pf.check_preregistration_frozen(repo))
    rep.extend("output", pf.check_output_root(repo, cfg))
    n = cfg["evaluation"]["expected_origins"]
    aud = budget_audit(n, cfg)
    rep.extend("budget", pf.check_budget(cfg, aud["optimize_calls_per_arm"], aud["optimize_calls_total"]))
    art, art_sha = None, None
    try:
        import calibrate_arm_c as cal
        art, art_sha = cal.load_artifact(repo / cfg["paths"]["calibration_artifact"], cfg)
    except Exception as e:  # missing or invalid artifact blocks execution
        rep.failures.append(f"[calibration] {e}")
    rep.extend("authorization", pf.check_execution_authorization(repo, cfg, mode, art_sha))
    rep.extend("calibration_authorization", pf.check_calibration_authorization(repo, cfg, art))
    if not rep.ok:
        # Data contents are not opened while governance, configuration or hash checks fail.
        rep.failures.append("[inputs] input-content guards skipped because earlier checks failed")
        return rep, art, art_sha
    try:
        import timestamp_guards as tg
        tg.run_all_guards(str(repo), _pvlib_elev_utc)
        w = pd.read_csv(repo / cfg["paths"]["weather"])
        evaluation_origins(w, cfg)
    except Exception as e:
        rep.failures.append(f"[inputs] {type(e).__name__}: {e}")
    return rep, art, art_sha


# ---------------------------------------------------------------------------- execution
def _write_json_exclusive(path: Path, obj: Any) -> None:
    with open(path, "x") as f:
        json.dump(obj, f, indent=2, default=str)


def _status(path: Path, obj: Dict[str, Any]) -> None:
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=2, default=str)
    os.replace(tmp, path)


def execute(repo: Path, cfg: Dict[str, Any]) -> int:
    """Re-runs the full preflight itself (defence in depth: no caller can skip it), then makes a single
    attempt with no retries, stopping at the first failure. Returns 2 if preflight fails, before any
    optimizer, forecaster or output directory is created."""
    rep, calibration, calibration_sha = full_preflight(repo, cfg, "execute")
    if not rep.ok:
        print("PREFLIGHT FAILED — execution refused:", file=sys.stderr)
        for f in rep.failures:
            print("  " + f, file=sys.stderr)
        return 2
    # Defence in depth (D9 boundary): re-check the execute-scoped authorization immediately before any machinery.
    scope_fails = pf.check_execution_authorization(repo, cfg, "execute", calibration_sha)
    if scope_fails:
        print("EXECUTION REFUSED — no valid execute-scoped authorization:", file=sys.stderr)
        for f in scope_fails:
            print("  " + f, file=sys.stderr)
        return 2
    exec_ref = json.loads((repo / cfg["paths"]["authorization_record"]).read_text())["execution"]["execute_instruction_ref"]
    frozen = load_frozen()
    Planner = load_planner_class()
    from system.control.router import EMSControlRouter
    from system.simulation.research_realization_executor import ResearchRealizationExecutor

    root = repo / cfg["paths"]["results_root"]
    run_dir = root / f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    run_dir.mkdir(parents=False, exist_ok=False)  # never reuse or overwrite an existing run
    status_path = run_dir / "RUN_STATUS.json"
    status = {"status": "RUNNING", "started_utc": datetime.now(timezone.utc).isoformat(),
              "runner_sha256": pf.sha256_file(Path(__file__)), "calibration_artifact_sha256": calibration_sha,
              "execute_instruction_ref": exec_ref,
              "arms": {a: "PENDING" for a in ARMS}}
    _status(status_path, status)

    weather = pd.read_csv(repo / cfg["paths"]["weather"])
    origins = evaluation_origins(weather, cfg)
    hv = pd.read_csv(repo / cfg["paths"]["sites_hourly"])
    sites = dict(zip(pd.to_datetime(hv["TIMESTAMP"]), hv["SW_IN"].astype(float)))
    configs = load_canonical_configs(repo)
    budget = SolveBudget(cfg["budget"]["per_arm_ceiling"], cfg["budget"]["total_ceiling"])
    provider = frozen.s4a.SolarElevationProvider(None)
    hourly_all: List[Dict[str, Any]] = []
    exec_all: List[Dict[str, Any]] = []
    for arm in ARMS:
        status["arms"][arm] = "RUNNING"
        _status(status_path, status)
        try:
            fc = ArmForecaster(arm, sites_hourly=sites, calibration=calibration)
            opt = BudgetedOptimizer(Planner(reserve_enabled=True), budget, arm)
            ex = ResearchRealizationExecutor(configs)
            router = EMSControlRouter()
            for oi, fs in enumerate(origins, start=1):
                h, e = run_origin(arm=arm, origin_index=oi, forecast_start=fs, weather_df=weather, forecaster=fc,
                                  optimizer=opt, executor=ex, router=router, elevation_provider=provider,
                                  frozen=frozen, configs=configs)
                hourly_all.extend(h)
                exec_all.extend(e)
            status["arms"][arm] = "COMPLETE"
        except Exception as exc:
            status["arms"][arm] = "INVALID"
            status.update({"status": "FAILED", "failed_arm": arm, "error": f"{type(exc).__name__}: {exc}",
                           "traceback": traceback.format_exc(), "solves_used": budget.counts,
                           "ended_utc": datetime.now(timezone.utc).isoformat(),
                           "note": "Run FAILED. Partial output is not a result. No retry or recovery without new authorization."})
            _status(status_path, status)
            pd.DataFrame(hourly_all).to_csv(run_dir / "PARTIAL_HOURLY_TELEMETRY_INVALID.csv", index=False)
            return 3
        _status(status_path, status)

    hourly_df = pd.DataFrame(hourly_all)
    hourly_df.to_csv(run_dir / "HOURLY_TELEMETRY.csv", index=False)
    pd.DataFrame(exec_all).to_csv(run_dir / "EXECUTED_HOUR_TELEMETRY.csv", index=False)
    probs = validate_run(hourly_df, origins)
    if probs:
        status.update({"status": "FAILED", "validity_problems": probs, "solves_used": budget.counts})
        _status(status_path, status)
        return 4
    import gates_three_arm as gates
    results = gates.evaluate(hourly_df, cfg, ARM_CONFIGS, frozen.stat)
    results["solves_used"] = {"per_arm": budget.counts, "total": budget.used}
    _write_json_exclusive(run_dir / "RESULTS.json", results)
    status.update({"status": "COMPLETED", "ended_utc": datetime.now(timezone.utc).isoformat(),
                   "solves_used": budget.counts})
    _status(status_path, status)
    return 0


# ---------------------------------------------------------------------------- CLI
def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="EXP-THREE-ARM-2024 runner (fail-closed; no override).")
    ap.add_argument("--repo", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--audit-budget", action="store_true")
    g.add_argument("--preflight", action="store_true")
    g.add_argument("--execute", action="store_true")
    args = ap.parse_args(argv)
    repo = Path(args.repo).resolve()
    cfg = pf.load_config(repo)
    if args.audit_budget:
        print(json.dumps(budget_audit(cfg["evaluation"]["expected_origins"], cfg), indent=2))
        return 0
    if args.execute:
        return execute(repo, cfg)
    rep, _, _ = full_preflight(repo, cfg, "preflight")
    if not rep.ok:
        print("PREFLIGHT FAILED:", file=sys.stderr)
        for f in rep.failures:
            print("  " + f, file=sys.stderr)
        return 2
    print("PREFLIGHT PASSED. This does not start or authorize a run; --execute separately requires a valid "
          "execution section (scope EXECUTE_EXPERIMENT).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
