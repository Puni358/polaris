# Protected Component Register & Cryptographic Signatures

The following core source files represent the protected baseline of POLARIS EMS. They must remain untouched during any future synthetic integration work.

| Component Name | File Path | SHA-256 Hash | Protected Status |
| :--- | :--- | :--- | :--- |
| **Runner** | `system/runtime/runner.py` | `86aee0b51ba169458aa4cd8bbf678120b43d284144998d9c81e37f5fcaad5efc` | PROTECTED |
| **Option B HiGHS** | `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | PROTECTED |
| **MILP Base** | `system/optimization/implementations/milp.py` | `ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35` | PROTECTED |
| **Simulator** | `system/simulation/simulator.py` | `7217dc2b034480216e21e3494873189e575a15f3b2e71435d0844c4ca0a9a508` | PROTECTED |
| **ForecastBundle Schema** | `system/schemas/forecast_bundle.py` | `98c0347aff21e05694625b6a77a067e094e9407e1d037d429d8f086332ade428` | PROTECTED |
| **StationState Schema** | `system/schemas/station_state.py` | `f2cb385efdb2fdc95b681c765642660f1e0d06125c545b7464a8ac4a83e9185f` | PROTECTED |
| **DispatchPlan Schema** | `system/schemas/dispatch_plan.py` | `02ff5550a6fd5d67a559cd188f8e7eafaf847b0e6318d9614d30f5df340c517b` | PROTECTED |
| **ECD Core** | `system/control/ecd.py` | `d97c680ca8f4c1ceec57b28ecbe80ed3835ab06b7146cc64b4e197088635af23` | PROTECTED |
