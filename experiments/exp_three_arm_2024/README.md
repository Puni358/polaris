# EXP-THREE-ARM-2024

The experiment package for the three-arm solar-forecast diagnostic (with the A-Fix and B diagnostics) on 2024 data.

**Status (2026-10-11, superseding the line below): the experiment has been executed and validated.** Run `results/run_20261011T143130Z/` completed all 14,760 solves and passed post-run validation; `winner: null`, no arm is promotion-eligible. (An earlier run, `results/run_20261011T075716Z/`, failed validation on a since-fixed telemetry-string bug and is preserved as historical evidence — see `CHANGELOG.md`.) **Start here for the completed-experiment outcome and analysis: `EXPERIMENT_KNOWLEDGE_BASE.md`.**

**Status as of the pre-execution freeze (2026-10-11, historical): calibrated (Arm C artifact `65732ccc…`); re-frozen after the D9 authorization boundary (schema v2); EXECUTION NOT AUTHORIZED; D8 re-confirmation open. No experiment, forecast replay, training or MILP solve has been run.** `--execute` refuses unless the `execution` section of `AUTHORIZATION_RECORD.json` (scope EXECUTE_EXPERIMENT) is signed and references the project lead's separate explicit execute instruction; a preflight-only signature (`execution_preflight`) never authorizes execution. See `reports/FINAL_READINESS_REVIEW.md`. **For the pre-execution governance process: `HANDOVER.md`** (status, blockers, decision ledger, next actions).

| File | What it is | Origin |
|---|---|---|
| EXPERIMENT_KNOWLEDGE_BASE.md | Entry point for the completed-run outcome: candidate register, gate results, mechanism, failure/limitation register, governance record, research backlog | New (post-execution, 2026-10-11) |
| reports/FORENSIC_INVESTIGATION_ARM_A_ARM_B_2026-10-11.md | Detailed read-only forensic analysis of Arm A's and Arm B's reported savings, referenced by the knowledge base | New (post-execution, 2026-10-11) |
| PREREGISTRATION.md | Preregistration; frozen 2026-10-11, §9 holds the PACKAGE_MANIFEST hash (outside the manifest) | New |
| AUTHORIZATION.md | Explanatory sheet only (the JSON record and the project lead's explicit instructions are authoritative) | New (supersedes `reports/source_prep/AUTHORIZATION_SHEET.md`) |
| DECISIONS_LOG.md | D1–D11, D7a and budget status, with evidence | New |
| HANDOVER.md | Authoritative handover after M9 (excluded from PACKAGE_MANIFEST because it records the manifest hash) | New (M9) |
| PROTOCOL_ADDENDUM_D7a_AMENDMENT_1.md | D10a amendment: Arm C label research-only candidate | New (M9) |
| CHANGELOG.md | What was created and changed, with reasons | New |
| DATA_PROVENANCE.md | Inputs, hashes, derivation, exclusions, rights | New |
| TIMESTAMP_VERIFICATION.md | D7 summary and test-backed geometry claims | New |
| DESIGN_AND_GATES.md | Arms, comparisons, gates, limits | New |
| COMPUTE_BUDGET.md | Solve accounting | New |
| scripts/causal_cloud_lookup.py | L1 lookahead fix | Extracted from `reports/source_prep/PROPOSED_PATCH.diff` (byte-for-byte content of the + lines) |
| scripts/solar_convention.py | A-Fix pvlib Location wrapper | Copy of `reports/source_prep/d7/PROPOSED_solar_convention.py` |
| scripts/timestamp_guards.py | Fail-closed input and timestamp guards | Copy of `reports/source_prep/d7/PROPOSED_timestamp_guards.py` (full decomposition hash filled before copying) |
| config/EXPERIMENT_CONFIG.json | Every execution-critical setting; `null` = unresolved; decision statuses mirror DECISIONS_LOG | New (frozen 2026-10-11, `frozen: true`) |
| AUTHORIZATION_RECORD.json | Machine-checked authorization record, schema v2: `calibration`, `execution_preflight` (PREFLIGHT_ONLY), `execution` (EXECUTE_EXPERIMENT), append-only `history` (never authorizes) | New |
| scripts/preflight.py | Fail-closed checks shared by the runner and calibration | New |
| scripts/run_three_arm_2024.py | Runner: `--audit-budget`, `--preflight`, `--execute` (no override) | New, never executed on evaluation data |
| scripts/calibrate_arm_c.py | Arm C calibration (refuses until calibration is authorized) | New, never run on real data |
| scripts/gates_three_arm.py | Post-run gate evaluation (refuses unresolved gate settings) | New |
| tests/ | Synthetic, static and integrity tests; every solver interface is mocked to fail if called | Two adapted from proposals (changes in CHANGELOG), the rest new |
| reports/CALIBRATION_AMBIGUITIES.md | Arm C protocol ambiguities left unresolved | New |
| reports/D7_VERIFICATION_REPORT.md | D7 report | Verbatim copy |
| reports/D7A_REVIEW.md, FINAL_READINESS_REVIEW.md | Reviews | New |
| reports/PREP_CHECKS_OUTPUT.txt | Exact output of the preparation checks | New (generated) |
| reports/source_prep/ | Earlier prep, audit and D7 files, kept as history | Verbatim copies |
| manifests/, PACKAGE_MANIFEST.sha256 | SHA-256 manifests | New (generated) |
| logs/, results/ | Empty; reserved for an authorized run | — (contain only an empty `.keep`) |

**Running the tests (preparation only, no solver)**, from the repo root with the project venv:

```
.venv/bin/python -m pytest -p no:cacheprovider -q -rA experiments/exp_three_arm_2024/tests
```

`test_input_integrity_2024.py` reads the four 2024 data files listed in DATA_PROVENANCE.md. `test_runner_three_arm.py::test_all_pinned_sources_byte_identical` hashes every pinned file. No test reads any 2025 file, and every test runs with `highspy.Highs` and the Planner-CF optimizer replaced by mocks that raise if called (`tests/conftest.py`).

**Commands that are safe now (no solver, no data contents):**

```
.venv/bin/python experiments/exp_three_arm_2024/scripts/run_three_arm_2024.py --repo . --audit-budget   # exit 0
.venv/bin/python experiments/exp_three_arm_2024/scripts/run_three_arm_2024.py --repo . --preflight      # exit 2 (BLOCKED)
```

`--execute` and `calibrate_arm_c.py` exit 2 while any decision is open or the authorization record is unsigned. They must not be run until the project lead has signed, and a passing preflight is not itself an authorization.

**Order once decisions are made (by the project lead, not by AI assistant):** record decisions and resolve every `null` in the config → set `frozen: true` → regenerate the manifests → write the freeze line in PREREGISTRATION.md → sign the `calibration` section → run calibration → sign the `execution` section with the artifact hash and the 14,760 ceiling → `--preflight` → `--execute`.
