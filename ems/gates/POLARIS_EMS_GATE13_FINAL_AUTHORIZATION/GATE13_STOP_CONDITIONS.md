# POLARIS EMS GATE-13 — PRE-FLIGHT STOP CONDITIONS

## Executive Statement
The following mandatory stop conditions MUST immediately halt execution if detected prior to or during final integrated execution.

## Mandatory Stop Conditions

1. **Source Hash Mismatch**: Any change in SHA256 checksums of protected core system files (`gap19_highs_native.py`, `option_d.py`, `ecd.py`, `router.py`, `simulator.py`, `runner.py`).
2. **Missing Explicit Human Authorization**: `HUMAN_EXECUTION_AUTHORIZATION != GRANTED`.
3. **UNKNOWN_INVALID State Evaluation**: `ECD` returning `UNKNOWN_INVALID` operational mode.
4. **MILP Solver Infeasibility**: Solver returning `HighsModelStatus.kInfeasible` or `constraint_status.startswith("OPTIMIZATION_INFEASIBLE")`.
5. **Physical Boundary Violation**: Physical SOC violating bounds ($SOC < 20.0\%$ or $SOC > 95.0\%$) or energy balance error $\ne 0.0 \text{ W}$.
6. **Truth Firewall Breach**: Any detection of future actual ground truth fields in controller input payloads (`ForecastBundle`).
7. **Unearned Fuel Increase**: Detection of non-monotonic fuel increase without an explicit replenishment event.
8. **Simultaneous Battery Charge & Discharge**: Detection of simultaneous charge and discharge power ($p_{\text{chg}} > 0$ and $p_{\text{dis}} > 0$).
