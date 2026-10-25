# POLARIS — FORMAL REAL ENERGY-DEMAND DATA ACCESS PACKAGE
## Smart India Hackathon (SIH) Project

---

## 1. Project Decision & Purpose

The POLARIS project team has formally selected:

```text
PATH A — ONE BOUNDED FORMAL RESTRICTED-DATA ACCESS ATTEMPT
```

### Purpose
This document constitutes the final formal access and readiness package for requesting historical, measured, station-level electrical-demand data for POLARIS as a **Smart India Hackathon (SIH)** innovation project.

This package is **PREPARED ONLY**. It establishes the technical dataset specifications, draft access request, target custodian inventory, data-suitability evaluation framework, and bounded stopping condition for human review and submission. 

**This task does NOT constitute data acquisition, external contact, automatic submission, software implementation, or experimental execution.**

---

## 2. Authoritative Project State

The authoritative POLARIS system and scientific states remain strictly enforced and locked:

- **Stage8.1 Solar Irradiance Research**: `FROZEN`
- **Stage8.1 Champion Model**: `FROZEN / NOT CONNECTED / NOT AUTHORIZED`
- **D5 Sensitivity Study**: `CLOSED / NOT REOPENED / NOT RERUN`
- **POLARIS System Integration**: `VALIDATED`
- **Real Energy-Demand Data Status**: `REAL DATA ACCESS RESTRICTED`
- **Synthetic Test Fixtures**: `PRESERVED` (`demo_scenario.json`, `synthetic_168h_endurance_scenario.json`, etc.)
- **Real-Data Adapter**: `NOT IMPLEMENTED / NOT AUTHORIZED`
- **Experiments / Architecture Changes**: `NOT AUTHORIZED`

---

## 3. SIH Project Context & Positioning

POLARIS is explicitly positioned as:

> **"A Smart India Hackathon (SIH) project developing an AI-driven predictive energy-management system for polar research stations."**

### Positioning Rules
1. POLARIS is **NOT** described as an academic research programme, university research initiative, institutional research study, or funded scientific research grant unless separately supplied.
2. No institutional affiliations, team names, faculty leads, student credentials, funding sources, or contact details are fabricated. Explicit placeholders are used throughout the package.
3. The request seeks permission/access for historical measured demand data solely to support SIH engineering development, optimization evaluation, and system demonstration under custodian-approved terms.

---

## 4. Primary Data Requirement

The **PRIMARY** requested dataset is:

```text
MEASURED STATION-LEVEL ELECTRICAL DEMAND / LOAD TIME SERIES
```

### Specification
1. **Station / Site Identifier**: Name and geographic location of the polar research station or candidate remote polar microgrid.
2. **Measured Electrical Demand / Load**: Active power demand ($\text{kW}$ or $\text{W}$) or energy consumption per interval ($\text{kWh}$).
3. **Timestamp**: ISO 8601 or unambiguous UTC date-time for each observation.
4. **Temporal Resolution / Interval**: Preferred sampling interval $\le 1\text{ hour}$ ($15\text{ min}$, $30\text{ min}$, or $60\text{ min}$). If multiple resolutions exist, request the highest-resolution historical series reasonably available. (Hourly interval is preferred, but not falsely represented as mandatory if another high-resolution series exists).
5. **Physical Units**: Explicit unit designation.
6. **Temporal Coverage**: The longest continuous historical logging period available.
7. **Quality / Missing-Data Information**: Quality flags, sensor outage markers, or missing-data indicators, if available.
8. **Data Provenance**: Metering instrumentation description or measurement method, if available.
9. **Terms of Use**: Terms governing project/hackathon use, analysis, reporting, publication, citation, redistribution, and storage.

---

## 5. Optional Supporting Variables

If the custodian can provide auxiliary microgrid measurements without complicating or delaying the primary electrical-demand request, the following variables may be requested as **OPTIONAL / IF AVAILABLE**:

- Solar PV power generation ($\text{kW}$ / $\text{W}$)
- Wind turbine power generation ($\text{kW}$ / $\text{W}$)
- Battery system State of Charge ($\text{SOC} \, [\%]$ / $\text{kWh}$)
- Battery power / stored-energy measurements ($\text{kW}$)
- Diesel generator operating status (on/off)
- Diesel generator electrical output ($\text{kW}$)
- Diesel generator operating hours / fuel rate
- Station ambient weather observations (ambient temperature, wind speed, solar irradiance $SW_{in}$)

**Boundary Rule**: Access to these auxiliary variables is strictly **OPTIONAL**. Their absence does **NOT** invalidate or compromise the primary electrical-demand data request.

---

## 6. Four Target Data Custodians

The access package targets the four potential custodians previously identified in project evidence. No new custodian reconnaissance or web search was conducted.

### Target 1: Australian Antarctic Division (AAD)
- **Scope / Stations**: Casey, Davis, Mawson, Macquarie Island.
- **Context**: Project evidence identified historical station energy usage information, but publicly available catalog data was aggregated monthly (too coarse for sub-hourly/hourly MPC).
- **Request Focus**: Inquire whether AAD can grant access to higher-resolution ($\le 1\text{-hour}$) historical measured station electrical-demand/load time series, if recorded and releasable for SIH project validation.
- **Contact Channel**: `aadcwebqueries@aad.gov.au`
- **Delivery Audit Status**: `DELIVERY FAILED — EXTERNAL SENDER RESTRICTION (550 5.7.133)`
- **AADC Data-Access Decision**: `NOT RECEIVED / NOT REVIEWED`
- **Scientific Interpretation**: `NONE` (Bounced by recipient distribution group restrictions before substantive review).
- **Retry Rule**: `NOT AUTHORIZED / DO NOT REPEAT` (Do not resend to restricted group).

### Target 2: South African National Antarctic Programme (SANAP) / SANAE IV Custodian
- **Scope / Station**: SANAE IV Station, Dronning Maud Land, Antarctica.
- **Context**: Literature describes 1-hour station/microgrid electrical load logging; raw high-resolution time series was not publicly obtained.
- **Request Focus**: Request historical measured station electrical-demand time series under SANAP custodian access rules.
- **Contact Channel**: `antarcticlegacy@sun.ac.za`
- **Status**: `REQUEST DISPATCHED — AWAITING RESPONSE`

### Target 3: International Polar Foundation (IPF) / Princess Elisabeth Antarctica Custodian
- **Scope / Station**: Princess Elisabeth Antarctica Station.
- **Context**: Micro-smart-grid operational profiles described in literature; raw high-resolution measured demand telemetry was not publicly obtained.
- **Request Focus**: Request historical measured station electrical-demand time series subject to IPF data governance.
- **Contact Channel**: `info@polarfoundation.org`
- **Status**: `REQUEST DISPATCHED — AWAITING RESPONSE`

### Target 4: Alaska Center for Energy and Power (ACEP) / University of Alaska Fairbanks
- **Scope / Sites**: Remote Arctic research / microgrid sites (e.g., Kotzebue, Cordova, Wales, St. Mary's).
- **Context**: Arctic microgrid load logging documented in literature; raw high-resolution time-series access was not established during initial inspection.
- **Request Focus**: Request historical measured electrical-demand/load time series for a suitable Arctic research/microgrid site, if available and releasable for an SIH project.
- **Contact Channel**: `ACEP.info@alaska.edu`
- **Status**: `REQUEST DISPATCHED — AWAITING RESPONSE`

---

## 7. Formal Access Request Draft

```text
SUBJECT: Data Access Request — Measured Station Electrical-Demand Data for POLARIS Smart India Hackathon Project

TO: [TARGET CUSTODIAN]

REQUESTER CONTEXT:
We are writing on behalf of University of Visvesvaraya College of Engineering + Team_Side_Quest, participating in the Smart India Hackathon (SIH). Our project, POLARIS, is an AI-driven predictive energy-management system designed for polar research stations. The system forecasts energy demand and renewable generation using historical, weather, and station data, and uses these forecasts to optimize renewable generation, battery storage, diesel generation, and flexible loads while maintaining reliable energy service under polar operating constraints.

PURPOSE OF DATA REQUEST:
To evaluate and demonstrate our predictive energy optimization algorithms realistically, we seek access to historical, measured station-level electrical-demand (load) data. Specifically, the data would be used to:
1. Provide a realistic electrical demand baseline for offline Model Predictive Control (MPC) dispatch simulations;
2. Evaluate predictive demand forecasting and load-following EMS performance under empirical polar station load dynamics;
3. Support SIH project reporting, system demonstration, and technical documentation strictly in accordance with your data use and attribution guidelines.

PRIMARY DATA REQUEST:
- Measured station-level electrical demand / load time series;
- Preferred temporal resolution: Hourly or finer (e.g., 15-minute, 30-minute, or 1-hour intervals);
- Unambiguous timestamps (preferably UTC / ISO 8601);
- Explicit physical units (e.g., kW, W, or kWh/interval);
- Longest continuous historical period available;
- Basic measurement quality flags or missing-data indicators, if available.

OPTIONAL SUPPORTING VARIABLES (IF CONVENIENT):
If readily available without complicating the request, auxiliary data such as solar generation, wind generation, battery SOC, diesel output, or local weather observations would be welcomed as optional enrichment. However, their absence will not invalidate our primary demand request.

DATA USE & GOVERNANCE INQUIRIES:
We request your guidance regarding:
- Whether historical demand data access is available for an SIH innovation project;
- Required application procedures, Non-Disclosure Agreements (NDAs), or Data Sharing Agreements (DSAs);
- Required requester credentials, student/mentor verification, or institutional approvals;
- Permitted use conditions, attribution requirements, and redistribution restrictions;
- Permission to present derived optimization metrics and charts in SIH evaluation reports and presentations.

SCOPE LIMITATIONS:
This request is strictly for historical measured data for offline algorithm evaluation. We do NOT seek physical station access, live operational control, or real-time grid connectivity.

OFFERED DOCUMENTATION:
We are prepared to submit SIH problem statement details, project architecture documentation, data security plans, or formal compliance undertakings upon request.

SINCERELY,

Punith B S
University of Visvesvaraya College of Engineering + Team_Side_Quest
Mentor / Faculty Contact: N/A
Email: sihteamsidequest@gmail.com
Phone: N/A

SIH Project Details:
Smart India Hackathon (SIH) project — POLARIS: an AI-driven predictive energy-management system designed for polar research stations. The system forecasts energy demand and renewable generation using historical, weather, and station data, and uses these forecasts to optimize renewable generation, battery storage, diesel generation, and flexible loads while maintaining reliable energy service under polar operating constraints.
```

---

## 8. Historical Data Access Scope & Distinctions

The request strictly distinguishes historical data access from operational access:

- **What is requested**: Historical measured electrical demand time-series data for offline algorithmic evaluation and SIH demonstration.
- **What is NOT requested**:
  - Physical station access or site visits;
  - Live station control or grid telemetry connection;
  - Private system passwords or network credentials;
  - Unrestricted public redistribution of raw data;
  - Proprietary equipment designs beyond permitted data release.

---

## 9. Data-Suitability Questions

When evaluating any dataset offered by a custodian, the project team must apply the following 15 suitability questions before authorizing integration work:

- **Question A**: Is measured electrical demand/load available?
- **Question B**: Is it station-level or building/facility-level?
- **Question C**: What is the temporal resolution ($\le 1\text{-hour}$ preferred)?
- **Question D**: What is the timestamp convention and timezone (UTC preferred)?
- **Question E**: What are the physical units ($\text{kW}$, $\text{W}$, $\text{kWh}$)?
- **Question F**: What historical date range is available?
- **Question G**: Is the series continuous?
- **Question H**: What percentage or nature of missing data exists?
- **Question I**: Are quality flags or maintenance/outage markers available?
- **Question J**: Is the measurement gross demand, net demand, generation, grid import/export, or another quantity?
- **Question K**: Is the measurement directly metered or derived?
- **Question L**: Are there known aggregation or preprocessing steps?
- **Question M**: What access/licensing restrictions apply?
- **Question N**: Can the data be used for a Smart India Hackathon (SIH) project?
- **Question O**: Can derived results be reported in an SIH project presentation, report, or demonstration?

---

## 10. Scientific & Engineering Integration Boundary

No software implementation or code modification is performed during this task.

If usable high-resolution demand data is eventually obtained and authorized, future integration must strictly respect the frozen POLARIS architecture:

```text
REAL MEASURED DATASET
         │
         v
REAL-DATA ADAPTER / PROVIDER  <-- Future Separate Authorization Only
         │
         v
EXISTING POLARIS DATA INTERFACES (LocalDataProvider / StationState)
         │
         v
ForecastEngine Boundary  (ForecastBundle v1.0)
         │
         v
FROZEN EMS / MPC / MILP OPTIMIZER
         │
         v
DispatchPlan v1.0
         │
         v
DigitalTwinSimulator
         │
         v
EvaluationEngine
```

### Boundary Constraints
- The frozen MILP formulation, MPC receding-horizon loop, `StationState` schema, `ForecastBundle` schema, `DispatchPlan` schema, `DigitalTwinSimulator`, `EvaluationEngine`, and D4-C1 fault containment semantics MUST NOT be modified to accommodate a dataset.
- Real-data integration must be handled entirely upstream via an authorized `RealDataIngestionAdapter`.

---

## 11. Current POLARIS Forecasting & Sensitivity Boundary

- **Stage8.1 Boundary**: Stage8.1 represents frozen solar-irradiance forecasting research. It is **NOT** connected to the EMS loop in this task.
- **D5 Boundary**: D5 represents a closed EMS controlled-perturbation sensitivity study on baseline forecasts. It is **NOT** reopened or rerun.
- **Demand Data Boundary**: The demand access request addresses a separate missing system input (measured station load). D5 did **NOT** use real station demand, Stage8.1 has **NOT** been validated on real station demand, and POLARIS has **NOT** claimed real-station EMS validation.

---

## 12. Bounded Access Strategy & Bounded Stopping Condition

This task represents **ONE BOUNDED FORMAL ACCESS ATTEMPT**.

### Execution Sequence
1. Finalize request package (`COMPLETE`).
2. Human review & identity verification (`COMPLETE`).
3. Human selection of target custodians (`COMPLETE`).
4. External submission (`EXECUTED BY HUMAN DISPATCH`).
5. Delivery audit & route monitoring (`IN PROGRESS` — AADC route bounced due to external sender restriction; SANAP, IPF, ACEP requests remain pending).
6. **Bounded Stop Branch**: If remaining custodians deny access, fail to respond, attach impractical conditions, or cannot provide usable high-resolution demand data, **PATH A IS CLOSED**. The project team may then separately consider the previously defined hybrid scenario option.

---

## 13. Delivery Audit & Access Event Record (2026-09-17)

### AADC Access Route Event
- **Target Custodian**: Australian Antarctic Division (AAD / AADC)
- **Attempted Channel**: `aadcwebqueries@aad.gov.au`
- **Delivery Status**: `DELIVERY FAILED — EXTERNAL SENDER RESTRICTION`
- **Error Code**: `550 5.7.133` (*Recipient distribution group restricts external senders; group only accepts messages from internal organization or allowed-senders list*)
- **AADC Data-Access Decision**: `NOT RECEIVED / NOT REVIEWED`
- **Scientific Interpretation**: `NONE` (*The access request was bounced by recipient-side mail server restrictions before reaching data custodians or receiving substantive review. This is an access-route delivery failure, NOT a data access rejection or dataset unavailability finding.*)
- **Retry Rule**: `NOT AUTHORIZED / DO NOT REPEAT` (*Do not repeatedly resend to aadcwebqueries@aad.gov.au or attempt to bypass sender restrictions.*)

---

## 14. Hard Firewall Verification

- **External Contact**: `DISPATCHED FOR SANAP, IPF, ACEP; AADC ROUTE BOUNCED (550 5.7.133)`
- **Data Acquisition**: `NOT PERFORMED`
- **Web / Dataset Search**: `NOT PERFORMED`
- **Code / Adapter Modification**: `NOT PERFORMED` (0 lines changed)
- **Stage8.1 Champion Connection**: `NOT PERFORMED` (`FROZEN`)
- **D5 Reopening**: `NOT PERFORMED` (`CLOSED`)
- **Synthetic Fixtures**: `PRESERVED`

---

## 15. Final Status Record

```text
PATH A:
FORMAL RESTRICTED-DATA ACCESS — BOUNDED ATTEMPT IN PROGRESS

AADC ACCESS ROUTE:
DELIVERY FAILED — EXTERNAL SENDER RESTRICTION (550 5.7.133)

AADC DATA-ACCESS DECISION:
NOT RECEIVED / NOT REVIEWED

OTHER ACCESS REQUESTS (SANAP, IPF, ACEP):
DISPATCHED / PENDING RESPONSE

SCIENTIFIC INTERPRETATION:
NONE — REJECTED BY RECIPIENT-SIDE SENDER RESTRICTIONS BEFORE SUBSTANTIVE REVIEW

RETRY TO SAME GROUP:
NOT AUTHORIZED / DO NOT REPEAT

ADAPTER:
NOT IMPLEMENTED / NOT AUTHORIZED

STAGE8.1:
FROZEN / NOT CONNECTED / NOT AUTHORIZED

D5:
CLOSED / UNTOUCHED / NOT RERUN

HYBRID SCENARIO:
NOT AUTHORIZED

SYNTHETIC FIXTURES:
PRESERVED

NEXT PROJECT ACTION:
WAIT FOR RESPONSES FROM OTHER ALREADY-SENT ACCESS REQUESTS / HUMAN DECISION IF FURTHER ACCESS ACTION IS REQUIRED
```
