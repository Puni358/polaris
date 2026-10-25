# OFFLINE DEPLOYMENT AUDIT

## Offline Operation, Licensing & Local Deployment

This document evaluates the offline deployment implications of Option A and Option B for the POLARIS EMS.

---

## Offline Deployment Evaluation

```text
OFFLINE_COMPATIBILITY_A = 100_PERCENT_OFFLINE_LOCAL
OFFLINE_COMPATIBILITY_B = 100_PERCENT_OFFLINE_LOCAL (Subject to local wheel availability)
```

---

## Factual Audit Findings

1. **Licensing**: Both SciPy (BSD 3-Clause) and HiGHS / `highspy` (MIT License) are open-source software packages that permit offline commercial and operational deployment without external license servers or cloud connections.
2. **Network Dependency**: Neither Option A nor Option B requires internet connectivity, cloud authentication, or remote solver execution during runtime.
3. **Local Deployment**: Option A uses pre-installed SciPy wheels already present in offline station images. Option B requires including the `highspy` wheel artifact in offline station deployment packages.
