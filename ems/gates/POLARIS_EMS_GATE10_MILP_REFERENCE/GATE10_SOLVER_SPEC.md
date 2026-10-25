# POLARIS EMS GATE-10 — MILP SOLVER SPECIFICATION

## 1. Executive Summary & Runtime Identity
This document specifies the solver architecture, variable structure, constraint formulation, and objective construction of the native HiGHS MILP reference implementation (`GAP19HighsNativeOptimizer`).

## 2. Solver Engine & Source File Identity
- **Optimizer Implementation**: `GAP19HighsNativeOptimizer` (`system/optimization/implementations/gap19_highs_native.py`)
- **Protected Option B Source SHA256**: `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737`
- **Native MILP Solver Engine**: Scipy HiGHS C++ Native Engine (`scipy.optimize.highs`)
- **Optimization Horizon**: 24 hourly steps ($H=24$)

## 3. Mathematical Optimization Problem Structure

### 3.1 Decision Variable Count (408 Variables Total)
For each hourly step $t \in [0, 23]$, 15 decision variables are defined ($24 \times 15 = 360$ variables):
- $P_{\text{solar\_used}}[t]$, $P_{\text{wind\_used}}[t]$, $P_{\text{solar\_curt}}[t]$, $P_{\text{wind\_curt}}[t]$
- $P_{\text{battery\_charge}}[t]$, $P_{\text{battery\_discharge}}[t]$, $E_{\text{battery\_next}}[t]$
- $P_{\text{diesel}}[t]$, $P_{\text{load\_served}}[t]$, $P_{\text{unmet\_total}}[t]$, $P_{\text{spill}}[t]$
- $u_{\text{chg}}[t]$ (binary), $u_{\text{dis}}[t]$ (binary), $u_{\text{diesel}}[t]$ (binary), $v_{\text{startup}}[t]$ (binary)

Additional slack variables across 24 steps:
- $s_{J2}[t]$: 24 unified reserve envelope slack variables
- $P_{\text{unmet\_crit}}[t]$: 24 critical demand unmet slack variables
- **Total Variable Count**: $360 + 24 + 24 = 408$ decision variables.

### 3.2 Constraint Count (312 Constraints Total)
- **Layer A (Physical & Balance Constraints)**: 24 steps $\times 11$ constraints = 264 constraints
- **Layer B (Critical Demand Balance Constraints)**: 24 constraints
- **Layer C (Stage 2 Unified Reserve Envelope Constraints)**: 24 constraints
- **Total Constraint Count**: $264 + 24 + 24 = 312$ constraints.

### 3.3 Multi-Objective Hierarchy ($J_1 \dots J_4$)
- $J_1$ (Fuel & Operational Cost): Base fuel, marginal fuel, startup costs, and battery degradation penalty.
- $J_2$ (Unified Reserve Envelope Target Penalty): Heavy penalty on reserve shortfall $s_{J2}[t]$.
- $J_3$ (Unmet Critical Demand Penalty): $1 \times 10^9 \cdot \sum P_{\text{unmet\_crit}}[t]$ (Hard Critical Load Policy).
- $J_4$ (Renewable Curtailment Penalty): Nominal penalty on renewable spill/curtailment.
