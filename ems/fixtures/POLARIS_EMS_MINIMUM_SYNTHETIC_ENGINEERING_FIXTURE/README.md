# POLARIS EMS — MINIMUM SYNTHETIC ENGINEERING FIXTURE
## FROZEN SYNTHETIC ENGINEERING FIXTURE DATASET & SPECIFICATION

### 1. FIXTURE PURPOSE & ARCHITECTURAL SCOPE
This package contains the frozen, deterministic synthetic engineering fixture generated to make the complete POLARIS EMS software architecture demonstrable end-to-end. 

The fixture provides complete data coverage for:
- Data Provider ingestion and `StationState` schema validation
- `ForecastEngine` bundle creation ($\hat{P} = 1.10 \times P_{\text{actual}}$)
- Emergency Condition Detector (ECD) $T_{\text{required\_baseline}} = 6.0\text{h}$ state classification
- Option D emergency policy layer (renewable critical support, diesel excess charging, curtailment, proportional allocation)
- `EnergyOptimizer / MILP` multi-period dispatch formulation
- `DigitalTwinSimulator` closed-loop state update evaluation

### 2. HARD SCIENTIFIC & PROVENANCE FIREWALL
> **CRITICAL NOTICE**: THIS FIXTURE IS 100% SYNTHETIC.
>
> It does NOT contain measured Nuolja station demand, live telemetry, actual electrical circuit mappings, real generator fuel curves, or real battery health data (`DIRECT_NUOLJA_EVIDENCE = 0`).
>
> Zero synthetic values or simulation outcomes from this package may be cited as empirical Nuolja station facts or performance claims.

### 3. ARTIFACT MANIFEST
1. [README.md](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_MINIMUM_SYNTHETIC_ENGINEERING_FIXTURE/README.md) - Package Overview & Data Contract Index
2. [POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.csv](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_MINIMUM_SYNTHETIC_ENGINEERING_FIXTURE/POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.csv) - 120-Row Canonical Time Series Dataset (5 Scenarios $\times$ 24 Hours)
3. [POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.json](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_MINIMUM_SYNTHETIC_ENGINEERING_FIXTURE/POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.json) - Structured Hierarchical Fixture Dataset
4. [POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE_PROVENANCE.json](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_MINIMUM_SYNTHETIC_ENGINEERING_FIXTURE/POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE_PROVENANCE.json) - Provenance Metadata Manifest
5. [POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE_CALCULATION_MANIFEST.md](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_MINIMUM_SYNTHETIC_ENGINEERING_FIXTURE/POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE_CALCULATION_MANIFEST.md) - Physical Equations & Mathematical Accounting Manifest
6. [POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE_SCENARIO_MATRIX.md](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_MINIMUM_SYNTHETIC_ENGINEERING_FIXTURE/POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE_SCENARIO_MATRIX.md) - 5-Scenario Deterministic Input Matrix
7. [POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE_TRUTH_FIREWALL.md](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_MINIMUM_SYNTHETIC_ENGINEERING_FIXTURE/POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE_TRUTH_FIREWALL.md) - Information Isolation Audit & Verification
8. [POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE_CLAIM_FIREWALL.md](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_MINIMUM_SYNTHETIC_ENGINEERING_FIXTURE/POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE_CLAIM_FIREWALL.md) - Scientific & Empirical Boundary Specification
9. [POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE_GENERATION_REPORT.md](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_MINIMUM_SYNTHETIC_ENGINEERING_FIXTURE/POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE_GENERATION_REPORT.md) - Read-Only Validation & Generation Report
10. [HASH_AUDIT.json](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_MINIMUM_SYNTHETIC_ENGINEERING_FIXTURE/HASH_AUDIT.json) - SHA-256 Cryptographic Hash Digest Manifest
