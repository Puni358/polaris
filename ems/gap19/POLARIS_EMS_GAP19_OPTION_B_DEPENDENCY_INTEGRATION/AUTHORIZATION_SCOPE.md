# Controlled Dependency Integration Authorization Scope

```text
AUTHORIZATION_TYPE = HUMAN_GRANTED
AUTHORIZED_SCOPE = ADD_EXACTLY_HIGHSPY_1.15.1
TARGET_ENVIRONMENT = MAIN_POLARIS_PROJECT_VENV
UNAUTHORIZED_CHANGES = NONE
MANIFEST_MODIFICATION = NOT_AUTHORIZED
SOURCE_MODIFICATION = NOT_AUTHORIZED
```

The human authorization specifically permitted installing `highspy==1.15.1` into the target virtual environment using `--no-deps` to preserve existing versions of SciPy (1.18.1) and NumPy (2.5.2).
