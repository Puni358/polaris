# Review Note — Candidate F Successor 18Z Feature Contract v2

**Date:** 2026-10-12. **Purpose:** a short, separate note for the project lead's explicit approval decision on `CANDIDATE_F_SUCCESSOR_18Z_FEATURE_CONTRACT_v2.md`. **This note does not itself approve anything** — approval must come from the project lead, explicitly, separately.

## v2 contract file and hash

- File: `CANDIDATE_F_SUCCESSOR_18Z_FEATURE_CONTRACT_v2.md`
- SHA-256: `98e5ce3a721eb3d0064412d9ce2cbdebb2f8bc59bad368f141c838feebc7a05f`
- v1 (unchanged, re-verified byte-identical before writing v2): `CANDIDATE_F_SUCCESSOR_18Z_FEATURE_CONTRACT_v1.md`, SHA-256 `e17764fc6dcbda2eb39625edec385e13b7a954c9ccbeb66a113426e4a5853c60`

## What v2 changes, in one sentence

Corrects the source lead-time mapping from `lead=6+h` (v1, one hour too late) to `lead=5+h` (v2), so that base `horizon_hour=h` is valid at `origin+(h−1)` — matching the base feature matrix's own, now-empirically-confirmed timestamp convention — and specifies that horizon 1 requires a new lead-6 record not present in the existing cache.

## Approval checklist (for the project lead to check off, not pre-filled here)

- [ ] The lead-mapping correction (§2: `lead=5+h`) is understood and agreed to be the correct target, based on the three independent live spot-checks already reported.
- [ ] The horizon-1 coverage gap (§3: base `h=1` has no existing cache record and requires a new lead-6 fetch) is understood and accepted as the consequence of this correction.
- [ ] No other element of the contract (variables, pressure level, units, key conventions, missing-value handling, §4–§6) is intended to change, and none does.
- [ ] `CANDIDATE_F_SUCCESSOR_18Z_FEATURE_CONTRACT_v1.md` is to remain in place, unchanged, as historical record — confirmed untouched (hash re-verified above).
- [ ] The unresolved historical publication-time availability limitation (§8) is acknowledged as still open and not resolved by this contract.
- [ ] Approval of v2 **does not** itself authorize the Phase 2 lead-6 acquisition or the Phase 3 dataset build — those remain separate authorizations per the governing task.

## Inconsistencies discovered while preparing v2

**None.** The arithmetic (§9 of the v2 document) was checked against the live fetcher code, a representative cache record, the acquisition manifest, and the clean-split protocol, and all are mutually consistent with the proposed correction.

## Status

Acquisition has **not** started. Dataset construction has **not** started. No code has been changed. No network request was made while preparing this contract or this review note. `winner: null` and all frozen artifacts, original caches, source matrices, models, published metrics, and prior reports are unchanged.
