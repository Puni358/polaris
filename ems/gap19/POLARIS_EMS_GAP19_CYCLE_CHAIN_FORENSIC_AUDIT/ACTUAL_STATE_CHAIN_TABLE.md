# Actual State Chain Reconstruction Table (`ACTUAL_STATE_CHAIN_TABLE.md`)

**FORENSIC AUDIT**: POLARIS EMS GAP19 — Cycle-Chain State Reconciliation Audit  
**SCOPE**: Read-Only Forensic Audit of `POLARIS_EMS_GAP19_CONTROLLED_DIGITAL_TWIN_8_CYCLE_TEST`  
**VERDICT**: `STATE_CHAIN_EXACT_MATCH = PASS`

---

## 1. Reconstructed Actual State Propagation Chain

| Cycle | Input Timestamp | Input Energy (Wh) | Input SOC (%) | Committed $P_{\text{chg}}$ (W) | Committed $P_{\text{dis}}$ (W) | Committed $P_{\text{diesel}}$ (W) | Output Timestamp | Output Energy (Wh) | Output SOC (%) | Output Diesel Running | Output Diesel Hours | Linkage Match |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | `2024-01-01T20:00:00Z` | 160000.00 | 80.00% | 29064.27 | 0.00 | 44064.27 | `2024-01-01T21:00:00Z` | 186739.13 | 93.37% | `True` | 1.0h | `PASS` |
| **2** | `2024-01-01T21:00:00Z` | 186739.13 | 93.37% | 0.00 | 0.00 | 15000.00 | `2024-01-01T22:00:00Z` | 186739.13 | 93.37% | `True` | 2.0h | `PASS` |
| **3** | `2024-01-01T22:00:00Z` | 186739.13 | 93.37% | 0.00 | 0.00 | 15000.00 | `2024-01-01T23:00:00Z` | 186739.13 | 93.37% | `True` | 3.0h | `PASS` |
| **4** | `2024-01-01T23:00:00Z` | 186739.13 | 93.37% | 0.00 | 0.00 | 15000.00 | `2024-01-02T00:00:00Z` | 186739.13 | 93.37% | `True` | 4.0h | `PASS` |
| **5** | `2024-01-02T00:00:00Z` | 186739.13 | 93.37% | 0.00 | 0.00 | 15000.00 | `2024-01-02T01:00:00Z` | 186739.13 | 93.37% | `True` | 5.0h | `PASS` |
| **6** | `2024-01-02T01:00:00Z` | 186739.13 | 93.37% | 0.00 | 0.00 | 15000.00 | `2024-01-02T02:00:00Z` | 186739.13 | 93.37% | `True` | 6.0h | `PASS` |
| **7** | `2024-01-02T02:00:00Z` | 186739.13 | 93.37% | 0.00 | 0.00 | 15000.00 | `2024-01-02T03:00:00Z` | 186739.13 | 93.37% | `True` | 7.0h | `PASS` |
| **8** | `2024-01-02T03:00:00Z` | 186739.13 | 93.37% | 0.00 | 0.00 | 15000.00 | `2024-01-02T04:00:00Z` | 186739.13 | 93.37% | `True` | 8.0h | `PASS` |

---

## 2. Chain Linkage Proof ($N = 1 \dots 7$)

For every transition $N \to N+1$:
- $\text{StationState}_{N+1}.\text{timestamp} \equiv \text{DigitalTwinOutput}_N.\text{timestamp}$
- $\text{StationState}_{N+1}.\text{battery\_energy\_wh} \equiv \text{DigitalTwinOutput}_N.\text{battery\_energy\_wh}$
- $\text{StationState}_{N+1}.\text{battery\_soc\_pct} \equiv \text{DigitalTwinOutput}_N.\text{battery\_soc\_pct}$
- $\text{StationState}_{N+1}.\text{diesel\_running} \equiv \text{DigitalTwinOutput}_N.\text{diesel\_running}$
- $\text{StationState}_{N+1}.\text{diesel\_hours\_running} \equiv \text{DigitalTwinOutput}_N.\text{diesel\_hours\_running}$

```text
STATE_CHAIN_EXACT_MATCH = PASS
BROKEN_TRANSITIONS = ZERO
```
