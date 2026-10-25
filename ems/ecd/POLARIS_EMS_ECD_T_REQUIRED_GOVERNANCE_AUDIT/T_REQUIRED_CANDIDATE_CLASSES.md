# POLARIS EMS — T_REQUIRED CANDIDATE SEMANTIC CLASSES

## 1. Overview

This document presents a neutral, evidence-based investigation of **five candidate semantic classes** for $T_{\text{required}}$. These candidate classes represent distinct operational paradigms for defining the emergency survivability horizon.

> [!NOTE]
> These candidate classes are provided for decision-support analysis only. They are **NOT** ranked or recommended. Selection rests solely with human governance.

---

## 2. Candidate Class A: Short-Horizon Operational Survivability (6h – 12h)

- **Meaning**: Focuses on immediate battery/diesel reserve adequacy to bridge short-term power interruptions or provide an immediate operational window for local operator dispatch.
- **Required Inputs**: Battery usable energy, immediate critical load $P_{\text{critical}}$, local operator response time window.
- **Station Data Required**: Operator response SLA, local shift schedule.
- **ECD Interaction**: ECD flags `EMERGENCY` if available stored energy cannot guarantee 6–12 hours of critical service.
- **Option D Interaction**: Short horizon triggers `UNKNOWN_INVALID` and safe state rapidly if telemetry or system data degrades.
- **Implementation Implications**: Computationally lightweight; minimal forecast horizon dependencies.
- **Supporting Evidence**: Supported by local operator dispatch response expectations.
- **Missing Evidence**: Station operator response SLAs are not established in repository data.

---

## 3. Candidate Class B: 24-Hour Daily Survivability (24h)

- **Meaning**: Aligns the survivability horizon with a complete diurnal solar cycle, ensuring the station can survive one full 24-hour day without renewable generation.
- **Required Inputs**: 24-hour dynamic critical load profile $P_{\text{critical}}(t)$, battery SOC, daily generator fuel usage.
- **Station Data Required**: Diurnal load profiles, daily weather variance bounds.
- **ECD Interaction**: Tests whether stored energy (battery + fuel) can bridge a full 24-hour zero-renewable day.
- **Option D Interaction**: Provides a natural daily cadence for safe-state evaluation and operator status reports.
- **Implementation Implications**: Matches standard 24-hour rolling horizon MPC optimization structures.
- **Supporting Evidence**: Standard diurnal solar cycle in renewable microgrid literature.
- **Missing Evidence**: Polar winter conditions involve polar night (0 solar for weeks), making 24h solar cycle alignment site-specific.

---

## 4. Candidate Class C: Multi-Day Storm/Blizzard Survivability (48h – 96h)

- **Meaning**: Designed to sustain protected critical service through extended adverse weather events (e.g. 2-to-4 day severe arctic storms or blizzards) where renewable generation is zero and off-site maintenance access is impossible.
- **Required Inputs**: 48h–96h critical load envelope, generator fuel storage capacity, battery reserve.
- **Station Data Required**: Historical extreme weather anomaly duration metrics for Nuolja station.
- **ECD Interaction**: High-bar survivability gate. Prototype fixture's 72-hour synthetic value falls within this class.
- **Option D Interaction**: Option D degraded fallback operates under Option D rules while awaiting storm passage or operator escalation.
- **Implementation Implications**: Requires high fuel inventory reserves to maintain `NORMAL` status.
- **Supporting Evidence**: Synthetic prototype fixture used 72 hours as an engineering test parameter.
- **Missing Evidence**: Historical weather anomaly duration distributions for Nuolja station are `NOT_ESTABLISHED`.

---

## 5. Candidate Class D: Next-Resupply Survivability (Logistics Horizon)

- **Meaning**: $T_{\text{required}}$ is set dynamically or statically to match the exact time remaining until the next scheduled fuel delivery or logistics resupply mission.
- **Required Inputs**: Scheduled resupply timestamp ($t_{\text{resupply}}$), current timestamp ($t_{\text{current}}$), critical load forecast trajectory.
- **Station Data Required**: Official fuel delivery calendar, logistics lead times, buffer margins.
- **ECD Interaction**: $T_{\text{required}} = t_{\text{resupply}} - t_{\text{current}}$. Shrinks dynamically as resupply approaches.
- **Option D Interaction**: Directly ties emergency condition detection to logistics fuel depletion risks.
- **Implementation Implications**: Requires dynamic $T_{\text{required}}$ input interface and dynamic schedule ingestion.
- **Supporting Evidence**: Standard practice for remote off-grid fuel management.
- **Missing Evidence**: No resupply schedule or logistics calendar exists in the repository (`FUEL_RESUPPLY_INTERVAL = NOT_ESTABLISHED`).

---

## 6. Candidate Class E: Mission / Seasonal Survivability (Polar Winter Horizon)

- **Meaning**: $T_{\text{required}}$ covers extended multi-week or multi-month seasonal isolation periods (e.g. polar night winter season) where no fuel delivery or solar generation is possible for months.
- **Required Inputs**: Seasonal fuel storage reserves, winter season duration, minimum baseline heating/filtration loads.
- **Station Data Required**: Annual polar winter operational calendar, bulk fuel tank capacities.
- **ECD Interaction**: ECD measures overall seasonal fuel depletion rate against remaining winter duration.
- **Option D Interaction**: Triggers high-level governance escalation if seasonal fuel depletion exceeds allowable burn rate.
- **Implementation Implications**: Evaluated at supervisory macro-level; distinct from short-term MPC control.
- **Supporting Evidence**: Conceptual polar station survivability requirements.
- **Missing Evidence**: Nuolja site-specific seasonal operational calendar and bulk fuel storage specs are `NOT_ESTABLISHED`.

---

## Summary Matrix of Candidate Classes

| Candidate Class | Primary Focus | Nominal Horizon Range | Primary Unresolved Input Gap |
| :--- | :--- | :--- | :--- |
| **Class A** | Operator Response Window | 6h – 12h | Operator response SLA |
| **Class B** | Diurnal Solar Cycle | 24h | Site diurnal winter load profiles |
| **Class C** | Multi-Day Storm Endurance | 48h – 96h | Weather anomaly duration metrics |
| **Class D** | Logistics Fuel Resupply | Variable ($t_{\text{resupply}} - t$) | Resupply logistics calendar |
| **Class E** | Seasonal Winter Isolation | Multi-week / Seasonal | Bulk seasonal tank specs |
