# POLARIS STAGE 8 — OPUS FINAL ADVERSARIAL RESEARCH PROGRESS

> [!IMPORTANT]
> **RESEARCH_STATUS: `IN_PROGRESS`**
> **CURRENT_PHASE: `PHASE 3 — GNSS / ATMOSPHERIC COLUMN`**
> **LAST_UPDATED: `2026-09-13T18:24:00+05:30`**

---

## Status Summary

| Field | Value |
| :--- | :--- |
| **RESEARCH_STATUS** | `IN_PROGRESS` |
| **CURRENT_PHASE** | `PHASE 3 — GNSS / ATMOSPHERIC COLUMN INVESTIGATION` |
| **PHASES_COMPLETED** | `PHASE 0 (Project Reconciliation), PHASE 1 (Information Map), PHASE 2 (Radar Investigation)` |
| **PHASES_REMAINING** | `PHASE 3 (GNSS), 4 (Other Observations), 5 (Adversarial Test), 6 (Final Ranking)` |
| **CURRENT_BEST_CANDIDATE** | `GNSS IWV — CONDITIONAL (unverified 2024 data availability at Abisko/Kiruna)` |
| **CURRENT_TOP_CANDIDATES** | `(1) GNSS IWV [CONDITIONAL_B], (2) Ceilometer/Cloud Base [UNINVESTIGATED], (3) MEPS Analysis Increments [CONDITIONAL_B]` |
| **ROUTES_ELIMINATED_THIS_SESSION** | `Kiruna individual radar (no 2024 data), Luleå individual radar (no 2024 data), Sweden composite radar (CLASS C — wrong physical quantity)` |
| **ROUTES_REMAINING_UNRESOLVED** | `GNSS IWV, Ceilometer, Analysis Increments, Upstream SYNOP, Cloud Radar/Lidar, Microwave Satellite` |
| **KEY_EVIDENCE_DISCOVERED** | `(1) Sweden composite radar has complete 2024 data at 5-min cadence with ~1-min latency. (2) BUT the physical measurement (hydrometeor reflectivity) is NOT the information gap. (3) Stage 8.1 lacks independent cloud OPTICAL information, not precipitation detection. (4) MEPS already assimilates radar, so raw radar is partially redundant. (5) Individual Kiruna/Luleå radars have NO 2024 archive.` |
| **KEY_SOURCES** | `SMHI open-data radar API (direct queries, verified 2026-09-13)` |
| **KEY_UNCERTAINTIES** | `(1) GNSS station existence near Abisko with 2024 IWV data. (2) Whether any ceilometer/cloud profiler operates near Nuolja. (3) Whether MEPS analysis increments are published with causal timeliness.` |
| **NEXT_ACTION** | `Phase 3: GNSS/SWEPOS investigation — station identification, IWV product, 2024 availability` |
| **EXACT_STOPPING_POINT** | `Phase 2 complete & saved. Phase 3 beginning.` |

---

## Phase 2 — Radar Investigation Summary (COMPLETED)

### Verified Facts
1. Sweden composite `comp` product: complete 2024 archive, 5-min cadence, ~1-min publication latency, PNG/TIF/H5 formats
2. Kiruna `qcvol`: NO 2024 data (Jan, Jun both empty)
3. Luleå `qcvol`: NO 2024 data
4. Composite measures hydrometeor reflectivity/precipitation rate — NOT cloud optical depth
5. MEPS already assimilates radar data → partial information redundancy

### Classification
- **Sweden Composite: CLASS C** — weak novelty, wrong physical quantity for SW_IN gap
- **Kiruna Individual: CLASS D** — operationally infeasible (no 2024 data)
- **Luleå Individual: CLASS D** — operationally infeasible (no 2024 data, too far)

### Full report: `STAGE8_OPUS_PHASE_02_RADAR.md`

---

## Governance Confirmations
- ODD: 100% UNTOUCHED & PROTECTED
- POLARIS_MASTER_HANDOFF.md: UNTOUCHED
- POLARIS_STAGE8_ROUTE_REGISTRY.*: UNTOUCHED
- No experiments run, no models modified
