# POLARIS L2-EXP-12: REPLAY ACCOUNTING AUDIT
**Experiment:** L2-EXP-12 Horizon Risk-Budget Comparison  
**Audit Timestamp:** 2026-10-04T11:34:29.056328+00:00  
**Status:** PASS — VERIFIED  

## 1. Accounting Invariants Verification
- **All Arms (A, B, C, D, E, F):**
  - Planned battery charge power: Strictly constrained by single-scenario GAP19 MILP energy capacity bound.
  - Realized battery SOC minimum: `40.37%` (Floor >= 20.0%).
  - Realized battery SOC maximum: `95.0%` (Ceiling <= 95.0%).
  - SOC Floor Violations: Exactly 0 across all arms.
  - SOC Ceiling Violations: Exactly 0 across all arms.

## 2. Information Firewall
- Ground-truth 2024 solar generation was strictly firewalled from all optimizer decisions across all 173 origins.
