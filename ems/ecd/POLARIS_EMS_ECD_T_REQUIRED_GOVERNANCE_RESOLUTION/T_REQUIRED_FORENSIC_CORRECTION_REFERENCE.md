# POLARIS EMS — T_REQUIRED FORENSIC CORRECTION REFERENCE

## 1. Executive Summary

This document references and preserves all verified forensic corrections established during prior audits. Selecting the production $6\text{-hour}$ baseline ($T_{\text{required\_baseline}} = 6\text{h}$) does **NOT** alter, invalidate, or revert these verified code and governance facts.

---

## 2. Preserved Forensic Facts

### Fact 1: 72-Hour Synthetic Prototype Classification
- **Fact**: $T_{\text{required}} = 72\text{ hours}$ was created as a synthetic engineering test value for prototype fixture construction.
- **Status**: `SYNTHETIC_ENGINEERING_TEST_VALUE_ONLY` (`STATION_MEANING = NONE`).
- **Firewall**: 72h MUST NOT be cited as empirical evidence for Nuolja station or as the basis for the 6h baseline selection.

### Fact 2: 2-Hour Test Horizon Classification
- **Fact**: $T_{\text{test}} = 2\text{ hours}$ is a test-space value used solely for synthetic ECD logic validation.
- **Status**: `SYNTHETIC_ECD_LOGIC_VALIDATION_ONLY` (`STATION_MEANING = NONE`).

### Fact 3: 30 kW Critical Load Parameter
- **Fact**: $P_{\text{crit}} = 30\text{ kW}$ is an illustrative constant parameter used in research memos and synthetic test fixtures.
- **Status**: `SYNTHETIC_PROTOTYPE_PARAMETER`.

### Fact 4: Runtime Code Implementation Status
- **Fact**: Code audit verified zero lines of code in `system/` implementing ECD runtime integration, $T_{\text{required}}$ override handling, cryptographic MFA validation, or Option D safe-state fallback.
- **Status**: `NOT_IMPLEMENTED`.

### Fact 5: MILP Optimizer Penalty Formulation
- **Fact**: Current MILP optimizer employs a single scalar unmet-demand penalty of $10/\text{Wh}$. Multi-stage lexicographic objective enforcement is not implemented.
- **Status**: `NOT_IMPLEMENTED`.
