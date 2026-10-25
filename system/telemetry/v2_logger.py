"""
POLARIS V2 Observational Telemetry Logger Module
Hardened Schema Implementation — Exactly 37 Fields

This module implements passive, non-intervening telemetry data structures and
serialization utilities for POLARIS Stage8.1 → EMS Mechanism Observability (V2).

Governance Contract:
- TOTAL FIELDS = 37 UNIQUE FIELDS
- DIRECTLY_AVAILABLE = 23
- REQUIRES_INSTRUMENTATION = 14
- NOT_AVAILABLE = 0
- NON-INTERVENTION: Zero mutation of solver, optimizer, simulator, or forecast inputs/outputs.
"""

import json
import csv
from dataclasses import dataclass, asdict, fields
from typing import List, Dict, Any, Optional, Union
from pathlib import Path


REQUIRED_37_FIELDS = [
    # Identity (4)
    "origin_id",
    "origin_timestamp",
    "mpc_timestep_idx",
    "timestamp",
    # Forecast Input (8)
    "treatment_forecast_vector_24",
    "control_forecast_vector_24",
    "actual_solar_truth",
    "treatment_h1_forecast",
    "control_h1_forecast",
    "treatment_forecast_error_h1",
    "control_forecast_error_h1",
    "forecast_difference_h1",
    # State Before Action (4)
    "soc_before",
    "diesel_state_before",
    "cumulative_diesel_fuel_before",
    "cumulative_diesel_energy_before",
    # Optimizer (9)
    "optimizer_status",
    "objective_value",
    "diesel_commitment",
    "startup_event",
    "shutdown_event",
    "battery_charge_decision",
    "battery_discharge_decision",
    "reserve_status",
    "constraint_status",
    # Executed Action (7)
    "h1_diesel_power",
    "h1_battery_charge_power",
    "h1_battery_discharge_power",
    "h1_renewable_dispatch",
    "h1_renewable_curtailment",
    "h1_served_load",
    "h1_unmet_load",
    # State After Action (5)
    "soc_after",
    "diesel_state_after",
    "cumulative_diesel_fuel_after",
    "cumulative_diesel_energy_after",
    "cumulative_battery_throughput_after",
]

AVAILABILITY_CLASSIFICATION = {
    # Identity (4)
    "origin_id": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "origin_timestamp": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "mpc_timestep_idx": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "timestamp": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    # Forecast Input (8)
    "treatment_forecast_vector_24": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "control_forecast_vector_24": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "actual_solar_truth": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "treatment_h1_forecast": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "control_h1_forecast": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "treatment_forecast_error_h1": "REQUIRES_EXECUTION_CODE_INSTRUMENTATION",
    "control_forecast_error_h1": "REQUIRES_EXECUTION_CODE_INSTRUMENTATION",
    "forecast_difference_h1": "REQUIRES_EXECUTION_CODE_INSTRUMENTATION",
    # State Before Action (4)
    "soc_before": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "diesel_state_before": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "cumulative_diesel_fuel_before": "REQUIRES_EXECUTION_CODE_INSTRUMENTATION",
    "cumulative_diesel_energy_before": "REQUIRES_EXECUTION_CODE_INSTRUMENTATION",
    # Optimizer (9)
    "optimizer_status": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "objective_value": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "diesel_commitment": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "startup_event": "REQUIRES_EXECUTION_CODE_INSTRUMENTATION",
    "shutdown_event": "REQUIRES_EXECUTION_CODE_INSTRUMENTATION",
    "battery_charge_decision": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "battery_discharge_decision": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "reserve_status": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "constraint_status": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    # Executed Action (7)
    "h1_diesel_power": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "h1_battery_charge_power": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "h1_battery_discharge_power": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "h1_renewable_dispatch": "REQUIRES_EXECUTION_CODE_INSTRUMENTATION",
    "h1_renewable_curtailment": "REQUIRES_EXECUTION_CODE_INSTRUMENTATION",
    "h1_served_load": "REQUIRES_EXECUTION_CODE_INSTRUMENTATION",
    "h1_unmet_load": "REQUIRES_EXECUTION_CODE_INSTRUMENTATION",
    # State After Action (5)
    "soc_after": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "diesel_state_after": "DIRECTLY_AVAILABLE_IN_EXISTING_EXECUTION_OBJECT",
    "cumulative_diesel_fuel_after": "REQUIRES_EXECUTION_CODE_INSTRUMENTATION",
    "cumulative_diesel_energy_after": "REQUIRES_EXECUTION_CODE_INSTRUMENTATION",
    "cumulative_battery_throughput_after": "REQUIRES_EXECUTION_CODE_INSTRUMENTATION",
}


@dataclass
class V2TelemetryRecord:
    """
    Authoritative 37-field V2 Observational Telemetry Record.
    Preserves exact floating-point numerics and explicit pair/timestep identity.
    """
    # Identity (4)
    origin_id: int
    origin_timestamp: str
    mpc_timestep_idx: int
    timestamp: str

    # Forecast Input (8)
    treatment_forecast_vector_24: List[float]
    control_forecast_vector_24: List[float]
    actual_solar_truth: float
    treatment_h1_forecast: float
    control_h1_forecast: float
    treatment_forecast_error_h1: float
    control_forecast_error_h1: float
    forecast_difference_h1: float

    # State Before Action (4)
    soc_before: float
    diesel_state_before: bool
    cumulative_diesel_fuel_before: float
    cumulative_diesel_energy_before: float

    # Optimizer (9)
    optimizer_status: str
    objective_value: float
    diesel_commitment: float
    startup_event: bool
    shutdown_event: bool
    battery_charge_decision: float
    battery_discharge_decision: float
    reserve_status: str
    constraint_status: str

    # Executed Action (7)
    h1_diesel_power: float
    h1_battery_charge_power: float
    h1_battery_discharge_power: float
    h1_renewable_dispatch: float
    h1_renewable_curtailment: float
    h1_served_load: float
    h1_unmet_load: float

    # State After Action (5)
    soc_after: float
    diesel_state_after: bool
    cumulative_diesel_fuel_after: float
    cumulative_diesel_energy_after: float
    cumulative_battery_throughput_after: float

    def validate(self) -> None:
        """Validates schema completeness, types, and vector dimensions."""
        rec_fields = [f.name for f in fields(self)]
        if set(rec_fields) != set(REQUIRED_37_FIELDS):
            missing = set(REQUIRED_37_FIELDS) - set(rec_fields)
            extra = set(rec_fields) - set(REQUIRED_37_FIELDS)
            raise ValueError(f"V2TelemetryRecord field set mismatch! Missing: {missing}, Extra: {extra}")

        if len(rec_fields) != 37 or len(set(rec_fields)) != 37:
            raise ValueError(f"V2TelemetryRecord field count must be exactly 37 unique fields, got {len(rec_fields)}")

        if len(self.treatment_forecast_vector_24) != 24:
            raise ValueError(f"treatment_forecast_vector_24 must have length 24, got {len(self.treatment_forecast_vector_24)}")

        if len(self.control_forecast_vector_24) != 24:
            raise ValueError(f"control_forecast_vector_24 must have length 24, got {len(self.control_forecast_vector_24)}")

    def to_dict(self) -> Dict[str, Any]:
        """Converts to dictionary representation, preserving raw exact floats."""
        self.validate()
        return asdict(self)

    def to_csv_dict(self) -> Dict[str, Any]:
        """Converts to flat dictionary suitable for CSV writing, encoding vectors as JSON strings."""
        d = self.to_dict()
        d["treatment_forecast_vector_24"] = json.dumps(d["treatment_forecast_vector_24"])
        d["control_forecast_vector_24"] = json.dumps(d["control_forecast_vector_24"])
        return d


class V2TelemetryCollector:
    """
    Passive observational collector for V2 Telemetry.
    Accumulates records in-memory and exports to JSON/CSV deterministically.
    """

    def __init__(self):
        self.records: List[V2TelemetryRecord] = []

    def add_record(self, record: V2TelemetryRecord) -> None:
        record.validate()
        self.records.append(record)

    def record_step(
        self,
        origin_id: int,
        origin_timestamp: str,
        mpc_timestep_idx: int,
        timestamp: str,
        treatment_forecast_vector_24: List[float],
        control_forecast_vector_24: List[float],
        actual_solar_truth: float,
        soc_before: float,
        diesel_state_before: bool,
        cumulative_diesel_fuel_before: float,
        cumulative_diesel_energy_before: float,
        optimizer_status: str,
        objective_value: float,
        diesel_commitment: float,
        battery_charge_decision: float,
        battery_discharge_decision: float,
        reserve_status: str,
        constraint_status: str,
        h1_diesel_power: float,
        h1_battery_charge_power: float,
        h1_battery_discharge_power: float,
        h1_renewable_dispatch: float,
        h1_renewable_curtailment: float,
        h1_served_load: float,
        h1_unmet_load: float,
        soc_after: float,
        diesel_state_after: bool,
        cumulative_diesel_fuel_after: float,
        cumulative_diesel_energy_after: float,
        cumulative_battery_throughput_after: float,
    ) -> V2TelemetryRecord:
        """
        Calculates derived forensics passively and constructs a validated V2TelemetryRecord.
        """
        # Exact forecast extractions and derived errors
        treatment_h1 = float(treatment_forecast_vector_24[0])
        control_h1 = float(control_forecast_vector_24[0])
        actual_truth = float(actual_solar_truth)

        treatment_error_h1 = treatment_h1 - actual_truth
        control_error_h1 = control_h1 - actual_truth
        forecast_diff_h1 = treatment_h1 - control_h1

        # Event logic
        startup_event = (not diesel_state_before) and bool(diesel_commitment > 0.5)
        shutdown_event = diesel_state_before and bool(diesel_commitment <= 0.5)

        record = V2TelemetryRecord(
            origin_id=int(origin_id),
            origin_timestamp=str(origin_timestamp),
            mpc_timestep_idx=int(mpc_timestep_idx),
            timestamp=str(timestamp),
            treatment_forecast_vector_24=[float(v) for v in treatment_forecast_vector_24],
            control_forecast_vector_24=[float(v) for v in control_forecast_vector_24],
            actual_solar_truth=actual_truth,
            treatment_h1_forecast=treatment_h1,
            control_h1_forecast=control_h1,
            treatment_forecast_error_h1=treatment_error_h1,
            control_forecast_error_h1=control_error_h1,
            forecast_difference_h1=forecast_diff_h1,
            soc_before=float(soc_before),
            diesel_state_before=bool(diesel_state_before),
            cumulative_diesel_fuel_before=float(cumulative_diesel_fuel_before),
            cumulative_diesel_energy_before=float(cumulative_diesel_energy_before),
            optimizer_status=str(optimizer_status),
            objective_value=float(objective_value),
            diesel_commitment=float(diesel_commitment),
            startup_event=bool(startup_event),
            shutdown_event=bool(shutdown_event),
            battery_charge_decision=float(battery_charge_decision),
            battery_discharge_decision=float(battery_discharge_decision),
            reserve_status=str(reserve_status),
            constraint_status=str(constraint_status),
            h1_diesel_power=float(h1_diesel_power),
            h1_battery_charge_power=float(h1_battery_charge_power),
            h1_battery_discharge_power=float(h1_battery_discharge_power),
            h1_renewable_dispatch=float(h1_renewable_dispatch),
            h1_renewable_curtailment=float(h1_renewable_curtailment),
            h1_served_load=float(h1_served_load),
            h1_unmet_load=float(h1_unmet_load),
            soc_after=float(soc_after),
            diesel_state_after=bool(diesel_state_after),
            cumulative_diesel_fuel_after=float(cumulative_diesel_fuel_after),
            cumulative_diesel_energy_after=float(cumulative_diesel_energy_after),
            cumulative_battery_throughput_after=float(cumulative_battery_throughput_after),
        )

        self.add_record(record)
        return record

    def export_json(self, output_path: Optional[Union[str, Path]] = None) -> str:
        """Deterministic JSON export preserving raw floats and ordering."""
        data = [r.to_dict() for r in self.records]
        serialized = json.dumps(data, indent=2, sort_keys=False)
        if output_path:
            Path(output_path).write_text(serialized, encoding="utf-8")
        return serialized

    def export_csv(self, output_path: Optional[Union[str, Path]] = None) -> str:
        """Deterministic CSV export."""
        if not self.records:
            return ""
        
        rows = [r.to_csv_dict() for r in self.records]
        fieldnames = REQUIRED_37_FIELDS

        import io
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
        csv_str = output.getvalue()

        if output_path:
            Path(output_path).write_text(csv_str, encoding="utf-8")
        return csv_str
