"""
Local Baseline ForecastEngine Implementation
Deterministic persistence & clear-sky baseline.
Marked explicitly as PROTOTYPE_UNVALIDATED.
"""
import math
import yaml
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

from system.forecasting.interface.base import ForecastEngine
from system.schemas.forecast_bundle import ForecastBundle, TimeseriesForecast
from system.schemas.station_state import StationState

class LocalBaselineForecastEngine(ForecastEngine):
    def __init__(self, pv_config_path: Path):
        self.pv_config_path = pv_config_path
        if pv_config_path.exists():
            with open(pv_config_path, "r") as f:
                self.pv_config = yaml.safe_load(f)
        else:
            self.pv_config = {
                "array_area_m2": 300.0,
                "panel_efficiency": 0.20,
                "performance_ratio": 0.85,
                "max_inverter_power_w": 60000.0
            }

    def _irradiance_to_power_w(self, irradiance_w_m2: float) -> float:
        raw_power = (
            irradiance_w_m2 *
            self.pv_config["array_area_m2"] *
            self.pv_config["panel_efficiency"] *
            self.pv_config["performance_ratio"]
        )
        return min(raw_power, self.pv_config["max_inverter_power_w"])

    def predict(self, station_state: StationState, runtime_context: Dict[str, Any]) -> ForecastBundle:
        origin_ts_str = station_state.timestamp
        try:
            origin_dt = datetime.fromisoformat(origin_ts_str.replace("Z", "+00:00"))
        except Exception:
            origin_dt = datetime.utcnow()

        timestamps = []
        solar_irr_pts = []
        solar_gen_pts = []
        wind_gen_pts = []
        demand_pts = []

        history = runtime_context.get("history", [])
        last_obs_irr = station_state.last_observed_solar_irradiance
        last_obs_wind = station_state.last_observed_wind_generation
        last_obs_demand = station_state.last_observed_demand

        for h in range(1, 25):
            future_dt = origin_dt + timedelta(hours=h)
            timestamps.append(future_dt.strftime("%Y-%m-%dT%H:%M:%SZ"))

            hour = future_dt.hour
            # Diurnal solar clear-sky curve simulation for demonstration
            if 4 <= hour <= 20:
                solar_sin = math.sin((hour - 4) * math.pi / 16.0)
                cs_ghi = 800.0 * solar_sin
                # Diurnal decay persistence cloud factor
                irr = round(cs_ghi * 0.75, 2)
            else:
                irr = 0.0

            solar_irr_pts.append(irr)
            solar_gen_pts.append(round(self._irradiance_to_power_w(irr), 2))

            # Wind persistence with diurnal wave
            w_val = max(0.0, round(last_obs_wind + 5000.0 * math.sin(h * math.pi / 6.0), 2))
            wind_gen_pts.append(w_val)

            # Demand persistence with morning/evening peaks
            d_val = max(10000.0, round(last_obs_demand + 3000.0 * math.cos(h * math.pi / 12.0), 2))
            demand_pts.append(d_val)

        # Optional deterministic forecast error perturbation diagnostic
        perturb_mode = runtime_context.get("forecast_perturbation_mode", "baseline")
        if perturb_mode == "renewable_underprediction":
            solar_irr_pts = [round(x * 0.8, 2) for x in solar_irr_pts]
            solar_gen_pts = [round(x * 0.8, 2) for x in solar_gen_pts]
            wind_gen_pts = [round(x * 0.8, 2) for x in wind_gen_pts]
        elif perturb_mode == "demand_overprediction":
            demand_pts = [round(x * 1.2, 2) for x in demand_pts]

        # --- RT-01 Stage 2: genuine forecast-outlook signal -----------------
        # Per ems/reports/rt01_runtime_fixes/RT01_CROSS_HORIZON_RESERVATION_DESIGN_MEMO.md Sec.2 (Candidate 4,
        # Stage 2): compute a bounded-lookahead "extended_outlook" beyond the
        # mandatory 24h ForecastBundle horizon, using the SAME imperfect
        # persistence methodology this engine already uses, with an EXPLICIT
        # uncertainty discount that decays with lookahead distance. Attached
        # only to ForecastBundle.metadata (free-form, already unvalidated) --
        # no schema change.
        #
        # Signal construction (seasonal/day-ago persistence, NOT perfect
        # foresight): for each extended lookahead hour h (25..cap), the
        # wind/demand projection uses the REAL ACTUAL observation from exactly
        # k*24h before that hour (k = smallest integer with
        # current_index + h - 24k <= current_index, i.e. the most recent valid
        # "same hour of day" actual on record) drawn from
        # `runtime_context["history"]` -- which `DataProvider.get_runtime_state`
        # already restricts to `timesteps[:current_index+1]` (strictly PAST
        # actuals only, never future/leaked data; verified in
        # system/data/provider.py). If no such history entry exists yet (early
        # steps), this falls back to the SAME scalar-anchor persistence formula
        # already used for the base 24h forecast above -- never a different,
        # more-informed method than what is genuinely available. Solar uses the
        # same deterministic clear-sky diurnal curve (a pure function of
        # hour-of-day in this model, requiring no anchor).
        #
        # `confidence` is an explicit, documented, monotonically-decreasing
        # function of lookahead distance beyond the mandatory 24h horizon (1.0
        # just past hour 24, decaying linearly to a configurable floor at the
        # lookahead cap) -- this is the "explicit confidence discount" the
        # design memo requires, not an unqualified point forecast.
        lookahead_cap_h = int(runtime_context.get("extended_outlook_lookahead_h", 72))
        min_confidence_floor = float(runtime_context.get("extended_outlook_min_confidence_floor", 0.05))
        current_index = runtime_context.get("current_index")
        if current_index is None:
            current_index = max(0, len(history) - 1)

        worst_margin_wh = None
        worst_h = None
        worst_confidence = None
        if lookahead_cap_h > 24:
            for h in range(25, lookahead_cap_h + 1):
                future_dt_ext = origin_dt + timedelta(hours=h)
                hour_ext = future_dt_ext.hour
                if 4 <= hour_ext <= 20:
                    solar_sin_ext = math.sin((hour_ext - 4) * math.pi / 16.0)
                    irr_ext = round(800.0 * solar_sin_ext * 0.75, 2)
                else:
                    irr_ext = 0.0
                solar_gen_ext = self._irradiance_to_power_w(irr_ext)

                k = -(-h // 24)  # ceil(h/24), smallest k with current_index+h-24k <= current_index
                day_ago_idx = current_index + h - 24 * k
                if 0 <= day_ago_idx <= current_index and day_ago_idx < len(history):
                    anchor_entry = history[day_ago_idx]
                    wind_ext = max(0.0, float(anchor_entry.get("actual_wind_generation", last_obs_wind)))
                    demand_ext = max(10000.0, float(anchor_entry.get("actual_demand", last_obs_demand)))
                else:
                    # Fallback: identical scalar-anchor persistence formula used
                    # for the mandatory 24h horizon above -- not a more-informed
                    # substitute.
                    wind_ext = max(0.0, last_obs_wind + 5000.0 * math.sin(h * math.pi / 6.0))
                    demand_ext = max(10000.0, last_obs_demand + 3000.0 * math.cos(h * math.pi / 12.0))

                net_margin_wh_ext = solar_gen_ext + wind_ext - demand_ext

                if worst_margin_wh is None or net_margin_wh_ext < worst_margin_wh:
                    worst_margin_wh = net_margin_wh_ext
                    worst_h = h
                    # Linear confidence decay: 1.0 just past the mandatory 24h
                    # horizon (h=25), down to min_confidence_floor at h=lookahead_cap_h.
                    span = max(1, lookahead_cap_h - 25)
                    decay_frac = (h - 25) / float(span)
                    worst_confidence = max(min_confidence_floor, 1.0 - decay_frac * (1.0 - min_confidence_floor))

        extended_outlook = None
        if worst_margin_wh is not None:
            extended_outlook = {
                "lookahead_h": lookahead_cap_h,
                "projected_min_net_renewable_margin_wh": round(worst_margin_wh, 2),
                "projected_min_net_renewable_margin_hour_offset": worst_h,
                "confidence": round(worst_confidence, 4),
                "methodology": "persistence_day_ago_seasonal_plus_clearsky_solar_v1",
                "status": "PROTOTYPE_UNVALIDATED",
                "note": "Imperfect persistence-style projection beyond the mandatory 24h ForecastBundle horizon; uses only actuals observed at or before the forecast origin (no future leakage). NOT a validated weather forecast.",
            }
        # --- END RT-01 Stage 2 extended_outlook signal -----------------------

        # Uncertainty bounds (10% bounds for demonstration)
        solar_irr_lower = [round(x * 0.9, 2) for x in solar_irr_pts]
        solar_irr_upper = [round(x * 1.1, 2) for x in solar_irr_pts]

        solar_gen_lower = [round(x * 0.9, 2) for x in solar_gen_pts]
        solar_gen_upper = [round(x * 1.1, 2) for x in solar_gen_pts]

        wind_lower = [round(x * 0.85, 2) for x in wind_gen_pts]
        wind_upper = [round(x * 1.15, 2) for x in wind_gen_pts]

        demand_lower = [round(x * 0.95, 2) for x in demand_pts]
        demand_upper = [round(x * 1.05, 2) for x in demand_pts]

        metadata = {
            "model_id": "polaris_local_baseline_persistence_v1",
            "model_version": "1.0.0",
            "feature_version": "local_causal_history_v1",
            "generation_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "status": "PROTOTYPE_UNVALIDATED",
            "research_qualification": "Operational 24h forecasting pipeline is an unvalidated prototype implementation; specific research validation applies only to H7-H12 diagnostic probes."
        }
        if extended_outlook is not None:
            # RT-01 Stage 2 (ems/reports/rt01_runtime_fixes/RT01_CROSS_HORIZON_RESERVATION_DESIGN_MEMO.md
            # Sec.2/6). Free-form metadata field; absent entirely when
            # lookahead_cap_h <= 24 (fully backward-compatible / opt-out).
            metadata["extended_outlook"] = extended_outlook

        return ForecastBundle(
            schema_version="1.0.0",
            origin_timestamp=origin_ts_str,
            horizon_hours=24,
            timestamps=timestamps,
            solar_irradiance=TimeseriesForecast(solar_irr_pts, solar_irr_lower, solar_irr_upper, "W/m^2"),
            solar_generation=TimeseriesForecast(solar_gen_pts, solar_gen_lower, solar_gen_upper, "W"),
            wind_generation=TimeseriesForecast(wind_gen_pts, wind_lower, wind_upper, "W"),
            demand=TimeseriesForecast(demand_pts, demand_lower, demand_upper, "W"),
            metadata=metadata
        )
