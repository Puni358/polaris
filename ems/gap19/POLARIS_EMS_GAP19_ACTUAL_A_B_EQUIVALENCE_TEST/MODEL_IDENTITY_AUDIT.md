# MODEL IDENTITY AUDIT

## CANONICAL REPRESENTATION AND HASH IDENTITY VERIFICATION

The exact canonical representation of the POLARIS MILP instance passed to Option A and Option B was hashed using SHA-256.

```text
MODEL_A_HASH = 9c740dc5de2a0cf28e17748dd12466e7f5ca00e733b93cfb34b148c60cfc779c
MODEL_B_HASH = 9c740dc5de2a0cf28e17748dd12466e7f5ca00e733b93cfb34b148c60cfc779c
MODEL_A_HASH == MODEL_B_HASH -> TRUE
```

- Same variable count ($N=385$)
- Same constraint count ($M=265$)
- Same variable ordering
- Same constraint matrix $A$ and bounds $(l, u)$
- Same objective vectors $c_1, c_2, c_3, c_4$

`MODEL_IDENTITY_A_B` = `PASS`
