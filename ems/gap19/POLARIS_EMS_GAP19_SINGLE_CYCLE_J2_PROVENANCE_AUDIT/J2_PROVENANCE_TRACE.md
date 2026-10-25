# J2 Numerical Target Provenance Trace

## Target 1: EBR Target = 56,000 Wh
- **Source File 1:** `system/optimization/implementations/gap19_highs_native.py` (Line 86)
  `ebr_target_wh = float(config.get("ebr_target_wh", min_e_wh + 0.1 * (max_e_wh - min_e_wh)))`
- **Source File 2:** `scratch/execute_controlled_single_cycle_test.py` (Line 87)
  `"ebr_target_wh": 56000.0` (Comment: `min_soc (40,000) + 10% of 160,000 = 56,000 Wh`)
- **Artifact:** `POLARIS_EMS_GAP19_CONTROLLED_SINGLE_CYCLE_RUNTIME_TEST/INPUT_MANIFEST.json`
- **Classification:** `C = NEW TEST-HARNESS VALUE`

## Target 2: Terminal Reserve Target = 160,000 Wh
- **Source File 1:** `system/optimization/implementations/gap19_highs_native.py` (Line 87)
  `terminal_target_wh = float(config.get("terminal_target_wh", initial_e_wh))`
- **Source File 2:** `scratch/execute_controlled_single_cycle_test.py` (Line 88)
  `"terminal_target_wh": 160000.0` (Comment: `initial_e_wh = 160,000 Wh` at 80% SOC)
- **Artifact:** `POLARIS_EMS_GAP19_CONTROLLED_SINGLE_CYCLE_RUNTIME_TEST/INPUT_MANIFEST.json`
- **Classification:** `C = NEW TEST-HARNESS VALUE`
