# POLARIS — Real-Data Human-Authorized Contact Action Package

> **Notice:** DO NOT SEND ANYTHING AUTOMATICALLY.  
> This document defines human-authorized request packages for manual dispatch by designated project leads. Zero outbound network calls or automated messages have been sent.

---

## Package Overview

This package specifies the exact technical and provenance parameters required to submit formal data-access requests to official polar research station data custodians. Each request package is structured to ensure that any received dataset meets the strict qualification criteria for POLARIS real-station demand validation.

---

## Human Action Request Specifications

### 1. British Antarctic Survey (BAS) / UK Polar Data Centre (UK PDC)

- **Organization:** British Antarctic Survey (BAS) / UK Polar Data Centre (UK PDC)
- **Facility / Target:** Rothera Research Station / Halley VI Research Station (Antarctica)
- **Official Contact / Access Route:** [`https://data.bas.ac.uk`](https://data.bas.ac.uk) (Official Data Request Portal) / `data@bas.ac.uk`
- **Data Requested:** Measured station-level active electrical demand time series
- **Exact Variables:**
  - Active Electrical Load $P_{\text{load}}$ ($\text{kW}$ or $\text{W}$)
  - UTC Interval Timestamps (ISO 8601 format)
  - *Optional:* Diesel generator output ($\text{kW}$), Renewable PV/Wind generation ($\text{kW}$)
- **Requested Temporal Resolution:** Continuous 1-hour interval ($\Delta t \le 1\text{h}$)
- **Requested Period:** Longest continuous historical period available (multi-month or multi-year)
- **Scientific Purpose:** Offline evaluation of AI-driven Model Predictive Control (MPC) dispatch algorithms under empirical polar station load dynamics for Smart India Hackathon (SIH) research project POLARIS.
- **Provenance Requirements:** Metering instrumentation metadata, physical units declaration, timestamp timezone specification (UTC), data quality flags, and missing data markers.
- **Accompanying Evidence Required:** Official custodian dataset documentation, terms of use / license agreement, and metering methodology summary.

---

### 2. Alfred Wegener Institute (AWI) / PANGAEA Data Publisher

- **Organization:** Alfred Wegener Institute, Helmholtz Centre for Polar and Marine Research (AWI) / PANGAEA Data Publisher
- **Facility / Target:** Neumayer Station III (Atka Bay, Dronning Maud Land, Antarctica)
- **Official Contact / Access Route:** [`https://www.pangaea.de`](https://www.pangaea.de) (Data Request Portal) / `info@pangaea.de` / `station-manager@awi.de`
- **Data Requested:** Measured station-level active electrical demand and wind-diesel microgrid telemetry
- **Exact Variables:**
  - Active Electrical Load $P_{\text{load}}$ ($\text{kW}$ or $\text{W}$)
  - UTC Interval Timestamps (ISO 8601 format)
  - *Optional:* Wind turbine electrical generation ($\text{kW}$), Diesel generator running state / power ($\text{kW}$)
- **Requested Temporal Resolution:** Continuous 1-hour interval ($\Delta t \le 1\text{h}$)
- **Requested Period:** Longest continuous historical period available
- **Scientific Purpose:** Offline validation of predictive energy management system (EMS) dispatch models under real polar microgrid demand patterns for SIH research project POLARIS.
- **Provenance Requirements:** Metering location, sensor specifications, physical unit confirmation ($\text{kW}$), UTC timestamps, and explicit data quality indicators.
- **Accompanying Evidence Required:** PANGAEA DOI / dataset citation metadata, custodian terms of use, and data collection methodology.

---

### 3. Norwegian Polar Institute (NPI) / Norwegian Polar Data Centre

- **Organization:** Norwegian Polar Institute (NPI) / Norsk Polarinstitutt
- **Facility / Target:** Troll Research Station (Jutulsessen, Dronning Maud Land, Antarctica)
- **Official Contact / Access Route:** [`https://data.npolar.no`](https://data.npolar.no) (Norwegian Polar Data Centre Portal) / `data@npolar.no`
- **Data Requested:** Measured station electrical demand and smart microgrid load profile time series
- **Exact Variables:**
  - Active Electrical Load $P_{\text{load}}$ ($\text{kW}$ or $\text{W}$)
  - UTC Interval Timestamps (ISO 8601 format)
  - *Optional:* Solar PV power output ($\text{kW}$), Battery storage State of Charge ($\text{SOC \%}$)
- **Requested Temporal Resolution:** Continuous 1-hour interval ($\Delta t \le 1\text{h}$)
- **Requested Period:** Longest continuous historical period available
- **Scientific Purpose:** Offline receding-horizon MPC optimization benchmark using empirical station electrical load data for SIH research project POLARIS.
- **Provenance Requirements:** Measurement methodology, physical units declaration, timezone specification (UTC), missing data flags.
- **Accompanying Evidence Required:** Norwegian Polar Data Centre dataset license agreement and official usage terms.

---

### 4. Australian Antarctic Division (AAD) / Australian Antarctic Data Centre (AADC)

- **Organization:** Australian Antarctic Division (AAD) / AADC
- **Facility / Target:** Casey, Davis, Mawson, Macquarie Island Stations (Antarctica)
- **Official Contact / Access Route:** [`https://data.aad.gov.au/contact`](https://data.aad.gov.au/contact) (Web Enquiry Portal) / [`https://data.aad.gov.au/aadc/portal/`](https://data.aad.gov.au/aadc/portal/)
- **Data Requested:** High-resolution logger electrical load time series (beyond archived public monthly totals)
- **Exact Variables:**
  - Active Electrical Load $P_{\text{load}}$ ($\text{kW}$ or $\text{W}$)
  - UTC Interval Timestamps (ISO 8601 format)
- **Requested Temporal Resolution:** Continuous 1-hour interval ($\Delta t \le 1\text{h}$)
- **Requested Period:** 1993–2016 historical logger archives
- **Scientific Purpose:** Offline microgrid dispatch algorithm evaluation using high-resolution station telemetry for SIH project POLARIS.
- **Provenance Requirements:** Logger metadata, unit confirmation, missing data documentation.
- **Accompanying Evidence Required:** AADC dataset metadata record and terms of use for academic research.

---

### 5. South African National Antarctic Programme (SANAP) / DFFE

- **Organization:** South African National Antarctic Programme (SANAP) / Department of Forestry, Fisheries and the Environment (DFFE)
- **Facility / Target:** SANAE IV Station (Vesleskarvet, Dronning Maud Land, Antarctica)
- **Official Contact / Access Route:** [`https://polar.sanap.ac.za`](https://polar.sanap.ac.za) (Portal Request Form) / NRF-SAEON Data Office
- **Data Requested:** Historical 1-hour active electrical demand telemetry
- **Exact Variables:**
  - Active Electrical Load $P_{\text{load}}$ ($\text{kW}$ or $\text{W}$)
  - UTC Interval Timestamps (ISO 8601 format)
- **Requested Temporal Resolution:** Continuous 1-hour interval ($\Delta t \le 1\text{h}$)
- **Requested Period:** Multi-year operational logging horizon
- **Scientific Purpose:** Offline EMS load-following and microgrid dispatch benchmark for SIH research project POLARIS.
- **Provenance Requirements:** Instrumentation metadata, units ($\text{kW}$), quality control flags.
- **Accompanying Evidence Required:** SANAP / DFFE data sharing authorization document.

---

### 6. International Polar Foundation (IPF) / BELSPO

- **Organization:** International Polar Foundation (IPF) / Belgian Science Policy Office (BELSPO)
- **Facility / Target:** Princess Elisabeth Antarctica Station
- **Official Contact / Access Route:** [`https://www.polarfoundation.org`](https://www.polarfoundation.org) / [`https://www.antarcticstation.org`](https://www.antarcticstation.org) (Portal Form)
- **Data Requested:** Zero-emission microgrid active load telemetry time series
- **Exact Variables:**
  - Active Microgrid Electrical Load $P_{\text{load}}$ ($\text{kW}$ or $\text{W}$)
  - UTC Interval Timestamps (ISO 8601 format)
- **Requested Temporal Resolution:** Continuous 1-hour or sub-hourly interval ($\Delta t \le 1\text{h}$)
- **Requested Period:** Multi-year operational profile
- **Scientific Purpose:** Evaluating offline predictive microgrid controller dispatch on zero-emission polar station load profiles for SIH project POLARIS.
- **Provenance Requirements:** Metering point description, units ($\text{kW}$), timestamp timezone.
- **Accompanying Evidence Required:** IPF / BELSPO research data agreement.

---

### 7. Alaska Center for Energy and Power (ACEP / UAF)

- **Organization:** Alaska Center for Energy and Power (ACEP) / University of Alaska Fairbanks
- **Facility / Target:** Kotzebue, Cordova, Wales Arctic Remote Microgrids
- **Official Contact / Access Route:** [`https://data.acep.uaf.edu`](https://data.acep.uaf.edu) (Data Portal Form) / [`https://energyalaska.uaf.edu`](https://energyalaska.uaf.edu)
- **Data Requested:** Remote community active electrical demand time series
- **Exact Variables:**
  - Community Electrical Demand $P_{\text{load}}$ ($\text{kW}$)
  - UTC Interval Timestamps (ISO 8601 format)
- **Requested Temporal Resolution:** Continuous 1-hour interval ($\Delta t \le 1\text{h}$)
- **Requested Period:** Multi-year continuous time series
- **Scientific Purpose:** Offline benchmark evaluation of predictive energy management systems on remote polar/sub-polar microgrid load profiles for SIH project POLARIS.
- **Provenance Requirements:** Utility metering metadata, units ($\text{kW}$), quality markers.
- **Accompanying Evidence Required:** ACEP / UAF data access agreement and attribution requirements.
