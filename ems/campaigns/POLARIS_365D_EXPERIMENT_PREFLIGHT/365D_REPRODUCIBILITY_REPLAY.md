# 365D REPRODUCIBILITY & REPLAY AUDIT SPECIFICATION

## Independent Replay Protocol
After campaign completion, an independent verification replay (`--verify <RUN_ID>`) is executed:
1. Loads `RUN_MANIFEST.json` and verifies protected component hashes.
2. Loads all 4 cell trajectory records.
3. Re-runs optimization and simulation on a 500-cycle sample.
4. Asserts 100% bitwise identity between saved records and replayed results:
   $$\text{Records}_{saved} \equiv \text{Records}_{replayed}$$

## Bitwise Pass Requirement
If any dispatch power, SOC %, or fuel Liter value differs by $> 10^{-6}$, the replay audit fails (`REPRODUCIBILITY_REPLAY_FAILED`).
