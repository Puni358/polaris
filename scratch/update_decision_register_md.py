import re

def update_markdown(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Date line (line 3)
    addition = (
        " — **amended a twenty-first time 2026-10-19** (RT-01 final owner authorization, fuel policy approval, "
        "Option D hash-transition ratification with provenance caveat, and formal RT-01 closure: Project Owner approved fuel policy "
        "(100 L hard limit governs Layer 1 physical tank depletion, 81.7166 L consumed, 18.2834 L remaining; Layer 2 evaluator surcharge "
        "of 99.72 L is economic metric), ratified patched Option D hash 688e3a7d41fe558726843ba6f70837c03fc67c3c7ba99f800e509e7ebc7929f3 "
        "with provenance caveat that historical source hash 022cc6a0... is unrecoverable, and authorized RT-01 closure subject to governing rules; "
        "all 5 named RT-01 tests passed (5/5, exit 0), 6/6 boundary tests passed (exit 0), 518/518 system tests passed (exit 0); "
        "RT-01 formally CLOSED with evidence; see **Section 37**)"
    )
    # Target the end of the Date paragraph before the closing parenthesis
    content = content.replace(
        "see **Section 36** and companion report `ems/reports/rt01_runtime_fixes/RT01_OWNER_DECISIONS_GOVERNANCE_REPORT.md`)",
        "see **Section 36** and companion report `ems/reports/rt01_runtime_fixes/RT01_OWNER_DECISIONS_GOVERNANCE_REPORT.md`)" + addition
    )

    # 2. Update version in companion file line
    content = content.replace(
        "docs/decision_registers/POLARIS_MASTER_DECISION_REGISTER.json` (machine-readable, same IDs, now at version `1.9.7`)",
        "docs/decision_registers/POLARIS_MASTER_DECISION_REGISTER.json` (machine-readable, same IDs, now at version `1.9.11`)"
    )

    # 3. Update RT-01 in Section 2 table (line 94)
    old_row = "| RT-01 | Authorize investigation of **5** (corrected from 3) pre-existing conservation-residual test failures | Runtime/tests | D | **decided 2026-10-17: retain diagnostic, defer protected fix** (§14); diesel-floor mechanism (a′) implemented+verified at unit level 2026-10-18, **item remains open at full-system level** — blocked by unrelated router.py defect (§30); closure_test field's own wording reconciled to the 5-test scope 2026-10-18 (§33), `current_state` unchanged | production_promotion |"
    new_row = "| RT-01 | Authorize investigation of **5** (corrected from 3) pre-existing conservation-residual test failures | Runtime/tests | D | **RESOLVED_WITH_EVIDENCE / CLOSED 2026-10-19** (§37); all 5 named closure tests passed (5/5), 6/6 boundary tests passed, 518/518 full system suite passed; fuel policy approved (100 L physical limit); Option D hash ratified to `688e3a7d41...` with provenance caveat; `current_state: resolved_with_evidence` | production_promotion |"
    content = content.replace(old_row, new_row)

    # 4. Append Section 37 at the end
    section_37 = """

---

## 37. POLARIS RT-01 — Final Owner Authorization and Governance Closure — 2026-10-19 (Twenty-First Pass)

This is a twenty-first, decisive governance pass, recording the Project Owner's explicit final authorizations and closing item **RT-01** under its governing closure rules.

### 37.1 Three Explicit Owner Decisions Recorded

1. **Fuel-Limit Policy: APPROVED.**
   - The synthetic 100 L hard limit (`initial_fuel_l = 100.0`) governs Layer 1 physical tank depletion.
   - Measured Layer 1 physical fuel consumption across the 168-hour endurance simulation is **81.7166 L**, leaving **18.2834 L** in the physical tank at completion. Zero fuel exhaustion occurred.
   - The evaluator's startup surcharge (Layer 2: **99.72 L** total, incorporating 18.0 L of economic startup penalties across 3 engine starts) remains a separate economic accounting metric and must NOT be represented as physical fuel depletion.

2. **Option D Hash-Transition Ratification: APPROVED WITH PROVENANCE CAVEAT.**
   - Patched `system/optimization/implementations/option_d.py` SHA-256: `688e3a7d41fe558726843ba6f70837c03fc67c3c7ba99f800e509e7ebc7929f3` is formally ratified as the operational baseline.
   - Supported by the completed acceptance package: pre-patch high-SOC/low-demand bus-bar balance defect (+6,000 W at 95% SOC, +3,826.09 W at 94% SOC) is eliminated to 0.0000 W maximum residual.
   - **Provenance Caveat Recorded:** The authentic historical baseline source code corresponding to hash `022cc6a0aef4e61772a7274ef3b0e772abacf16fab373feb3273d6af0f653771` remains unrecoverable from Git or local filesystem history. No authentic historical source-level A/B comparison is claimed or reconstructible.

3. **RT-01 Closure: AUTHORIZED AND SATISFIED UNDER GOVERNING RULES.**
   - Governing closure standard: all 5 named tests in `system/tests/test_offline_runtime.py` pass.
   - Verified acceptance test evidence:
     * **5/5 Governed RT-01 Closure Tests Passed** (`system/tests/test_offline_runtime.py`, 56.52s, exit code 0):
       1. `test_flexible_load_constraints`
       2. `test_flexible_load_no_double_counting`
       3. `test_per_timestep_conservation_audit`
       4. `test_cumulative_physical_conservation_168h`
       5. `test_long_duration_closed_loop_endurance_168h`
     * **6/6 Boundary Regression Tests Passed** (`system/tests/test_option_d_boundary.py`, 0.13s, exit code 0).
     * **518/518 Full System Test Suite Passed** (`system/tests/`, 1434.44s / 23m 54s, exit code 0).
     * **168-Hour Simulation Metrics Verified:**
       - Completed timesteps: 168 / 168
       - System reliability: 100.0%
       - Total unmet load: 0.0 Wh
       - Renewable utilization: 79.98% (curtailment: 1372.68 kWh)
       - Maximum executed H1 bus-bar residual: 0.000000 W (step 19)
       - Battery SOC range: [20.0%, 95.0%] (strictly bounded within limits)
       - Physical fuel consumed (Layer 1): 81.7166 L (18.2834 L remaining)
       - Evaluator economic fuel (Layer 2): 99.72 L
       - Optimizer/runner faults: 0
   - **Verdict:** RT-01 is formally **CLOSED**. Register `current_state` transitioned from `decided` to `resolved_with_evidence`.

### 37.2 Protected-File Hash Verification

All 6 `PROTECTED_FILES` entries and `manifest.py` verified:
- `system/optimization/implementations/gap19_highs_native.py`: `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` (MATCH)
- `system/optimization/implementations/option_d.py`: `688e3a7d41fe558726843ba6f70837c03fc67c3c7ba99f800e509e7ebc7929f3` (RATIFIED OPERATIONAL BASELINE)
- `system/control/ecd.py`: `091358c08b9460e0e9a802ff149c2b54ce1d8036bc2d6eed0f4c1fd9e41c96db` (MATCH)
- `system/control/router.py`: `b2a46bc5bd8c619b5eca9b020daa3dd1b4571214bab47cfe17587bc9074e90f3` (MATCH)
- `system/simulation/simulator.py`: `8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f` (MATCH)
- `system/runtime/runner.py`: `6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10` (MATCH)
- `system/orchestration/manifest.py`: `7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35` (MATCH)

### 37.3 Preservation of Safety & Governance Boundaries

- `winner: null` preserved untouched.
- `CampaignExecutionNotAuthorizedError` guard preserved untouched.
- `DSL-01` `epsilon_tol` remains unset.
- Sealed 2025 blind data: NOT accessed.
- Frozen Stage 8.1 / N6 assets: NOT modified.
- Zero Git mutations performed.

### 37.4 Register Impact

- `docs/decision_registers/POLARIS_MASTER_DECISION_REGISTER.md` / `.json`: v1.9.10 -> v1.9.11.
- `RT-01.current_state`: `decided` -> `resolved_with_evidence` (**CLOSED**).
- `RT-01.owner_decision_record`: `implementation_authorized=true`, `implementation_completed=true`, `evidence_verified=true`.
- Mirrored to `forecasting/n6/remediation_reports/POLARIS_MASTER_DECISION_REGISTER.md` and `forecasting/n6/remediation_reports/POLARIS_MASTER_DECISION_REGISTER.json`.

**PASS COMPLETE — RT-01 FORMALLY CLOSED WITH VERIFIED EVIDENCE; FUEL POLICY (100 L PHYSICAL) APPROVED; OPTION D BASELINE HASH RATIFIED WITH PROVENANCE CAVEAT; ALL BOUNDARY & GOVERNANCE CONSTRAINTS MAINTAINED.**
"""
    content = content + section_37

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {md_path} successfully.")

if __name__ == '__main__':
    update_markdown('docs/decision_registers/POLARIS_MASTER_DECISION_REGISTER.md')
    update_markdown('forecasting/n6/remediation_reports/POLARIS_MASTER_DECISION_REGISTER.md')
