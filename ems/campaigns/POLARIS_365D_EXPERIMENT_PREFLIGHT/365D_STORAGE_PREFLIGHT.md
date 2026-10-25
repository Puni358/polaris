# 365D STORAGE & DISK CAPACITY PREFLIGHT

## Storage Budget Estimation

| Artifact Category | Format | Estimated Size per Cell | Total Size (4 Cells) |
| :--- | :--- | :--- | :--- |
| **Trajectory Records** | JSON | ~3.5 MB | ~14.0 MB |
| **Checkpoints** (17 per cell) | JSON | ~120 KB | ~2.0 MB |
| **Worker Logs** | Text | ~500 KB | ~2.0 MB |
| **Master & Resource Logs** | Text / CSV | ~300 KB | ~300 KB |
| **Final Aggregated Results** | JSON / MD | ~50 KB | ~50 KB |
| **Total Campaign Storage** | — | **~4.5 MB** | **~18.35 MB** |

## Disk Preflight Gate
- Available Disk Space: **240.19 GB**
- Required Storage Budget: **~18.35 MB**
- Safety Margin Ratio: $> 10,000	imes$ free space margin.
- Storage Gate Status: **PASSED / CLEARED**.
