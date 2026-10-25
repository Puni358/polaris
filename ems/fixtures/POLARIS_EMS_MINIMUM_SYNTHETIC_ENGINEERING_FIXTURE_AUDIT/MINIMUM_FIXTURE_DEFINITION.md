# POLARIS EMS — MINIMUM SYNTHETIC FIXTURE DEFINITION

## 1. Executive Summary

This document specifies the master design contract for the **Minimum Synthetic Engineering Fixture** required to exercise the complete POLARIS software architecture.

---

## 2. Minimum Horizon & Temporal Parameters

| Parameter | Minimum Value | Justification |
| :--- | :--- | :--- |
| **Simulation Horizon** | $24.0\text{ Hours}$ ($H=24$) | Smallest deterministic window containing a full 24-hour diurnal cycle and MPC loop. |
| **Simulation Timestep** | $1.0\text{ Hour}$ ($\Delta t = 1.0\text{h}$) | Native timestep matching ForecastBundle and MILP optimizer resolution. |
| **MPC Horizon** | $24.0\text{ Hours}$ (24 timesteps) | Full lookahead window for LocalMILPEnergyOptimizer. |
| **ECD Baseline Horizon** | $6.0\text{ Hours}$ ($T_{\text{required\_baseline}}$) | Sealed baseline survivability window under `TREQ-001`. |
| **Control Loop Cycles** | 24 Closed-Loop Steps | Demonstrates receding-horizon state updates from $t=0$ to $t=23$. |

---

## 3. Minimum Sufficiency Justification

- **Why 24 Hours is Sufficient**: A 24-hour closed-loop simulation exercises 100% of pipeline control interfaces (Data Provider $\rightarrow$ StationState $\rightarrow$ ForecastEngine $\rightarrow$ ForecastBundle $\rightarrow$ ECD $\rightarrow$ Policy $\rightarrow$ EnergyOptimizer $\rightarrow$ DispatchPlan $\rightarrow$ DigitalTwin $\rightarrow$ State Update).
- **Why Multi-Day / Annual Replays are Omitted**: Multi-day scenarios (e.g. 72-hour or 8,784-hour annual replays) test long-term capacity adequacy, but add zero new code execution paths to the software architecture pipeline.

---

## 4. Status Classification

```yaml
MINIMUM_FIXTURE_DEFINITION_STATUS: COMPLETE
TIME_HORIZON: 24_HOURS
TIMESTEP: 1_HOUR
DEMONSTRATION_SCOPE: SOFTWARE_ARCHITECTURE_PIPELINE_ONLY
```
