# POLARIS L2-EXP-11: REPLAY ACCOUNTING AUDIT
**Experiment:** L2-EXP-11 Adaptive q10 Relaxation  
**Audit Timestamp:** 2026-10-04T11:14:51.478221+00:00  
**Status:** VERIFIED  

## 1. Accounting Invariants Verification
- **Arm D (NN Adaptive-q):**
  - Planned battery charge power: Strictly constrained by single-scenario GAP19 MILP energy capacity bound.
  - Realized battery SOC minimum: `37.91%` (Floor >= 20.0%).
  - Realized battery SOC maximum: `95.0%` (Ceiling <= 95.0%).
  - SOC Floor Violations: `0`.
  - SOC Ceiling Violations: `0`.

- **Arm C (L2-EXP-10 Arm F Replay Fix):**
  - Planned battery charge power: Corrected to use central scenario planned charge (`sol[c_offset + t*K + 4]`).
  - Realized battery SOC minimum: `2.75%`.
  - Realized battery SOC maximum: `95.0%`.
  - SOC Floor Violations: `62`.
  - SOC Ceiling Violations: `0` (Eliminated previous 604 upper-bound excursions).

## 2. Information Firewall
- Ground-truth 2024 solar generation was strictly firewalled from model training, calibration, and all optimizer decisions across all 173 origins.
