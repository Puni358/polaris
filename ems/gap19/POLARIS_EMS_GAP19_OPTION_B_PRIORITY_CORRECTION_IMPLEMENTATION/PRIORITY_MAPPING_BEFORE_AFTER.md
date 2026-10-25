# Priority Mapping Before vs After

| Objective Symbol | Objective Name | Physical Unit | Pre-Correction Priority | Pre-Correction Effective Order | Post-Correction Priority | Post-Correction Effective Order |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **$J_1$** | Critical Deficit | Wh | `1` | 4th (Lowest) | `4` | **1st (Highest)** |
| **$J_2$** | EBR Reserve Shortfall | Wh | `2` | 3rd | `3` | **2nd** |
| **$J_3$** | Diesel Fuel | Liters | `3` | 2nd | `2` | **3rd** |
| **$J_4$** | Curtailment | Wh | `4` | 1st (Highest) | `1` | **4th (Lowest)** |

## Summary
- Pre-Correction Effective Order: $J_4 > J_3 > J_2 > J_1$ (Reverse order)
- Post-Correction Effective Order: $J_1 > J_2 > J_3 > J_4$ (Correct governed order)
