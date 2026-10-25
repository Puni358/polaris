# Priority Mapping Audit

## Verified Source Priority Values

| POLARIS Objective | Physical Meaning | Source Code Assigned Priority | Required Lexicographic Priority |
| :--- | :--- | :---: | :---: |
| **J1** | Critical Deficit (Wh) | `4` | **1st (Highest)** |
| **J2** | EBR Reserve Shortfall (Wh) | `3` | **2nd** |
| **J3** | Diesel Fuel (Liters) | `2` | **3rd** |
| **J4** | Renewable Curtailment (Wh) | `1` | **4th (Lowest)** |

Under the verified HiGHS rule (`HIGHER_NUMBER_IS_HIGHER_PRIORITY`), assigning priorities $4, 3, 2, 1$ to $J_1, J_2, J_3, J_4$ enforces:

$$J_1 > J_2 > J_3 > J_4$$
