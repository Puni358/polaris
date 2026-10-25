# Stage8.19 Clean Revalidation Plan

## Objective
Conduct a clean revalidation of Stage8.19 (ABIS ZTD + AROME disagreement features) on the locked 173 ODD test set using only real surviving input artifacts.

## Governance & Anti-Failure Constraints
1. **Rule 1 & 12:** NEVER hardcode metrics into evaluation scripts or import metric variables.
2. **Rule 5:** Synthetic data (e.g. `np.random.seed(819)` / `np.random.seed(817)`) can NEVER be used to claim real-model improvement.
3. **Rule 10 & 11:** Metrics must be independently verified by loading prediction CSVs from disk.

## Pre-Conditions & Input Lineage Verification
1. Real raw ABIS GNSS ZTD observation files: **MISSING**
2. Real raw AROME-Arctic NWP data: **MISSING**
3. Stage8.19 Feature Matrix: **MISSING (Only synthetic generator script exists)**

## Execution Decision
Because real ABIS and real AROME inputs are missing, and synthetic generation is strictly prohibited:
**STATUS: STAGE8.19 = NOT RECONSTRUCTABLE**
Clean revalidation is aborted.
