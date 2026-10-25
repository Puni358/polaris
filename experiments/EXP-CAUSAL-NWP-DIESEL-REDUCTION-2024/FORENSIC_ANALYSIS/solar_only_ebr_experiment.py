"""
Six-origin SOLAR-ONLY critical-aware EBR diagnostic (research-only).

Arms (same origins, forecasts, initial states, executor, terminal target, GAP19 unmodified):
  A = frozen Arm B        : governed EBR (config has no ebr_target_wh key)
  W = critical-aware EBR  : EBR = (1/eta) sum max(0, crit - solar - wind) dt        (previous experiment)
  S = solar-only EBR      : EBR = (1/eta) sum max(0, crit - solar) dt                (this experiment)

The ONLY difference between W and S is the subtracted term (wind dropped). Both are computed by a
research wrapper around GAP19 and passed as a 24-element list through the existing config path.
Terminal target unchanged. min_e floor unchanged. No tuning.
"""
import importlib.util
import json
import math
import os
import sys
from multiprocessing import Pool
from pathlib import Path

REPO = Path("/home/punith-bs/01polaris (Copy)")
os.chdir(REPO)
sys.path.insert(0, str(REPO))
HERE = REPO / "experiments/EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024/FORENSIC_ANALYSIS"
OUT = HERE / "solar_only_ebr"
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("cae", HERE / "critical_aware_ebr_experiment.py")
cae = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cae)

ETA = cae.ETA_DIS
DT = cae.DT
CRIT_W = cae.CRIT_W
ORIGINS = cae.ORIGINS
FROZEN = cae.FROZEN
WEATHER = cae.WEATHER


def ebr_solar_only(crit, solar_w, wind_w_ignored=None):
    """Reserve over 6 h of critical energy not covered by forecast SOLAR only. Wh per hour t."""
    assert len(crit) == len(solar_w) == 24
    out = []
    for t in range(24):
        end_k = min(t + 6, 24)
        s = 0.0
        for k in range(t, end_k):
            s += max(0.0, crit[k] - solar_w[k]) * DT
        out.append(s / ETA)
    assert all(math.isfinite(v) and v >= 0.0 for v in out), "reserve must be finite and non-negative"
    return out


def _check():
    """Pre-run verification: formula identity and isolation from the wind term."""
    z = [0.0] * 24
    crit = [11600.0] * 24
    sol = [0.0, 0.0, 500.0, 2000.0] + [0.0] * 20
    wnd = [3000.0] * 24
    # 1. zero solar -> solar-only equals governed formula
    gov = cae.ebr_governed(crit)
    so0 = ebr_solar_only(crit, z)
    assert all(abs(a - b) < 1e-9 for a, b in zip(so0, gov)), "solar-only identity failed"
    # 2. solar-only must ignore wind: result independent of wind
    assert ebr_solar_only(crit, sol) == ebr_solar_only(crit, sol, wnd), "wind leaked into solar-only"
    # 3. solar-only >= wind-including reserve for the same inputs (wind only removes reserve)
    so = ebr_solar_only(crit, sol)
    cw = cae.ebr_critical_aware(crit, sol, wnd)
    assert all(a >= b - 1e-9 for a, b in zip(so, cw)), "solar-only must not be below wind-including reserve"
    # 4. non-negative
    assert all(v >= 0 for v in so)


class CaptureOpt2:
    def __init__(self, inner, mode, sink):
        self.inner, self.mode, self.sink = inner, mode, sink

    def optimize(self, bundle, state, cfg):
        crit = list(cfg["critical_demand_w"])
        ebr_used = None
        cfg2 = cfg
        if self.mode == "W":
            ebr_used = cae.ebr_critical_aware(crit, bundle.solar_generation.point, bundle.wind_generation.point)
        elif self.mode == "S":
            ebr_used = ebr_solar_only(crit, bundle.solar_generation.point)
        if ebr_used is not None:
            cfg2 = dict(cfg)
            cfg2["ebr_target_wh"] = ebr_used
        plan = self.inner.optimize(bundle, state, cfg2)
        self.sink.append({
            "forecast_solar_w": list(bundle.solar_generation.point),
            "forecast_wind_w": list(bundle.wind_generation.point),
            "forecast_demand_w": list(bundle.demand.point),
            "crit_w": crit,
            "ebr_used_wh": ebr_used,
            "plan_soc_pct": list(plan.battery_soc),
            "plan_reserve_shortfall": list(plan.reserve_shortfall),
            "plan_status": plan.constraint_status,
        })
        return plan


def run_arm2(mode, fs, t0):
    from system.research.research_critical_demand_adapter import AdaptedClosedLoopRunner
    from system.forecasting.implementations.causal_nwp_physics import CausalNwpPhysicsForecastEngine
    cfg = cae._CFG["base"]   # all arms use the base config; the reserve is injected per step by the wrapper
    import math as _m
    sub = WEATHER[WEATHER["forecast_start"] == fs]
    rs = sub["actual_SW_IN"].tolist()
    rts = [ts.replace(" ", "T") + "Z" for ts in sub["timestamp"].tolist()]
    rw = [max(0.0, round(4500.0 + 5000.0 * _m.sin(h * _m.pi / 6.0), 2)) for h in range(1, 25)]
    rd = [max(10000.0, round(15000.0 + 3000.0 * _m.cos(h * _m.pi / 12.0), 2)) for h in range(1, 25)]
    runner = AdaptedClosedLoopRunner(cfg)
    runner.forecast_engine = CausalNwpPhysicsForecastEngine()
    sink = []
    runner.optimizer = CaptureOpt2(runner.optimizer, mode, sink)
    state = cae._camp.make_initial_state(t0)
    rep = runner.run_closed_loop(state, 24, WEATHER, rs, rw, rd, rts)
    return rep, sink


def work(oi):
    fr = FROZEN[oi]
    fs, t0 = fr["forecast_start"], fr["t0_timestamp"]
    res = {"origin_index": oi, "forecast_start": fs, "arms": {}}
    for mode, label in [("A", "frozen_B"), ("W", "critical_aware_wind"), ("S", "solar_only")]:
        try:
            rep, sink = run_arm2(mode, fs, t0)
            rows = cae.hourly_rows(rep, sink, mode)
            res["arms"][label] = {"summary": cae.summarize(rep, rows), "hourly": rows}
        except RuntimeError as e:
            res["arms"][label] = {"error": str(e)}
    fb = fr["arms"]["ARM_B_CANDIDATE"]
    a = res["arms"]["frozen_B"]["summary"]
    res["frozen_B_reproduced"] = (
        abs(a["fuel_l"] - fb["diesel_fuel_liters"]) < 1e-3
        and abs(a["total_unmet_wh"] - fb["unmet_critical_load_wh"]) < 1e-2
        and abs(a["curtail_wh"] - fb["curtailment_wh"]) < 1e-2
        and abs(a["total_served_wh"] - fb["served_load_wh"]) < 1e-2)
    (OUT / f"origin_{oi}.json").write_text(json.dumps(res))
    return res


if __name__ == "__main__":
    cae._init()     # identity checks for the governed/wind formulas (in-process)
    _check()        # identity and isolation checks for the solar-only formula
    print("pre-run checks passed", flush=True)
    with Pool(processes=4, initializer=cae._init) as pool:
        results = pool.map(work, ORIGINS, chunksize=1)
    (OUT / "all_results.json").write_text(json.dumps(results))
    print("DONE", flush=True)
