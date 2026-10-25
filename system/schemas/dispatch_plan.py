"""
DispatchPlan Schema Definition (Version 1.0.0)
Strictly enforces 24-hour operational microgrid dispatch schedules, finite numerics,
physical non-negativity, and charge/discharge exclusivity.
"""
import json
import math
from typing import List, Dict, Any, Optional

class DispatchPlan:
    def __init__(
        self,
        schema_version: str,
        timestamps: List[str],
        solar_used: List[float],
        wind_used: List[float],
        battery_charge: List[float],
        battery_discharge: List[float],
        battery_soc: List[float],
        diesel_power: List[float],
        load_served: List[float],
        flexible_load_schedule: List[float],
        renewable_curtailment: List[float],
        unmet_load: List[float],
        objective_value: float,
        constraint_status: str,
        energy_balance_errors: List[float],
        j1_objective: Optional[float] = None,
        j2_objective: Optional[float] = None,
        j3_objective: Optional[float] = None,
        j4_objective: Optional[float] = None,
        reserve_shortfall: Optional[List[float]] = None,
        load_served_essential: Optional[List[float]] = None,
        unmet_essential: Optional[List[float]] = None,
        reservation_target_wh: Optional[List[float]] = None,
        outlook_triggered_flag: Optional[List[float]] = None,
        unmet_noncritical_load: Optional[List[float]] = None,
        j1b_objective: Optional[float] = None
    ):
        if schema_version != "1.0.0":
            raise ValueError(f"Unsupported schema_version '{schema_version}'; expected '1.0.0'.")

        if len(timestamps) != 24:
            raise ValueError("DispatchPlan must contain exactly 24 timestep entries.")

        # Helper validator for float list
        def validate_float_list(arr: List[float], name: str, non_negative: bool = True) -> List[float]:
            if len(arr) != 24:
                raise ValueError(f"DispatchPlan array '{name}' must contain exactly 24 entries.")
            res = []
            for idx, val in enumerate(arr):
                fval = float(val)
                if math.isnan(fval) or math.isinf(fval):
                    raise ValueError(f"DispatchPlan array '{name}' contains non-finite value (NaN/Inf) at index {idx}.")
                if non_negative and fval < -1e-4:
                    raise ValueError(f"DispatchPlan array '{name}' contains negative power value at index {idx}: {fval}.")
                res.append(max(0.0, fval) if non_negative else fval)
            return res

        self.schema_version = schema_version
        self.timestamps = timestamps
        self.solar_used = validate_float_list(solar_used, "solar_used")
        self.wind_used = validate_float_list(wind_used, "wind_used")
        self.battery_charge = validate_float_list(battery_charge, "battery_charge")
        self.battery_discharge = validate_float_list(battery_discharge, "battery_discharge")
        self.battery_soc = validate_float_list(battery_soc, "battery_soc", non_negative=False)
        self.diesel_power = validate_float_list(diesel_power, "diesel_power")
        self.load_served = validate_float_list(load_served, "load_served")
        self.flexible_load_schedule = validate_float_list(flexible_load_schedule, "flexible_load_schedule")
        self.renewable_curtailment = validate_float_list(renewable_curtailment, "renewable_curtailment")
        self.unmet_load = validate_float_list(unmet_load, "unmet_load")

        # Exclusivity validation
        for idx, (chg, dis) in enumerate(zip(self.battery_charge, self.battery_discharge)):
            if chg > 1.0 and dis > 1.0:
                raise ValueError(f"DispatchPlan violates charge/discharge exclusivity at index {idx}: charge={chg}, discharge={dis}.")

        f_obj = float(objective_value)
        if math.isnan(f_obj) or math.isinf(f_obj):
            raise ValueError("DispatchPlan objective_value must be finite.")
        self.objective_value = f_obj
        self.constraint_status = str(constraint_status)
        self.energy_balance_errors = validate_float_list(energy_balance_errors, "energy_balance_errors", non_negative=False)

        self.j1_objective = float(j1_objective) if j1_objective is not None else None
        self.j2_objective = float(j2_objective) if j2_objective is not None else None
        self.j3_objective = float(j3_objective) if j3_objective is not None else None
        self.j4_objective = float(j4_objective) if j4_objective is not None else None
        self.reserve_shortfall = validate_float_list(reserve_shortfall, "reserve_shortfall") if reserve_shortfall is not None else None

        # Research-only (MILP v2) additive fields. Optional and default None so that
        # callers producing schema_version 1.0.0 plans without these (e.g. the frozen
        # GAP19 control) are completely unaffected.
        self.load_served_essential = validate_float_list(load_served_essential, "load_served_essential") if load_served_essential is not None else None
        self.unmet_essential = validate_float_list(unmet_essential, "unmet_essential") if unmet_essential is not None else None

        # RT-01 Stage 2 (ems/reports/rt01_runtime_fixes/RT01_CROSS_HORIZON_RESERVATION_DESIGN_MEMO.md Sec.2/6,
        # RT01_STAGE2_FORECAST_OUTLOOK_RESERVATION_REPORT.md). Research-only
        # diagnostic fields, additive and optional (default None) so every
        # existing caller/consumer (including the frozen GAP19 control and
        # Stage 1's own tests) is completely unaffected. Mirrors the same
        # 24-length-array-with-value-only-at-index-23 convention already used
        # by `reserve_shortfall` above -- NOT a new per-timestep flow.
        self.reservation_target_wh = validate_float_list(reservation_target_wh, "reservation_target_wh") if reservation_target_wh is not None else None
        self.outlook_triggered_flag = validate_float_list(outlook_triggered_flag, "outlook_triggered_flag") if outlook_triggered_flag is not None else None

        # J1b (non-critical unmet load penalty, see gap19_highs_native.py). Additive
        # and optional (default None) so every existing caller/consumer producing
        # schema_version 1.0.0 plans without it is completely unaffected.
        self.unmet_noncritical_load = validate_float_list(unmet_noncritical_load, "unmet_noncritical_load") if unmet_noncritical_load is not None else None
        self.j1b_objective = float(j1b_objective) if j1b_objective is not None else None

    def to_dict(self) -> Dict[str, Any]:
        res = {
            "schema_version": self.schema_version,
            "timestamps": self.timestamps,
            "solar_used": self.solar_used,
            "wind_used": self.wind_used,
            "battery_charge": self.battery_charge,
            "battery_discharge": self.battery_discharge,
            "battery_soc": self.battery_soc,
            "diesel_power": self.diesel_power,
            "load_served": self.load_served,
            "flexible_load_schedule": self.flexible_load_schedule,
            "renewable_curtailment": self.renewable_curtailment,
            "unmet_load": self.unmet_load,
            "objective_value": self.objective_value,
            "constraint_status": self.constraint_status,
            "energy_balance_errors": self.energy_balance_errors
        }
        if self.j1_objective is not None:
            res["j1_objective"] = self.j1_objective
        if self.j2_objective is not None:
            res["j2_objective"] = self.j2_objective
        if self.j3_objective is not None:
            res["j3_objective"] = self.j3_objective
        if self.j4_objective is not None:
            res["j4_objective"] = self.j4_objective
        if self.reserve_shortfall is not None:
            res["reserve_shortfall"] = self.reserve_shortfall
        if self.load_served_essential is not None:
            res["load_served_essential"] = self.load_served_essential
        if self.unmet_essential is not None:
            res["unmet_essential"] = self.unmet_essential
        if self.reservation_target_wh is not None:
            res["reservation_target_wh"] = self.reservation_target_wh
        if self.outlook_triggered_flag is not None:
            res["outlook_triggered_flag"] = self.outlook_triggered_flag
        if self.unmet_noncritical_load is not None:
            res["unmet_noncritical_load"] = self.unmet_noncritical_load
        if self.j1b_objective is not None:
            res["j1b_objective"] = self.j1b_objective
        return res

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DispatchPlan':
        return cls(
            schema_version=data["schema_version"],
            timestamps=data["timestamps"],
            solar_used=data["solar_used"],
            wind_used=data["wind_used"],
            battery_charge=data["battery_charge"],
            battery_discharge=data["battery_discharge"],
            battery_soc=data["battery_soc"],
            diesel_power=data["diesel_power"],
            load_served=data["load_served"],
            flexible_load_schedule=data["flexible_load_schedule"],
            renewable_curtailment=data["renewable_curtailment"],
            unmet_load=data["unmet_load"],
            objective_value=data["objective_value"],
            constraint_status=data["constraint_status"],
            energy_balance_errors=data.get("energy_balance_errors", [0.0]*24),
            j1_objective=data.get("j1_objective"),
            j2_objective=data.get("j2_objective"),
            j3_objective=data.get("j3_objective"),
            j4_objective=data.get("j4_objective"),
            reserve_shortfall=data.get("reserve_shortfall"),
            load_served_essential=data.get("load_served_essential"),
            unmet_essential=data.get("unmet_essential"),
            reservation_target_wh=data.get("reservation_target_wh"),
            outlook_triggered_flag=data.get("outlook_triggered_flag"),
            unmet_noncritical_load=data.get("unmet_noncritical_load"),
            j1b_objective=data.get("j1b_objective")
        )

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

