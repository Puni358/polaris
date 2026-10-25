# PRE-GENERATION BLOCKER REGISTER
## PRE-GENERATION GATE BLOCKERS & RESOLUTION CRITERIA

### 1. GATE DECISION SUMMARY
- **Preflight Review Gate Status**: `FIXTURE_GENERATION_READY = NO`
- **Reason**: Three specific parameter discrepancies and specification ambiguities must be formally acknowledged and frozen prior to fixture generation.

### 2. DETAILED BLOCKER REGISTER

#### BLOCKER 1: BATTERY MINIMUM SOC FLOOR DISCREPANCY
- **Description**: The proposed fixture specified a $10\%$ SOC minimum ($20\text{ kWh}$). In contrast, `system/config/battery.yaml` and the MILP optimization formulation enforce `soc_min = 0.20` ($20\% / 40\text{ kWh}$) as the hardware cell protection floor (`SOC_min_technical`).
- **Impact**: Generating fixture trajectories starting at $10\%$ SOC or assuming a $10\%$ floor will cause immediate solver constraint violations or infeasibility in `milp.py`.
- **Required Pre-Generation Action**: Freeze the fixture minimum SOC floor to **$20\%$ ($40\text{ kWh}$)** to align with `battery.yaml`.

#### BLOCKER 2: DIESEL FUEL CONSUMPTION MODEL AMBIGUITY
- **Description**: The proposed fixture specified a flat $12.5\text{ L/h}$ fuel rate. Forensic audit confirmed $12.5\text{ L/h}$ is the specific consumption of the prototype linear fuel model $F(t) = 5.0 + 0.25 \times P_{\text{gen}}(t)\text{ L/h}$ at $30\text{ kW}$ output.
- **Impact**: Using a flat $12.5\text{ L/h}$ across all generator operating points distorts fuel accounting by $+66\%$ at minimum load ($10\text{ kW}$) and $-37.5\%$ at maximum load ($60\text{ kW}$).
- **Required Pre-Generation Action**: Mandate that the synthetic fixture generator implements the linear model $F(P_{\text{gen}}) = 5.0 \cdot u_{\text{gen}} + 0.25 \cdot P_{\text{gen}}\text{ L/h}$ rather than a static scalar.

#### BLOCKER 3: CRITICAL LOAD PRIORITY HIERARCHY CLARIFICATION
- **Description**: The 3-component critical load vector (Heating 15 kW, Water 10 kW, Comms 5 kW) must NOT be interpreted as establishing a priority hierarchy ($\text{Heating} > \text{Water} > \text{Comms}$).
- **Impact**: Unsanctioned priority ordering violates sealed Option D governance, which mandates proportional allocation across all protected critical loads during deficits.
- **Required Pre-Generation Action**: Formally record that the 3-component vector exists strictly to test proportional allocation ($15:10:5$ baseline ratio), and that all three subsystems share equal statutory priority under Option D.

### 3. CLEARANCE CRITERIA FOR FUTURE FIXTURE GENERATION
When human governance accepts the preflight resolutions (Blocker 1 $\to$ 20% SOC floor, Blocker 2 $\to$ Linear fuel model, Blocker 3 $\to$ Proportional allocation without priority ranking), `FIXTURE_GENERATION_READY` may be updated to `YES` in a subsequent generation task.
