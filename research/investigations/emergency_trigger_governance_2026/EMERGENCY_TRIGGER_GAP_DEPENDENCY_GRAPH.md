# POLARIS — EMERGENCY TRIGGER GAP DEPENDENCY GRAPH

## Executive Overview

This artifact documents the **inter-gap dependencies and decision precedence topology** for resolving the remaining POLARIS Emergency Governance gaps. 

Resolving human governance decisions in the correct logical sequence prevents contradictory specification rules and ensures mathematical consistency.

---

## 1. Cross-Gap Interaction Analysis

```
+-----------------------------------------------------------------------------------+
|                           1. GENERATOR <-> RENEWABLE                              |
| GAP-01 (Gen Credibility) and GAP-02 (Renewable Derating) jointly determine total   |
| net deliverable energy. If renewables receive zero credit (GAP-02 Option C),       |
| generator credibility (GAP-01) becomes the sole determinant of 6h survivability.  |
+-----------------------------------------------------------------------------------+

+-----------------------------------------------------------------------------------+
|                        2. SURVIVABILITY MARGIN <-> EXIT                           |
| GAP-01/02 establish M_surv math. GAP-03 (Exit Criteria) and GAP-05 (Exit Path)    |
| evaluate M_surv for state transitions. M_surv math MUST be locked before exit    |
| thresholds (+10 kWh or 4-interval persistence) can be finalized.                 |
+-----------------------------------------------------------------------------------+

+-----------------------------------------------------------------------------------+
|                        3. RESERVE TARGET <-> EXIT PATH                            |
| GAP-05 (Exit to Deficit vs Normal) depends on whether SOC >= 37.83% is a          |
| mandatory exit condition (GAP-03). If exit requires SOC >= 37.83%, exit to        |
| RESERVE_DEFICIT is impossible because SOC is already at reserve target.           |
+-----------------------------------------------------------------------------------+

+-----------------------------------------------------------------------------------+
|                     4. UNKNOWN_INVALID <-> FORECAST FALLBACK                      |
| GAP-04 (Missing Forecast Fallback) dictates whether missing weather telemetry     |
| triggers UNKNOWN_INVALID (sensor lock) or sets E_ren = 0.0 (fail-safe fallback).   |
+-----------------------------------------------------------------------------------+
```

---

## 2. Decision Precedence Dependency Graph (Mermaid)

```mermaid
flowchart TD
    subgraph Layer1["Layer 1: Core Credibility Policies (Must Decide First)"]
        GAP01["GAP-01: Generator Credibility Model<br>(Model A, B, C, or D)"]
        GAP02["GAP-02: Renewable Forecast Policy<br>(Option A, B, C, or D)"]
    end

    subgraph Layer2["Layer 2: Energy Balance & Telemetry Safeguards"]
        M_SURV["Mathematical Equation:<br>M_surv = E_batt + E_gen + E_ren - 69.60 kWh"]
        GAP04["GAP-04: Missing Forecast Fallback<br>(Zero Renewable vs UNKNOWN_INVALID)"]
    end

    subgraph Layer3["Layer 3: Exit Conditions & Topology"]
        GAP03["GAP-03: Exit Parameters<br>(SOC >= 37.83% & Generator Required?)"]
        GAP05["GAP-05: Exit Transition Path<br>(Exit to NORMAL vs RESERVE_DEFICIT)"]
    end

    subgraph Layer4["Layer 4: Final Implementation Specification"]
        SPEC["POLARIS ECD Production Code Spec<br>(ecd.py & State Machine)"]
    end

    GAP01 --> M_SURV
    GAP02 --> M_SURV
    GAP02 --> GAP04
    M_SURV --> GAP03
    GAP03 --> GAP05
    GAP04 --> SPEC
    GAP05 --> SPEC

    style GAP01 fill:#f9f,stroke:#333,stroke-width:2px
    style GAP02 fill:#f9f,stroke:#333,stroke-width:2px
    style GAP03 fill:#bbf,stroke:#333,stroke-width:2px
    style GAP04 fill:#bbf,stroke:#333,stroke-width:2px
    style GAP05 fill:#bbf,stroke:#333,stroke-width:2px
    style SPEC fill:#bfb,stroke:#333,stroke-width:2px
```

---

## 3. Recommended Order of Decision Sign-Off

To ensure systematic resolution, the human project owner should resolve decisions in the following sequence:

1. **FIRST**: Resolve **GAP-01** (Generator Credibility Model) and **GAP-02** (Renewable Forecast Policy). This locks the input terms of the $M_{\text{surv}}$ equation.
2. **SECOND**: Resolve **GAP-04** (Missing Forecast Fallback). This defines system behavior when weather telemetry drops out.
3. **THIRD**: Resolve **GAP-03** (Emergency Exit Requirements) and **GAP-05** (Exit Transition Topology). This defines state transition mechanics.
4. **FOURTH**: Authorize ECD production code implementation based on the fully locked specification.
