# POLARIS — G1.3-E RESEARCH REQUIREMENTS & RESEARCH AGENDA

## Executive Summary

This document defines the **Research Requirements Agenda** that must be completed before resource-specific telemetry freshness rules can be specified for G1.3-E.

Consistent with Human Decision G1.3-E, no numerical freshness numbers have been assigned. This document outlines the technical research questions, empirical evidence requirements, and physical criteria needed to establish resource-specific freshness specifications.

---

## 1. Core Research Question

The research deliverable resulting from this agenda must answer:

> **"What is the maximum permissible age of each safety-critical measurement for this specific resource and this specific survivability decision, and what evidence justifies that value?"**

---

## 2. Resource-Specific Research Domains

The research agenda is structured across thirteen physical and operational dimensions:

### 2.1 Dimension 1: Telemetry Type & Physical Dynamics
- **Research Scope**: Measure the physical rate-of-change ($\frac{dx}{dt}$) of different microgrid variables.
  - *Fuel Tank Level*: Changes slowly ($\approx \text{Liters/hour}$). A 5-minute fuel measurement age represents minimal physical change under steady load.
  - *Generator Operating Health / Fault Relay*: Changes instantaneously ($\approx \text{milliseconds}$ during breaker trip). A 5-minute-old health status could miss an active engine trip.
  - *AC Bus Output Voltage / Frequency*: Fluctuates sub-second.

### 2.2 Dimension 2: Generator Operating State (Running vs OFF)
- **Research Scope**: Evaluate freshness requirements based on generator state ($u(t_0)$).
  - *Running Generator ($u=1$)*: Requires fresh fuel flow, oil pressure, and cooling temperature telemetry to verify continuous deliverability.
  - *OFF Generator ($u=0$)*: Requires fresh battery voltage for starter motor, block heater temperature, and fuel valve position to establish start-readiness.

### 2.3 Dimension 3: Communication Path & Network Jitter
- **Research Scope**: Model network transport dynamics across SCADA topologies:
  - Wired Modbus RTU / Ethernet ($\text{latency} < 100\text{ ms}$).
  - Remote Satellite Link (Iridium / Starlink) during polar blizzards ($\text{latency} = 5\text{ s}$ to $300\text{ s}$ with occasional packet loss).
- **Goal**: Ensure freshness rules do not cause unneeded telemetry fault locks during routine satellite communication jitter.

### 2.4 Dimension 4: Consequence Severity of Stale Information
- **Research Scope**: Classify measurements by failure consequence:
  - *Class A (Critical Failure Hazard)*: Stale generator health status masking an active trip $\rightarrow$ High risk of unserved critical load if battery is low.
  - *Class B (Deficit Hazard)*: Stale fuel measurement masking slow leak $\rightarrow$ Risk of fuel exhaustion after 4+ hours.
  - *Class C (Economic Penalty Only)*: Stale ambient temperature $\rightarrow$ Minor derating error.

---

## 3. Resource-Specific Research Matrix Template

The future research pass must populate the following matrix using empirical station data or hardware hardware-in-the-loop (HIL) testing:

| Telemetry Measurement Name | Physical Sensor Type | Typical Update Rate | Max Rate of Change ($\frac{dx}{dt}$) | Failure Consequence Class | Max Permissible Age ($\Delta t_{\text{fresh\_max}}$) | Justifying Evidence Source |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| Generator Breaker / Health Status | ECU Relay Bit | $1.0\text{ s}$ | Instantaneous | Class A | *To Be Researched* | ECU Fault Log & HIL Test |
| Day-Tank Fuel Level | Ultrasonic / Hydrostatic | $10.0\text{ s}$ | $25.0\text{ L/h}$ | Class B | *To Be Researched* | Fuel Tank Dynamics Model |
| Start-Readiness Battery Voltage | Analog DC Voltmeter | $5.0\text{ s}$ | $0.1\text{ V/h}$ | Class A | *To Be Researched* | Battery Starter Curve |
| Engine Block Heater Temp | RTD Sensor | $60.0\text{ s}$ | $2.0^\circ\text{C/h}$ | Class B | *To Be Researched* | Thermal Loss Model |

---

## 4. Summary of Research Deliverable Requirements

To authorize code implementation of G1.3-E, the research team must deliver:
1. Empirically justified $\Delta t_{\text{fresh\_max}}$ parameters for each measurement in the matrix above.
2. Fallback logic definitions for each measurement when telemetry exceeds $\Delta t_{\text{fresh\_max}}$.
3. Validation test results proving the freshness rules do not produce false Emergency triggers during satellite comm drops.
