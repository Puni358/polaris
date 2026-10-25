# POLARIS EMS — P_CRITICAL EXTERNAL PROVENANCE MATRIX

## Executive Summary

This document tracks data provenance across external web research, internal codebase files, and sealed governance policies.

---

## Provenance Tracking Register

| Parameter | External Research Provenance | Internal Repo Provenance | Governance Classification | Production Status |
| :--- | :--- | :--- | :--- | :--- |
| **$T_{\text{required\_baseline}}$ (6h)** | N/A (Internal Governance) | `TREQ-001` Resolution | `SEALED_GOVERNANCE_POLICY` | `SEALED` |
| **Option D Fallback** | N/A (Internal Governance) | `DEC-004` Resolution | `SEALED_GOVERNANCE_POLICY` | `SEALED` |
| **Protected Heating Equipment** | Regional (Abisko geothermal/heat pumps) | `loads.yaml:15` ($5\text{kW}$ prototype) | `SYNTHETIC_PROTOTYPE_PARAMETER` | `NOT_ESTABLISHED` |
| **Water Treatment Equipment** | Centralized Base Station Context | `loads.yaml:8` ($10\text{kW}$ prototype) | `SYNTHETIC_PROTOTYPE_PARAMETER` | `NOT_ESTABLISHED` |
| **Emergency Comms Hardware** | Weather station & cameras confirmed | `loads.yaml:5` (Subsumed in $30\text{kW}$) | `SYNTHETIC_PROTOTYPE_PARAMETER` | `NOT_ESTABLISHED` |
| **Electrical Circuit Map** | `NOT_FOUND` in public domain | `NOT_FOUND` in codebase | `NOT_ESTABLISHED` | `NOT_ESTABLISHED` |
| **Measured $P_{\text{critical}}(t)$** | `NOT_FOUND` in public domain | `NOT_FOUND` in codebase | `NOT_ESTABLISHED` | `NOT_ESTABLISHED` |
| **Total Demand `demand.point`** | `NOT_FOUND` in public domain | `ForecastBundle` v1.0.0 | `ESTABLISHED_TOTAL_DEMAND_INTERFACE` | `DO_NOT_RELABEL` |

---

## Provenance Audit Summary

Zero external web findings or synthetic prototype values have been improperly promoted to Nuolja station facts. Provenance boundaries remain 100% intact.
