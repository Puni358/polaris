# POLARIS EMS — PROTECTED CRITICAL LOAD STATION EVIDENCE DECISION FORM

## Executive Statement

This form specifies the empirical station evidence required from site electrical engineers before a production **$P_{\text{critical}}(t)$** trajectory can be constructed for Nuolja Station.

> [!IMPORTANT]
> **GOVERNANCE DECISION FIREWALL**:
> This form does **NOT** ask governance to choose policy numbers or redefine sealed decisions ($T_{\text{required\_baseline}} = 6\text{h}$, Option D fallback). Sealed governance policies remain 100% untouched. This form collects empirical site engineering data only.

---

## Required Station Engineering Submissions

### ITEM 1: Physical Protected Equipment Datasheets
*Please provide certified nameplate datasheets for station life-support systems:*
- [ ] Essential space heating system datasheets (kW rating, circuit ID, location).
- [ ] Essential water treatment & filtration pump datasheets (kW rating, flow rate, duty cycle).
- [ ] Emergency communications & SCADA control rack datasheets (nominal & peak Watts).

`STATUS: UNCOLLECTED`

---

### ITEM 2: As-Built Electrical Single-Line Diagram & Panel Schedule
*Please provide station electrical drawings:*
- [ ] As-built Single-Line Diagram (SLD) showing main feeder, transformer, and bus routing.
- [ ] Breaker panel schedule identifying controllable vs non-controllable load breakers.
- [ ] SCADA breaker actuator channel mapping.

`STATUS: UNCOLLECTED`

---

### ITEM 3: Minimum Viable Operating Levels ($P_{\text{min}}$)
*Please specify lower electrical bounds required for Option D Rule D4 proportional allocation:*
- [ ] $P_{\text{min,heating}}$ (Minimum kW to maintain indoor temp $\ge +5^\circ\text{C}$).
- [ ] $P_{\text{min,water}}$ (Minimum kW for baseline 50L/day water production).
- [ ] $P_{\text{min,comms}}$ (Minimum kW for SCADA heartbeat and emergency beacon).

`STATUS: UNCOLLECTED`

---

### ITEM 4: Sub-Hourly Inrush Current Ratings
*Please specify motor startup power spikes:*
- [ ] Water pump locked-rotor inrush multiplier and spike duration (seconds).
- [ ] Heating compressor / fan startup inrush multiplier.

`STATUS: UNCOLLECTED`

---

## Form Execution Status

- **HUMAN_GOVERNANCE_DECISIONS_REOPENED**: `NO`
- **ENGINEERING_DATA_COLLECTION_REQUIRED**: `YES`
- **P_CRITICAL_CONSTRUCTION_READINESS**: `NOT_READY`
