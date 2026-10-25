# POLARIS 365-DAY DIESEL COMPARISON EXPERIMENT — PRE-FLIGHT DESIGN & AUDIT PACKAGE

## Executive Summary
This document establishes the authoritative pre-flight experiment design, forensic inspection, causality audit, baseline parity verification, and computational specification for the eventual full-calendar-year 2024 POLARIS microgrid closed-loop EMS diesel consumption comparison campaign.

### Key Pre-Flight Parameters
- **Experiment Purpose**: Scientifically quantify annual diesel fuel consumption of POLARIS closed-loop EMS versus an authoritative baseline control strategy over full-calendar-year 2024 under identical physical microgrid assets and identical environmental trajectories.
- **Time Domain**: Full-calendar-year 2024 / 8,784 hourly cycles (`2024-01-01T00:00:00Z` to `2024-12-31T23:00:00Z`).
- **Canonical Dataset**: H1.0 Canonical Hybrid Fixture (`POLARIS_HYBRID_FIXTURE_H1_0`, `h10_scenario_temp.json`, SHA256: `f94dbdf03e39b17b7461180db838a324b2cf0a57f1b302f1bd57db84d1bdf6c5`).
- **Protected Core Hashes**: Verified 100% intact across all 6 protected components. Zero modifications permitted or performed.
- **Pre-Flight Status**: `365D_PREFLIGHT = COMPLETE_AND_SEALED`
- **Execution Authorization**: `HUMAN_EXECUTION_AUTHORIZATION = NOT_GRANTED`
- **Campaign Execution Status**: `365D_CAMPAIGN = NOT_PERFORMED`
- **Source Code Changes**: `SOURCE_MODIFICATIONS = 0`

## Authoritative Audit Summary
1. **Time Domain**: Full-calendar-year 2024 / 8,784 hourly cycles ($366 \text{ days} \times 24 \text{ hours}$). UTC timezone.
2. **Fuel Scenarios**: Scenario Fuel-1 (Infinite Reservoir / Cumulative Accounting) is PRIMARY. Scenario Fuel-2 (Synthetic Finite Resupply) is SECONDARY SENSITIVITY (`PARAMETER BLOCKED`). Scenario Fuel-3 (Physical Station Logistics) is `NOT_ESTABLISHED`.
3. **Comparison Matrix**: 4-cell matrix evaluating Mode 1 (Same-Forecast Control Isolation) and Mode 2 (Complete System) independently.
4. **Gate-02 Compliance**: Gate-02 Option C enforced. Automatic Option D invocation on MILP infeasibility is strictly PROHIBITED.
5. **Stage 8.1 Model**: Unrecoverable model artifact acknowledged; silent substitution prohibited.
6. **Causality Audit**: Static audit identified zero future-truth access paths. Runtime firewall compliance to be measured during campaign.
