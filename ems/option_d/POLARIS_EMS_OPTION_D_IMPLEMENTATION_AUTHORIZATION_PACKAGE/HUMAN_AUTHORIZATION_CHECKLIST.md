# HUMAN AUTHORIZATION CHECKLIST

## Multi-Tier Governance, Implementation, and Execution Sign-off Matrix

This checklist defines the formal human authorization gates for Option D implementation.

> [!CAUTION]
> **SIGN-OFF STATUS**:
> Governance items already sealed in prior reviews are marked checked `[x]`.
> All implementation and execution authorization boxes remain unchecked `[ ]`.
> **Coding or runtime execution must not commence until human authorities explicitly sign off.**

---

## 1. Governance Already Sealed

- [x] **DEC-004**: Option D — Protected Critical Load Fallback selected.
- [x] **D1**: Station-defined protected critical equipment and dynamic minimum requirements $P_{i,\text{min}}(t)$.
- [x] **D2**: Battery discharge restricted strictly to protected critical load during Option D.
- [x] **D3**: Renewable + Diesel insufficient $\rightarrow$ battery supports protected critical load until minimum SOC.
- [x] **D4**: Critical load allocation basis sealed as `PROPORTIONAL_TO_MINIMUM_VIABLE_CRITICAL_REQUIREMENTS` ($P_{i,\text{served}} = \alpha P_{i,\text{min}}$).
- [x] **D5**: Dual escalation triggers sealed (Time boundary OR resource survivability boundary).
- [x] **D6**: Diesel excess $\rightarrow$ battery charging $\rightarrow$ curtailment; no diesel start solely to charge battery.
- [x] **$T_{\text{required}}$ Baseline**: Baseline sealed as $6.0\text{ hours}$ (`PROTECTED_CRITICAL_SERVICE_SURVIVABILITY_DURATION`, Hybrid config, MFA gate).

---

## 2. Governance & Engineering Inputs Still Open

- [ ] Operator escalation quantitative time threshold (hours).
- [ ] Operator escalation quantitative resource volume threshold (Liters fuel).
- [ ] System recovery clearance policy (Automatic vs manual operator sign-off).
- [ ] Real Nuolja station critical equipment inventory and circuit mapping.
- [ ] Real station dynamic minimum viable load vectors $P_{i,\text{min}}(t)$.
- [ ] Real generator fuel consumption maps and operating limits.
- [ ] Real battery thermal limits and usable SOC range.
- [ ] Production security parameters (cryptographic keys, telemetry freshness thresholds).

---

## 3. Pre-GAP19 Implementation Scope Authorization

- [ ] Additive schema extensions (`state.py`, `forecast.py`, `dispatch.py`).
- [ ] `SyntheticFixtureProvider` interface adapter.
- [ ] ECD runtime wiring in `runner.py`.
- [ ] `OptionDPolicyLayer` and `ModeConstraintSet` implementation.
- [ ] 21-variable scalar MILP linear constraint formulation in `milp.py`.
- `UNKNOWN_INVALID` safe-state routing path.
- [ ] Additive `DispatchPlan` reporting fields.
- [ ] Synthetic test harness implementation.

---

## 4. Execution Authorization Gates

- [ ] **Gate 0**: Static contract verification execution.
- [ ] **Gate 1**: Synthetic fixture adapter test execution.
- [ ] **Gate 2**: ECD interface integration test execution.
- [ ] **Gate 3**: `OperatingMode` & policy layer test execution.
- [ ] **Gate 4**: D4 proportional allocation math test execution.
- [ ] **Gate 5**: D6 excess charging test execution.
- [ ] **Gate 6**: `UNKNOWN_INVALID` routing test execution.
- [ ] **Gate 7**: Normal mode regression test execution.
- [ ] **Gate 8**: Single synthetic scenario execution (SC-01).
- [ ] **Gate 9**: All five synthetic scenarios execution (SC-01 to SC-05).
- [ ] **Gate 10**: 24h closed-loop synthetic demonstration execution.
