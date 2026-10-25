"""
POLARIS Local CLI Entrypoint
Provides offline command line interface for polaris forecast, optimize, simulate, evaluate, and run.
"""
import sys
import json
import argparse
from pathlib import Path

SYSTEM_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = SYSTEM_DIR.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from system.runtime.runner import PolarisLocalRunner

def main():
    parser = argparse.ArgumentParser(description="POLARIS Offline Energy Management System CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # polaris forecast
    forecast_parser = subparsers.add_parser("forecast", help="Generate 24h operational ForecastBundle")
    forecast_parser.add_argument("--scenario", type=str, default="demo_scenario.json", help="Scenario filename")
    forecast_parser.add_argument("--forecast-engine", type=str, choices=["baseline", "stage81_solar"], default="baseline", help="Forecast engine type")

    # polaris optimize
    optimize_parser = subparsers.add_parser("optimize", help="Generate 24h DispatchPlan given forecast")
    optimize_parser.add_argument("--scenario", type=str, default="demo_scenario.json", help="Scenario filename")
    optimize_parser.add_argument("--optimizer", type=str, choices=["milp", "rule_based"], default="milp", help="Optimizer type")
    optimize_parser.add_argument("--forecast-engine", type=str, choices=["baseline", "stage81_solar"], default="baseline", help="Forecast engine type")

    # polaris simulate
    simulate_parser = subparsers.add_parser("simulate", help="Run closed-loop MPC simulation")
    simulate_parser.add_argument("--steps", type=int, default=24, help="Number of timesteps")
    simulate_parser.add_argument("--optimizer", type=str, choices=["milp", "rule_based"], default="milp", help="Optimizer type")
    simulate_parser.add_argument("--forecast-engine", type=str, choices=["baseline", "stage81_solar"], default="baseline", help="Forecast engine type")

    # polaris evaluate
    evaluate_parser = subparsers.add_parser("evaluate", help="Compute Forecast and EMS metrics")

    # polaris run
    run_parser = subparsers.add_parser("run", help="Execute complete end-to-end local pipeline")
    run_parser.add_argument("--scenario", type=str, default="demo_scenario.json", help="Scenario filename")
    run_parser.add_argument("--steps", type=int, default=24, help="Number of timesteps")
    run_parser.add_argument("--optimizer", type=str, choices=["milp", "rule_based"], default="milp", help="Optimizer type")
    run_parser.add_argument("--forecast-engine", type=str, choices=["baseline", "stage81_solar"], default="baseline", help="Forecast engine type")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    opt_type = getattr(args, "optimizer", "milp")
    fe_type = getattr(args, "forecast_engine", "baseline")
    runner = PolarisLocalRunner(
        SYSTEM_DIR,
        scenario_filename=getattr(args, "scenario", "demo_scenario.json"),
        optimizer_type=opt_type,
        forecast_engine_type=fe_type
    )

    if args.command == "forecast":
        context = runner.data_provider.get_runtime_state(0)
        from system.schemas.station_state import StationState
        initial_state = StationState(
            timestamp=context["origin_timestamp"],
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=context["last_observed_solar_irradiance"],
            last_observed_demand=context["last_observed_demand"],
            last_observed_wind_generation=context["last_observed_wind_generation"]
        )
        bundle = runner.forecast_engine.predict(initial_state, context)
        out_path = SYSTEM_DIR / "artifacts" / "latest_forecast_bundle.json"
        with open(out_path, "w") as f:
            f.write(bundle.to_json())
        print(f"ForecastBundle successfully generated at {out_path}")

    elif args.command == "optimize":
        context = runner.data_provider.get_runtime_state(0)
        from system.schemas.station_state import StationState
        initial_state = StationState(
            timestamp=context["origin_timestamp"],
            battery_soc_pct=50.0,
            battery_energy_wh=100000.0,
            diesel_running=False,
            diesel_hours_running=0.0,
            last_observed_solar_irradiance=context["last_observed_solar_irradiance"],
            last_observed_demand=context["last_observed_demand"],
            last_observed_wind_generation=context["last_observed_wind_generation"]
        )
        bundle = runner.forecast_engine.predict(initial_state, context)
        plan = runner.optimizer.optimize(bundle, initial_state, runner.configs)
        out_path = SYSTEM_DIR / "artifacts" / "latest_dispatch_plan.json"
        with open(out_path, "w") as f:
            f.write(plan.to_json())
        print(f"DispatchPlan successfully generated at {out_path}")

    elif args.command == "simulate" or args.command == "run":
        report = runner.run_pipeline(steps_to_run=getattr(args, "steps", 24))
        print("\n==================================================")
        print("POLARIS LOCAL RUNNER EXECUTION REPORT")
        print("==================================================")
        print(f"Run ID:                 {report['run_id']}")
        print(f"Environment:            {report['environment']}")
        print(f"Network Status:         {report['network_connectivity']}")
        print(f"Timesteps Executed:     {report['timesteps_executed']}")
        print("\n--- FORECAST EVALUATION METRICS [DEMO / SMOKE-TEST RESULT] ---")
        print("(Synthetic scenario only — not operational performance validation.)")
        print(json.dumps(report["forecast_evaluation"], indent=2))
        print("\n--- ENERGY MANAGEMENT METRICS [DEMO / SMOKE-TEST RESULT] ---")
        print("(Synthetic scenario only — not operational performance validation.)")
        print(json.dumps(report["ems_evaluation"], indent=2))
        print("\nArtifacts saved to system/artifacts/")

    elif args.command == "evaluate":
        report_path = SYSTEM_DIR / "artifacts" / "run_report.json"
        if not report_path.exists():
            print("No previous run report found. Execute 'polaris run' first.")
            sys.exit(1)
        with open(report_path, "r") as f:
            report = json.load(f)
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
