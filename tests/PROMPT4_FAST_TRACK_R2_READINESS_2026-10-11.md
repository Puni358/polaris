# POLARIS — Prompt 4: Fast-Track R2 and New Experiment Readiness (READ-ONLY)

No experiment executed. No authorization created, signed, or consumed. Nothing in
`experiments/exp_three_arm_2024/` modified. Saved outside the frozen package for the same reason
as the Prompt 3 report (see that report's "Report destination" note): `experiments/exp_three_arm_2024/reports/`
is manifest-tracked, and no top-level `reports/` convention exists for the frozen Planner module.

## 1. Preserved state — fresh hashes, all match every previously recorded value

| Artifact | SHA-256 |
|---|---|
| `PACKAGE_MANIFEST.sha256` | `8c09074c4f202356c6a9ee8725de58bc75a8cd3224bb9e97051e3522e978a58c` |
| `manifests/CODE.sha256` | `2cc1bcb794e8f77029ffc62eeff06863ee3078bde61ad18ffad991694d1daa2b` |
| `config/EXPERIMENT_CONFIG.json` | `9d41e3f4bd608aec5b0f9d970275c693cd7608d86ec2d5ebda37533b3d808157` |
| `calibration/ARM_C_CALIBRATION.json` | `0fd914dd7770890f23a97782164204e7a76ef1cbacbe1b6e7c53c6b38d3d70e0` |
| `scripts/run_three_arm_2024.py` | `aba1bb97b53f7e4509f5bacfbdfb87b8ed0bdde2b44696a2aae671712b798c16` |
| Frozen Planner module | `a8dd9fc7d84e3d2344ba4f99ba1b1cd0ec2165a83d8f7af438b69f8178815093` |
| `AUTHORIZATION_RECORD.json` | `bbfb1489074326f6d10c3d2aad4b197e7cb36a120d1d891bc19788a24e211b63` |
| `results/run_20261011T075716Z/RUN_STATUS.json` | `d232f51c37e595323627402951f0a74eaf8b897a9cb0fa6817491c99e67a1afa` |
| `.../HOURLY_TELEMETRY.csv` (md5) | `9c41bb1d599fac7a9db36ddb0b7072fd` |
| `.../EXECUTED_HOUR_TELEMETRY.csv` (md5) | `1daa469c2a45cf93dfe4eef08cd1cc29` |

No mismatch; nothing silently repaired.

## 2. R2 — bounded cross-environment check: BLOCKED (no second environment available)

Checked, without installing anything:
- `/usr/bin/python3.11` exists on this machine but has no `highspy` installed (`ModuleNotFoundError`).
- `/usr/bin/python3` is 3.12.3 (same major version as the device venv) and also has no `highspy`.
- `pip cache list highspy` → no cached wheels of any version.
- `pip index versions highspy` → PyPI is reachable and lists other versions (1.15.0, 1.14.0, 1.13.1, ...), but obtaining any of them requires installing a new package, which this prompt explicitly prohibits ("Do not install or upgrade dependencies").

**No suitable second environment is readily available with minimal effort.** Per your explicit time-box instruction, cross-environment work stops here. **R2 status: BLOCKED (not compared), not "not mandatory," not "resolved."** This is the same conclusion as Prompt 3's report, now confirmed by an actual environment search rather than inference.

## 3. Is R2 a mandatory execution-blocking gate?

Checked directly: `preflight.py`'s `CALIBRATION_DECISIONS`/`EXECUTION_DECISIONS` tuples and every
decision entry in `config/EXPERIMENT_CONFIG.json` were re-inspected — **no decision, gate, or
preflight check anywhere in this codebase references cross-environment solver reproducibility,
"R2," or any equivalent requirement.** R1–R5 do not exist as named entities in any repository
document (confirmed repeatedly across this entire process) — they are risk labels carried in
conversation context, not governance-coded requirements.

**Conclusion: cross-environment solver equivalence is not an explicit, code-enforced, or
preregistration-mandated precondition for execution.** It is a genuine, documented *limitation*
(no second environment has ever existed to test against) that should be disclosed, not a gate
that blocks signing. This is not a downgrade of a requirement — no such requirement was ever
written down; I am reporting its absence, not waiving it.

## 4. Minimum essential readiness checks — results

```
check_package_manifest(repo)                    -> []
check_preregistration_frozen(repo)               -> []
check_decisions(cfg, EXECUTION_DECISIONS)         -> []
check_decisions(cfg, CALIBRATION_DECISIONS)       -> []
check_gates(cfg)                                  -> []
check_hashes(repo, cfg)                           -> []
check_calibration_authorization(repo, cfg, art)   -> []   (passes against the refreshed artifact)
check_authorization(repo, cfg, "execution", art_sha) -> [
  'execution package_manifest_sha256 does not match the current manifest',
  'execution experiment_config_sha256 does not match the current config',
  'execution calibration_artifact_sha256 does not match the calibration artifact',
  "execution execute_instruction_ref has already been consumed by run_20261011T075716Z (status 'FAILED'); ..."
]
```
**The old `execution` section is correctly and completely rejected** — stale on all three hash bindings *and* consumed. `_execution_history(repo)` enumerated: exactly one consumed reference (the original), zero ambiguous evidence — the single-use guard is intact and functioning.

**Solver-status serialization/validator compatibility:** already fixed and tested (Prompt 1's fix + its regression tests, part of the 396-passed suite re-confirmed via unchanged hashes above) — not re-run here, no concrete reason to repeat it.

**All execution-bound hashes computable and recorded:** yes, table in §1. **No artifact missing or ambiguous.**

## 5. R1 status (retained verbatim, not re-opened)

`R1 EVIDENCE IMPROVED — TARGETED RELATIONSHIPS VERIFIED; REMAINING GAPS DOCUMENTED`

## 6. R3 and R4 — mandatory gate check

Grepped `preflight.py` and `config/EXPERIMENT_CONFIG.json` for `timeout`, `time_limit`,
`interruption` — **zero matches.** Same conclusion as R2: no mandatory, code-enforced, or
preregistration-written requirement exists for solver timeouts or interruption/recovery. Both
remain real, documented residual risks (no `time_limit` HiGHS option is ever set; no
checkpoint/resume mechanism exists — both independently confirmed by direct code reading in
Prompt 1), but neither is a governance gate. Not implemented here, per your instruction.

## 7. Summary

1. **R2 outcome:** **BLOCKED** — no second real-solver environment available without installing a new dependency, which this prompt prohibits. Not compared. Not mandatory per governance (§3).
2. **Readiness checks:** all pass except the (correctly) rejected old `execution` section — see §4 for exact commands/output.
3. **Current hashes:** table in §1.
4. **Mandatory unresolved blockers:** none found in governance/code. The only hard requirement before any new run is a *fresh* `execution` signature — which this prompt does not create.
5. **Known, non-mandatory limitations:** R2 (no cross-environment solver comparison ever performed), R3 (no solver timeout configured), R4 (no interruption/resume mechanism) — all previously documented, re-confirmed here, not newly discovered.
6. **Smallest remaining actions before a fresh execution authorization:** (a) your explicit decision to accept R2/R3/R4 as documented limitations rather than requiring remediation, and (b) your actual, explicit execute instruction, from which a new `execute_instruction_ref`, signer, and timestamp would be honestly derived — nothing else is technically blocking.
7. No experiment execution occurred. No authorization was created, signed, or consumed. No frozen file was modified.
