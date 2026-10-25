"""Synthetic DODS .ascii response fixtures. No fixture here was downloaded; every value
is hand-constructed to exercise the parser/validator, matching the ASCII-DODS text
shape the existing project's own parse_ascii_series already expects (variable name
line, then comma-separated value lines, until the next variable's name/Dataset line)."""
from datetime import datetime, timedelta, timezone

RUN_INIT = datetime(2024, 1, 19, 18, 0, 0, tzinfo=timezone.utc)
ORIGIN = datetime(2024, 1, 20, 0, 0, 0, tzinfo=timezone.utc)  # run_init + 6h


def _epoch(dt: datetime) -> float:
    return dt.timestamp()


def make_valid_ascii(run_init: datetime = RUN_INIT, n_time: int = 67) -> str:
    lwp_vals = [round(0.0001 * i, 6) for i in range(n_time)]
    iwp_vals = [round(0.00005 * i, 6) for i in range(n_time)]
    time_vals = [_epoch(run_init + timedelta(hours=h)) for h in range(n_time)]
    lines = [
        "Dataset {",
        f"forecast_reference_time, {_epoch(run_init)}",
        "pressure.pressure\n700.0",
        "time.time\n" + ",".join(str(v) for v in time_vals),
        "mass_fraction_of_cloud_condensed_water_in_air_pl.mass_fraction_of_cloud_condensed_water_in_air_pl\n"
        + ",".join(str(v) for v in lwp_vals),
        "mass_fraction_of_cloud_ice_in_air_pl.mass_fraction_of_cloud_ice_in_air_pl\n"
        + ",".join(str(v) for v in iwp_vals),
        "} meps_det_pl_20240119T18Z.ncml.ascii",
    ]
    return "\n".join(lines)


def make_empty_ascii() -> str:
    return ""


def make_missing_variable_ascii() -> str:
    """Has forecast_reference_time/time/pressure but is missing the IWP variable entirely."""
    time_vals = [_epoch(RUN_INIT + timedelta(hours=h)) for h in range(67)]
    lwp_vals = [round(0.0001 * i, 6) for i in range(67)]
    lines = [
        "Dataset {",
        f"forecast_reference_time, {_epoch(RUN_INIT)}",
        "pressure.pressure\n700.0",
        "time.time\n" + ",".join(str(v) for v in time_vals),
        "mass_fraction_of_cloud_condensed_water_in_air_pl.mass_fraction_of_cloud_condensed_water_in_air_pl\n"
        + ",".join(str(v) for v in lwp_vals),
        "}",
    ]
    return "\n".join(lines)


def make_wrong_run_ascii() -> str:
    """forecast_reference_time points to a DIFFERENT run than the one requested -- must
    be rejected as FAILED_RUN_MISMATCH, never silently accepted."""
    wrong_run = RUN_INIT - timedelta(hours=6)
    return make_valid_ascii(run_init=wrong_run)


def make_duplicate_time_ascii() -> str:
    n = 67
    time_vals = [_epoch(RUN_INIT + timedelta(hours=h)) for h in range(n)]
    time_vals[5] = time_vals[4]  # introduce a duplicate
    lwp_vals = [round(0.0001 * i, 6) for i in range(n)]
    iwp_vals = [round(0.00005 * i, 6) for i in range(n)]
    lines = [
        "Dataset {",
        f"forecast_reference_time, {_epoch(RUN_INIT)}",
        "pressure.pressure\n700.0",
        "time.time\n" + ",".join(str(v) for v in time_vals),
        "mass_fraction_of_cloud_condensed_water_in_air_pl.mass_fraction_of_cloud_condensed_water_in_air_pl\n"
        + ",".join(str(v) for v in lwp_vals),
        "mass_fraction_of_cloud_ice_in_air_pl.mass_fraction_of_cloud_ice_in_air_pl\n"
        + ",".join(str(v) for v in iwp_vals),
        "}",
    ]
    return "\n".join(lines)


def make_nonfinite_ascii() -> str:
    n = 67
    time_vals = [_epoch(RUN_INIT + timedelta(hours=h)) for h in range(n)]
    lwp_vals = [round(0.0001 * i, 6) for i in range(n)]
    lwp_vals[10] = float("nan")
    iwp_vals = [round(0.00005 * i, 6) for i in range(n)]
    lines = [
        "Dataset {",
        f"forecast_reference_time, {_epoch(RUN_INIT)}",
        "pressure.pressure\n700.0",
        "time.time\n" + ",".join(str(v) for v in time_vals),
        "mass_fraction_of_cloud_condensed_water_in_air_pl.mass_fraction_of_cloud_condensed_water_in_air_pl\n"
        + ",".join(("nan" if str(v) == "nan" else str(v)) for v in lwp_vals),
        "mass_fraction_of_cloud_ice_in_air_pl.mass_fraction_of_cloud_ice_in_air_pl\n"
        + ",".join(str(v) for v in iwp_vals),
        "}",
    ]
    return "\n".join(lines)


def make_short_time_ascii() -> str:
    """Time dimension too short to cover horizon 24 (lead hour 30) -- must be rejected
    as FAILED_DIM_MISMATCH / FAILED_HORIZON_OUT_OF_RANGE, not silently truncated."""
    n = 20  # far too short
    time_vals = [_epoch(RUN_INIT + timedelta(hours=h)) for h in range(n)]
    lwp_vals = [round(0.0001 * i, 6) for i in range(n)]
    iwp_vals = [round(0.00005 * i, 6) for i in range(n)]
    lines = [
        "Dataset {",
        f"forecast_reference_time, {_epoch(RUN_INIT)}",
        "pressure.pressure\n700.0",
        "time.time\n" + ",".join(str(v) for v in time_vals),
        "mass_fraction_of_cloud_condensed_water_in_air_pl.mass_fraction_of_cloud_condensed_water_in_air_pl\n"
        + ",".join(str(v) for v in lwp_vals),
        "mass_fraction_of_cloud_ice_in_air_pl.mass_fraction_of_cloud_ice_in_air_pl\n"
        + ",".join(str(v) for v in iwp_vals),
        "}",
    ]
    return "\n".join(lines)


def make_zero_value_ascii() -> str:
    """All-zero LWP/IWP -- a genuine physical value (clear air), must be accepted as OK,
    never confused with a missing/failed status."""
    n = 67
    time_vals = [_epoch(RUN_INIT + timedelta(hours=h)) for h in range(n)]
    lines = [
        "Dataset {",
        f"forecast_reference_time, {_epoch(RUN_INIT)}",
        "pressure.pressure\n700.0",
        "time.time\n" + ",".join(str(v) for v in time_vals),
        "mass_fraction_of_cloud_condensed_water_in_air_pl.mass_fraction_of_cloud_condensed_water_in_air_pl\n"
        + ",".join("0.0" for _ in range(n)),
        "mass_fraction_of_cloud_ice_in_air_pl.mass_fraction_of_cloud_ice_in_air_pl\n"
        + ",".join("0.0" for _ in range(n)),
        "}",
    ]
    return "\n".join(lines)
