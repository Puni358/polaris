# J2 Pointwise Maximum Envelope Forensics

## 1. Executable Implementation Inspection

In `system/optimization/implementations/gap19_highs_native.py` (lines 147–151):

```python
e_stage2_target = [0.0] * 24
for t in range(23):
    e_stage2_target[t] = ebr_target_wh_list[t]
# Horizon edge (t=23): pointwise maximum envelope of EBR and Terminal Reserve
e_stage2_target[23] = max(ebr_target_wh_list[23], terminal_target_wh)
```

---

## 2. Quantitative Proof

- At $t=23$:
  - $E_{\text{EBR,target}}[23] = 21,739.13\text{ Wh}$
  - $E_{\text{term,target}} = 100,000.00\text{ Wh}$
  - $e\_stage2\_target[23] = \max(21,739.13, 100,000.00) = \mathbf{100,000.00\text{ Wh}}$
- Confirms the implementation did **NOT** calculate $21,739.13 + 100,000 = 121,739.13\text{ Wh}$.

---

## 3. Verdict

```
POINTWISE_MAX_ENVELOPE_VERIFIED = YES
ADDITIVE_SUM_REJECTED = CONFIRMED
J2_ENVELOPE_FORENSICS_STATUS = PASS
```
