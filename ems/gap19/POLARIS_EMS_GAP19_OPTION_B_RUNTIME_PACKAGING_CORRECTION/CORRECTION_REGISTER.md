# Correction Register

| Audit Item | Previous Terminology / State | Corrected Terminology / State | Governance Purpose |
| :--- | :--- | :--- | :--- |
| **Main POLARIS HiGHS** | `MAIN_POLARIS_HIGHS_VERSION = NONE` | `MAIN_POLARIS_STANDALONE_HIGHSPY = NOT_INSTALLED`<br>`MAIN_POLARIS_BUNDLED_HIGHS = 1.12.0` | Distinguish standalone module from SciPy's bundled C++ HiGHS runtime |
| **highspy Dependency** | Implied installed | `PROPOSED_PACKAGING_CHANGE = highspy==1.15.1`<br>`PACKAGING_CHANGE_STATUS = PROPOSED_ONLY` | Clarify dependency addition is proposed, not installed |
| **Main Environment Change** | `MAIN_ENV_CHANGE_REQUIRED = YES` | `MAIN_ENVIRONMENT_CHANGE_REQUIRED = YES`<br>`MAIN_ENVIRONMENT_CHANGE_PERFORMED = NO` | Distinguish requirement from action |
| **Preservation Rationale** | Not explicit | Deliberate control decision to preserve baseline | Explain sequencing decision |
| **Windows Compatibility** | Qualified | `WINDOWS_COMPATIBILITY = QUALIFIED` | Retain qualification for unverified Windows platform |
| **Offline Reproduction** | Pass | `OFFLINE_REPRODUCTION = PASS` | Restrict claim to staged local wheel reproduction |
| **Mathematical Firewall** | Established | `A_B_MATHEMATICAL_EQUIVALENCE = ESTABLISHED_FOR_PINNED_EXPERIMENT_ENVIRONMENT` | Protect established $A \equiv B$ equivalence |
| **Human Authorization** | Not explicit | `HUMAN_DEPENDENCY_INTEGRATION_AUTHORIZATION = REQUIRED` | Seal packaging boundary before integration |
