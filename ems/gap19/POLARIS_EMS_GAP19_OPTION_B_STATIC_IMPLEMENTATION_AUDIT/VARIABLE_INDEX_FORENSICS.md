# Variable Index Forensics

The 409 variables are indexed strictly without overlap, gap, or off-by-one errors:

| Index Range | Count | Type | Variable Name | Timestep / Index |
| :--- | :---: | :---: | :--- | :--- |
| `0 .. 359` | 360 | Mixed (264 Cont, 96 Bin) | Base Production Variables ($15 	imes 24$) | $t=0..23$ |
| `360 .. 383` | 24 | Continuous ($\ge 0$) | $P_{\text{unmet,critical}}[t]$ | $t=0..23$ |
| `384 .. 407` | 24 | Continuous ($\ge 0$) | $s_{\text{EBR}}[t]$ | $t=0..23$ |
| `408` | 1 | Continuous ($\ge 0$) | $s_{\text{terminal}}$ | Final step $t=23$ |

Total Variables: $360 + 24 + 24 + 1 = 409$.

`VARIABLE_INDEXING = PASS`
