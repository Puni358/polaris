# J2 Indexing Audit

The reserve shortfall constraints link battery state $E_{\text{next}}[t]$ (index `base + 6`) to reserve targets:
1. Hourly EBR Slack: $E_{\text{next}}[t] + s_{\text{EBR}}[t] \ge E_{\text{EBR\_target}}[t]$ for $t=0..23$.
2. Terminal Reserve Slack: $E_{\text{next}}[23] + s_{\text{terminal}} \ge E_{\text{terminal\_target}}$.

No index collision, off-by-one, or double counting with initial SOC exists.

`J2_INDEXING = PASS`
