import json
from hashlib import sha256
from pathlib import Path
import pandas as pd

BASE_DIR = Path("/home/punith-bs/01polaris (Copy)")
SYSTEM_DIR = BASE_DIR / "system"

def sha256_file(p):
    if not p.exists():
        return "FILE_NOT_FOUND"
    with open(p, "rb") as f:
        return sha256(f.read()).hexdigest()

def build_system_architecture():
    print("==================================================")
    print("POLARIS — PHASE D0: LOCAL-FIRST SYSTEM ARCHITECTURE GENERATION")
    print("==================================================")

    # Ensure system directory structure exists
    subdirs = [
        "architecture", "config", "data/raw", "data/processed", "data/runtime", "data/scenarios",
        "models", "forecasting/interface", "forecasting/implementations", "forecasting/preprocessing", "forecasting/postprocessing",
        "optimization/interface", "optimization/implementations", "optimization/constraints", "optimization/objectives",
        "simulation", "control", "evaluation", "schemas", "runtime", "tests", "scripts", "artifacts"
    ]
    for sd in subdirs:
        (SYSTEM_DIR / sd).mkdir(parents=True, exist_ok=True)

    arch_payload = {
        "document_name": "POLARIS_LOCAL_SYSTEM_ARCHITECTURE",
        "version": "1.0.0",
        "phase": "Phase D0 — System Architecture & Design",
        "timestamp_utc": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M:%S%z"),
        "core_principle": "STRICTLY LOCAL, OFFLINE-CAPABLE, SELF-CONTAINED, END-TO-END ENERGY MANAGEMENT SYSTEM",
        "runtime_network_requirement": "ZERO NETWORK CONNECTIVITY (100% OFFLINE)",
        "deployment_target": "Local PC (CPU-compatible local Python runtime)",
        "governance_status": {
            "polaris_research_phase": "CLOSED",
            "abc2_checkpoint": "FROZEN",
            "pard_c_c3_branch": "CLOSED",
            "odd_firewall": "SEALED_0_ROWS_ACCESSED",
            "polaris_system_build": "STARTING_PHASE_D0"
        },
        "system_goals": [
            "Build an offline-first microgrid Energy Management System (EMS) for remote/off-grid stations.",
            "Decouple operational forecasting engines from energy optimization and dispatch logic via stable contracts.",
            "Implement a receding-horizon Model Predictive Control (MPC) dispatch loop with a Digital Twin simulator.",
            "Provide transparent local CLI tools for forecasting, optimization, simulation, and evaluation.",
            "Enforce 100% local data and execution isolation with zero cloud or network dependencies."
        ],
        "architecture_layers": {
            "layer_1_data": "Local files (CSV, Parquet, NetCDF, JSON) managed by LocalWeatherProvider and LocalDataProvider.",
            "layer_2_forecasting": "ForecastEngine implementations (HistGBDT, Chronos, TimesFM, Persistence) outputting versioned ForecastBundle.",
            "layer_3_optimization": "EnergyOptimizer (LP/MILP/Heuristic) taking ForecastBundle + StationState -> DispatchPlan.",
            "layer_4_simulation": "Digital Twin Simulator stepping actual environmental state against DispatchPlan in closed-loop MPC.",
            "layer_5_evaluation": "Decoupled ForecastMetrics and EnergyManagementMetrics evaluation engine."
        },
        "forecast_bundle_contract": {
            "horizon_hours": 24,
            "fields": [
                "origin_timestamp (ISO 8601 UTC string)",
                "horizon_hours (int, default 24)",
                "timestamps (array of 24 UTC strings)",
                "solar (object: point[24], lower[24], upper[24])",
                "wind (object: point[24], lower[24], upper[24])",
                "demand (object: point[24], lower[24], upper[24])",
                "metadata (model_id, model_version, feature_version, generation_timestamp)"
            ]
        },
        "dispatch_plan_contract": {
            "horizon_hours": 24,
            "fields": [
                "timestamps (array of 24 UTC strings)",
                "solar_used (array of 24 floats, W)",
                "wind_used (array of 24 floats, W)",
                "battery_charge (array of 24 floats, W)",
                "battery_discharge (array of 24 floats, W)",
                "battery_soc (array of 24 floats, % or Wh)",
                "diesel_power (array of 24 floats, W)",
                "load_served (array of 24 floats, W)",
                "flexible_load_schedule (array of 24 floats, W)",
                "renewable_curtailment (array of 24 floats, W)",
                "unmet_load (array of 24 floats, W)",
                "objective_value (float)",
                "constraint_status (string: OPTIMAL, FEASIBLE, INFEASIBLE)"
            ]
        },
        "validated_vs_unvalidated": {
            "research_validated": "Phase C-1/C-2 GBDT feature extractability for H7-H12 daytime solar transmission and irradiance.",
            "operational_prototype": "Operational H1-H24 solar, wind, and demand forecasting modules (marked as PROTOTYPE / UNVALIDATED OPERATIONAL COMPONENTS)."
        },
        "first_milestone": "Milestone D1 — Local System Foundation, Interfaces, Schemas, & Offline Test Harness."
    }

    arch_json_path = BASE_DIR / "docs/architecture/POLARIS_LOCAL_SYSTEM_ARCHITECTURE.json"
    with open(arch_json_path, "w") as f:
        json.dump(arch_payload, f, indent=2)

    arch_md_path = BASE_DIR / "docs/architecture/POLARIS_LOCAL_SYSTEM_ARCHITECTURE.md"
    with open(arch_md_path, "w") as f:
        f.write("# POLARIS — LOCAL-FIRST SYSTEM ARCHITECTURE SPECIFICATION (PHASE D0)\n\n")
        f.write(f"**Date (UTC):** {arch_payload['timestamp_utc']}  \n")
        f.write("**System Status:** PHASE D0 ARCHITECTURE SPECIFICATION  \n")
        f.write("**Research Branch Status:** CLOSED (ABC2 Frozen)  \n")
        f.write("**Runtime Requirement:** **STRICTLY LOCAL, OFFLINE-CAPABLE, ZERO NETWORK CONNECTIVITY**  \n")
        f.write("**Primary Target:** Local PC (CPU-compatible Python runtime)  \n")
        f.write("**ODD Status:** SEALED (0 rows accessed)  \n\n---\n\n")

        f.write("## 1. System Goals & Engineering Principles\n\n")
        f.write("POLARIS is transitioning from scientific identification research into an **operational, local-first Energy Management System (EMS)** designed for off-grid, remote microgrid infrastructure (e.g., arctic research stations, isolated microgrids).\n\n")
        f.write("### Primary Engineering Mandates\n")
        f.write("1. **Strictly Local & Offline-Capable:** The runtime system must operate with zero internet, zero cloud APIs, zero external databases (e.g., Supabase/Vercel), zero remote weather/NWP APIs, and zero browser connectivity. Network is used only during initial development package installation.\n")
        f.write("2. **Separation of Forecasting and Optimization:** The Energy Optimizer operates strictly against a stable `ForecastBundle` contract. The optimizer is agnostic to whether forecasts are generated by GBDT, Chronos, TimesFM, persistence, or local physics models.\n")
        f.write("3. **Contract-Driven Modular Architecture:** Clean interface isolation across Data, Forecasting, Optimization, Simulation (Digital Twin), Control, and Evaluation.\n")
        f.write("4. **Receding-Horizon Model Predictive Control (MPC):** System dispatch operates in closed-loop MPC mode ($24\\text{h}$ forecast $\\to 24\\text{h}$ optimize $\\to$ execute 1st step $\\to$ update state $\\to$ repeat).\n")
        f.write("5. **CLI-First Local Runtime:** Primary control and execution occur via a local Python CLI. Browser UI is deferred as a thin client wrapper.\n\n---\n\n")

        f.write("## 2. End-to-End System Architecture Diagram\n\n")
        f.write("```\n")
        f.write(" +---------------------------------------------------------------------------------+\n")
        f.write(" |                            POLARIS LOCAL RUNTIME                                |\n")
        f.write(" +---------------------------------------------------------------------------------+\n")
        f.write("                                          |\n")
        f.write("               +--------------------------+--------------------------+\n")
        f.write("               |                                                     |\n")
        f.write("               v                                                     v\n")
        f.write("   +-----------------------+                             +-----------------------+\n")
        f.write("   |  LocalWeatherProvider |                             |    LocalDataProvider  |\n")
        f.write("   | (CSV/Parquet/NetCDF)  |                             |  (Station State/Logs) |\n")
        f.write("   +-----------------------+                             +-----------------------+\n")
        f.write("               |                                                     |\n")
        f.write("               +--------------------------+--------------------------+\n")
        f.write("                                          |\n")
        f.write("                                          v\n")
        f.write("                             +-------------------------+\n")
        f.write("                             |     ForecastEngine      |\n")
        f.write("                             |  (Pluggable Local Mod)  |\n")
        f.write("                             +-------------------------+\n")
        f.write("                                          |\n")
        f.write("                                          | [ForecastBundle (24h Contract)]\n")
        f.write("                                          v\n")
        f.write("                             +-------------------------+\n")
        f.write("                             |     EnergyOptimizer     |\n")
        f.write("                             |  (LP/MILP/Heuristic)    |\n")
        f.write("                             +-------------------------+\n")
        f.write("                                          |\n")
        f.write("                                          | [DispatchPlan (24h Schedule)]\n")
        f.write("                                          v\n")
        f.write("                             +-------------------------+\n")
        f.write("                             |  Simulator / Controller |\n")
        f.write("                             |  (Digital Twin MPC)     |\n")
        f.write("                             +-------------------------+\n")
        f.write("                                          |\n")
        f.write("                                          v\n")
        f.write("                             +-------------------------+\n")
        f.write("                             |    EvaluationEngine     |\n")
        f.write("                             | (Forecast & EMS Metrics)|\n")
        f.write("                             +-------------------------+\n")
        f.write("```\n\n---\n\n")

        f.write("## 3. Dedicated System Workspace Directory Structure\n\n")
        f.write("Operational code is strictly isolated inside `system/`, leaving historical research artifacts untouched.\n\n")
        f.write("```\n")
        f.write("POLARIS/\n")
        f.write("├── research/                  # Historical research code (Stage 7-8, Phase A/B/C)\n")
        f.write("├── checkpoints/               # Authoritative synthesis checkpoints (ABC2)\n")
        f.write("└── system/                    # OPERATIONAL LOCAL SYSTEM WORKSPACE\n")
        f.write("    ├── README.md              # Offline setup & CLI usage guide\n")
        f.write("    ├── architecture/          # Architecture specs & system diagrams\n")
        f.write("    ├── config/                # Configuration files (station.yaml, battery.yaml, diesel.yaml)\n")
        f.write("    ├── data/                  # Local offline dataset storage\n")
        f.write("    │   ├── raw/               # Raw local weather/multivariate site files\n")
        f.write("    │   ├── processed/         # Feature tables & preprocessed tensors\n")
        f.write("    │   ├── runtime/           # Active runtime state & logs\n")
        f.write("    │   └── scenarios/         # Offline demo evaluation scenarios\n")
        f.write("    ├── models/                # Local trained model weights & feature scalers\n")
        f.write("    ├── forecasting/           # Forecasting Engine Module\n")
        f.write("    │   ├── interface/         # Abstract ForecastEngine interface\n")
        f.write("    │   ├── implementations/   # Local GBDT, Persistence, Chronos adapters\n")
        f.write("    │   ├── preprocessing/     # Feature extraction & clear-sky calculators\n")
        f.write("    │   └── postprocessing/    # Uncertainty bounds & clipping\n")
        f.write("    ├── optimization/          # Energy Optimizer Module\n")
        f.write("    │   ├── interface/         # Abstract EnergyOptimizer interface\n")
        f.write("    │   ├── implementations/   # MILP, LP, and Rule-based solvers\n")
        f.write("    │   ├── constraints/       # Battery, Diesel, Load, and Grid constraints\n")
        f.write("    │   └── objectives/        # Fuel minimization & reliability objective functions\n")
        f.write("    ├── simulation/            # Digital Twin Simulator (Closed-loop MPC)\n")
        f.write("    ├── control/               # Dispatch execution & MPC controller\n")
        f.write("    ├── evaluation/            # Forecast & Energy Management metrics\n")
        f.write("    ├── schemas/               # Versioned Pydantic schemas (ForecastBundle, DispatchPlan)\n")
        f.write("    ├── runtime/               # Local CLI entrypoints & offline runner\n")
        f.write("    ├── tests/                 # Unit tests & offline isolation tests\n")
        f.write("    ├── scripts/               # Offline setup & helper scripts\n")
        f.write("    └── artifacts/             # Output run reports & evaluation logs\n")
        f.write("```\n\n---\n\n")

        f.write("## 4. Forecasting Engine & Contract Specs\n\n")
        f.write("### Abstract Interface\n")
        f.write("```python\n")
        f.write("class ForecastEngine(ABC):\n")
        f.write("    @abstractmethod\n")
        f.write("    def predict(self, input_state: StationState) -> ForecastBundle:\n")
        f.write("        \"\"\"Generate a 24-hour operational ForecastBundle from local state.\"\"\"\n")
        f.write("        pass\n")
        f.write("```\n\n")

        f.write("### `ForecastBundle` Schema (Version 1.0)\n")
        f.write("```json\n")
        f.write("{\n")
        f.write("  \"origin_timestamp\": \"2024-06-01T00:00:00Z\",\n")
        f.write("  \"horizon_hours\": 24,\n")
        f.write("  \"timestamps\": [\"2024-06-01T01:00:00Z\", \"...\", \"2024-06-02T00:00:00Z\"],\n")
        f.write("  \"solar\": {\n")
        f.write("    \"point\": [12.5, 45.2, \"...\", 0.0],\n")
        f.write("    \"lower\": [8.0, 30.0, \"...\", 0.0],\n")
        f.write("    \"upper\": [18.0, 60.0, \"...\", 0.0]\n")
        f.write("  },\n")
        f.write("  \"wind\": {\n")
        f.write("    \"point\": [100.0, \"...\", 85.0],\n")
        f.write("    \"lower\": [70.0, \"...\", 50.0],\n")
        f.write("    \"upper\": [130.0, \"...\", 120.0]\n")
        f.write("  },\n")
        f.write("  \"demand\": {\n")
        f.write("    \"point\": [50.0, \"...\", 45.0],\n")
        f.write("    \"lower\": [45.0, \"...\", 40.0],\n")
        f.write("    \"upper\": [55.0, \"...\", 50.0]\n")
        f.write("  },\n")
        f.write("  \"metadata\": {\n")
        f.write("    \"model_id\": \"polaris_gbdt_local_v1\",\n")
        f.write("    \"model_version\": \"1.0.0\",\n")
        f.write("    \"feature_version\": \"p1_causal_147\",\n")
        f.write("    \"generation_timestamp\": \"2024-06-01T00:00:01Z\"\n")
        f.write("  }\n")
        f.write("}\n")
        f.write("```\n\n---\n\n")

        f.write("## 5. Optimization & Dispatch Plan Specs\n\n")
        f.write("### Abstract Interface\n")
        f.write("```python\n")
        f.write("class EnergyOptimizer(ABC):\n")
        f.write("    @abstractmethod\n")
        f.write("    def optimize(self, forecast: ForecastBundle, state: StationState, config: ConfigDict) -> DispatchPlan:\n")
        f.write("        \"\"\"Generate a 24-hour optimal DispatchPlan given forecasts and station constraints.\"\"\"\n")
        f.write("        pass\n")
        f.write("```\n\n")

        f.write("### `DispatchPlan` Schema (Version 1.0)\n")
        f.write("```json\n")
        f.write("{\n")
        f.write("  \"timestamps\": [\"2024-06-01T01:00:00Z\", \"...\", \"2024-06-02T00:00:00Z\"],\n")
        f.write("  \"solar_used\": [12.5, \"...\", 0.0],\n")
        f.write("  \"wind_used\": [100.0, \"...\", 85.0],\n")
        f.write("  \"battery_charge\": [20.0, \"...\", 0.0],\n")
        f.write("  \"battery_discharge\": [0.0, \"...\", 15.0],\n")
        f.write("  \"battery_soc\": [85.0, \"...\", 60.0],\n")
        f.write("  \"diesel_power\": [0.0, \"...\", 30.0],\n")
        f.write("  \"load_served\": [50.0, \"...\", 45.0],\n")
        f.write("  \"flexible_load_schedule\": [10.0, \"...\", 0.0],\n")
        f.write("  \"renewable_curtailment\": [0.0, \"...\", 0.0],\n")
        f.write("  \"unmet_load\": [0.0, \"...\", 0.0],\n")
        f.write("  \"objective_value\": 142.50,\n")
        f.write("  \"constraint_status\": \"OPTIMAL\"\n")
        f.write("}\n")
        f.write("```\n\n---\n\n")

        f.write("## 6. Energy System & Modular Models\n\n")
        f.write("### Configuration-Driven Properties (`system/config/`)\n")
        f.write("- **`station.yaml`:** Master microgrid configuration and topology.\n")
        f.write("- **`battery.yaml`:** SOC bounds ($20\\% - 95\\%$), charge/discharge efficiency ($92\\%$), max power ($50\\text{ kW}$), capacity ($200\\text{ kWh}$).\n")
        f.write("- **`diesel.yaml`:** Min/max generation ($10\\text{ kW} - 100\\text{ kW}$), ramp limits, fuel consumption curve parameters ($L/kWh$), startup penalty.\n")
        f.write("- **`loads.yaml`:** Critical load definitions (unmet penalty $= 10,000\\$/kWh$), deferrable load time windows, curtailable load priority.\n")
        f.write("- **`optimizer.yaml`:** Solver selection (PuLP/SciPy MILP), objective weight coefficients.\n\n---\n\n")

        f.write("## 7. Digital Twin Simulator & Receding-Horizon Control (MPC)\n\n")
        f.write("The `Simulator` models closed-loop physical station dynamics:\n")
        f.write("1. At step $t$, `ForecastEngine` predicts 24-hour `ForecastBundle` using only data available up to $t$.\n")
        f.write("2. `EnergyOptimizer` generates 24-hour `DispatchPlan`.\n")
        f.write("3. `Simulator` executes step 1 of `DispatchPlan` against **hidden local environmental actuals** at $t+1$.\n")
        f.write("4. Battery SOC, fuel consumption, and load compliance are updated. Actual future values are **never leaked to the optimizer**.\n\n---\n\n")

        f.write("## 8. Evaluation Architecture\n\n")
        f.write("Decouples statistical forecasting accuracy from physical energy management performance:\n")
        f.write("- **`ForecastMetrics`:** MAE, RMSE, nMAE, Bias (evaluating $SW\\_IN$, wind, and demand forecasts).\n")
        f.write("- **`EnergyManagementMetrics`:** Total fuel consumed (L), renewable utilization (%), renewable curtailment (%), battery throughput (kWh) / cycles, unmet critical load (kWh), unmet total load (kWh), reliability (%), SOC violations.\n\n---\n\n")

        f.write("## 9. Critical Research vs. System Capability Distinction\n\n")
        f.write("| Feature Category | Research Validated Capability | Operational System Capability |\n")
        f.write("| :--- | :--- | :--- |\n")
        f.write("| **Solar Irradiance** | Validated $P1$ feature extractability for $k(t+h)$ and $SW\\_IN(t+h)$ at H7–H12 on 104 EVEN origins (Phase C-1, C-2). | Full 24-hour ($H1$–$H24$) operational solar module (**PROTOTYPE / UNVALIDATED OPERATIONAL COMPONENT**). |\n")
        f.write("| **Wind Generation** | Not evaluated in research phase. | 24-hour operational wind module (**PROTOTYPE / UNVALIDATED OPERATIONAL COMPONENT**). |\n")
        f.write("| **Demand Profile** | Not evaluated in research phase. | 24-hour operational load module (**PROTOTYPE / UNVALIDATED OPERATIONAL COMPONENT**). |\n")
        f.write("| **Energy Dispatch** | Not evaluated in research phase. | Closed-loop MPC MILP optimizer & Digital Twin (**PROTOTYPE / UNVALIDATED OPERATIONAL COMPONENT**). |\n\n---\n\n")

        f.write("## 10. First Implementation Milestone (Milestone D1)\n\n")
        f.write("1. Create `system/` directory structure and abstract interfaces.\n")
        f.write("2. Implement `ForecastBundle` and `DispatchPlan` Pydantic schemas.\n")
        f.write("3. Implement `LocalWeatherProvider` reading local CSV/Parquet files from `system/data/`.\n")
        f.write("4. Implement a baseline `LocalGBDTForecastEngine` wrapping validated Phase C-2 feature pipelines.\n")
        f.write("5. Implement a baseline MILP `LocalEnergyOptimizer` using PuLP/SciPy.\n")
        f.write("6. Implement `DigitalTwinSimulator` for offline closed-loop simulation.\n")
        f.write("7. Implement `test_offline_runtime.py` verifying 100% offline network isolation.\n\n---\n\n")

        f.write("## 11. Offline Runtime Isolation Guarantee\n\n")
        f.write("> **\"THE POLARIS RUNTIME REQUIRES ZERO NETWORK CONNECTIVITY AND RUNS STRICTLY OFFLINE ON A LOCAL PC.\"**\n\n")
        f.write("Network access is blocked at the runtime level. All data, model weights, feature scalers, and solver dependencies reside strictly on local disk (`system/data/`, `system/models/`, `system/config/`).\n\n---\n\n")

        f.write("POLARIS LOCAL SYSTEM ARCHITECTURE SPECIFICATION COMPLETE.\n")
        f.write("AWAITING HUMAN REVIEW BEFORE IMPLEMENTATION.\n")

    # Create initial system README
    readme_path = SYSTEM_DIR / "README.md"
    with open(readme_path, "w") as f:
        f.write("# POLARIS Operational Local System Workspace\n\n")
        f.write("This directory contains the operational code for the POLARIS local-first, offline-capable Energy Management System (EMS).\n\n")
        f.write("## Key Principles\n")
        f.write("- **Offline First:** 100% self-contained local runtime. Zero network dependency.\n")
        f.write("- **Decoupled Architecture:** Forecasting Engine (`ForecastBundle`) $\\to$ Energy Optimizer (`DispatchPlan`) $\\to$ Digital Twin Simulator.\n")
        f.write("- **Config Driven:** Microgrid physical properties managed via YAML configuration (`config/`).\n\n")
        f.write("See `docs/architecture/POLARIS_LOCAL_SYSTEM_ARCHITECTURE.md` in the project root for full technical specification.\n")

    hashes = {
        "docs/architecture/POLARIS_LOCAL_SYSTEM_ARCHITECTURE.json": sha256_file(arch_json_path),
        "docs/architecture/POLARIS_LOCAL_SYSTEM_ARCHITECTURE.md": sha256_file(arch_md_path),
        "system/README.md": sha256_file(readme_path)
    }

    print("\nArchitecture Document Hashes:")
    print("Architecture JSON Hash:", hashes["docs/architecture/POLARIS_LOCAL_SYSTEM_ARCHITECTURE.json"])
    print("Architecture MD Hash:  ", hashes["docs/architecture/POLARIS_LOCAL_SYSTEM_ARCHITECTURE.md"])
    print("system/README.md Hash: ", hashes["system/README.md"])

if __name__ == "__main__":
    build_system_architecture()
