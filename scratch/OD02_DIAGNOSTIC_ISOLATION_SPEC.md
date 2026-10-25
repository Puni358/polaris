# POLARIS — Strict-Whitelist Bubblewrap Isolation Specification (Revision 2.1)
## Review & Static-Preflight Deliverable | No Execution Authorized | Gate C & Gate C.1 Unauthorized

**Tracking ID:** `SPEC-2026-OD02-ISOLATION-03`  
**Supersedes:** `SPEC-2026-OD02-ISOLATION-02`, `SPEC-2026-OD02-ISOLATION-01`  
**Reference Proposal:** `PROP-2026-OD02-DIAG-01`, Revision 2.1  
**Authoritative Governance Version:** MDR `v1.9.13`, Pass 23 (`POLARIS_MASTER_DECISION_REGISTER.md`)  
**Authorization Clearance:** **Preflight Script & Static Tests Only — CONTAINER EXECUTION STRICTLY PROHIBITED**  
**Governance Invariants:** 2025 blind data quarantined; `winner: null`; `GATE_C_AUTHORIZED = False`; `DSL-01 epsilon_tol` and `tau_cont` unset; Decision `OD-02` frozen.

---

## 1. Executive Summary & Revision 2.1 Reconciliations

This specification defines the host pre-checks, Bubblewrap namespace configuration, and in-container preflight probes (`scratch/run_isolation_probes.py`) for Gate C.1.

### Defects Resolved in Revision 2.1 (`SPEC-2026-OD02-ISOLATION-03`):
1. **Individual `scratch/` File Bindings:** Removed broad host scratch directory binding. `/workspace/scratch` is created as an in-memory directory (`--dir /workspace/scratch`) and only three specific files (`run_isolation_probes.py`, `run_od02_boundary_diagnostic.py`, `diag_od02_boundary.py`) are individually bound read-only.
2. **Explicit PID & Network Namespace Isolation:** Both `--unshare-pid` and `--unshare-net` are explicitly configured in the Bubblewrap command.
3. **Fail-Closed Mount Metadata Verification:** Probe P1 and Probe P4 parse `/proc/self/mountinfo` to verify mount presence, filesystem types, and `ro`/`rw` flags rather than relying on existence checks alone.
4. **Non-Destructive Read-Only Verification:** Probe P4 never attempts to create a file on `/workspace/system` or any host-backed read-only mount. It verifies `ro` enforcement via `/proc/self/mountinfo` and `not os.access(path, os.W_OK)`, testing transient file creation exclusively inside the approved writable output directory (`/workspace/experiments/diagnostics/diag_od02_boundary_2024`).
5. **Enforced Wall-Clock & Resource Wrappers:** Added `/usr/bin/timeout --signal=KILL 60s` (preflight) and `600s` (diagnostic) outside `/usr/bin/prlimit --as=8589934592 --cpu=300`.
6. **Direct Preflight Script Invocation:** The proposed preflight command executes `/workspace/.venv/bin/python3 -B /workspace/scratch/run_isolation_probes.py` directly instead of an inline `-c` placeholder.

---

## 2. Host-Side vs. In-Container Verification Boundaries

| Check ID | Domain | Verification Operation | Current Status |
| :--- | :--- | :--- | :--- |
| **H1** | Host-Side (Pre-Launch) | Verify `git status` clean and MDR v1.9.13 untouched | Requires authorized execution |
| **H2** | Host-Side (Pre-Launch) | Verify host files, `.venv`, `/usr/bin/bwrap`, `/usr/bin/prlimit`, `/usr/bin/timeout` exist | Statically specified; runtime check requires authorization |
| **H3** | Host-Side (Pre-Launch) | Independently compute SHA-256 of the 3 approved 2024 CSVs on host via `sha256sum -c` | Requires host execution |
| **H4** | Host-Side (Pre-Launch) | Verify approved output directory `${APPROVED_HOST_OUT}` exists and is writable | Requires Owner provisioning |
| **P1–P7** | In-Container (`bwrap`) | Execute `/workspace/scratch/run_isolation_probes.py` inside isolated namespace | Implemented & statically unit-tested; runtime launch **NOT AUTHORIZED** |

---

## 3. Reconciled Mount Table & Complete Accessible-Path Inventory

Inside the container namespace, `/` is an ephemeral `tmpfs`. Only the paths below exist:

| In-Namespace Path | Host Source Path | Mount Type | Purpose / Justification |
| :--- | :--- | :--- | :--- |
| `/` | *(None - in-memory)* | `--tmpfs` | Clean root VFS, isolating host filesystem root entirely. |
| `/usr` | `/usr` | `--ro-bind` | System binaries, `/usr/bin/python3.12`, C/C++ shared libraries. |
| `/bin` | `usr/bin` | `--symlink` | Ubuntu usrmerge compatibility symlink. |
| `/lib` | `usr/lib` | `--symlink` | Ubuntu usrmerge dynamic library loader symlink. |
| `/lib64` | `usr/lib64` | `--symlink` | x86_64 ELF interpreter symlink (`/lib64/ld-linux-x86-64.so.2`). |
| `/etc` | `/etc` | `--ro-bind` | Linker cache (`/etc/ld.so.cache`) and local timezone metadata. |
| `/proc` | *(procfs)* | `--proc` | Process table isolated to container PID namespace (`--unshare-pid`). |
| `/dev` | *(devtmpfs)* | `--dev` | Standard device nodes (`/dev/null`, `/dev/urandom`, `/dev/zero`). |
| `/tmp` | *(None - in-memory)* | `--tmpfs` | Ephemeral in-memory temporary directory. |
| `/workspace` | *(None - in-memory)* | `--dir` | In-namespace root anchor for POLARIS workspace. |
| `/workspace/scratch` | *(None - in-memory)* | `--dir` | In-namespace directory holding only the 3 approved scripts. |
| `/workspace/data` | *(None - in-memory)* | `--dir` | In-namespace directory holding only the 2 approved 2024 data CSVs. |
| `/workspace/experiments` | *(None - in-memory)* | `--dir` | Parent directory anchor for diagnostics output mount. |
| `/workspace/experiments/diagnostics` | *(None - in-memory)* | `--dir` | Parent directory anchor for diagnostics output mount. |
| `/workspace/.venv` | `${REPO_DIR}/.venv` | `--ro-bind` | Python 3.12.3 virtual environment (`highspy`, `scipy`, `numpy`). |
| `/workspace/system` | `${REPO_DIR}/system` | `--ro-bind` | Production schemas, adapters, and optimizer interfaces (read-only). |
| `/workspace/scratch/run_isolation_probes.py` | `${REPO_DIR}/scratch/run_isolation_probes.py` | `--ro-bind` | Standalone P1–P7 preflight validation probe script. |
| `/workspace/scratch/run_od02_boundary_diagnostic.py` | `${REPO_DIR}/scratch/run_od02_boundary_diagnostic.py` | `--ro-bind` | Approved OD-02 boundary diagnostic batch runner. |
| `/workspace/scratch/diag_od02_boundary.py` | `${REPO_DIR}/scratch/diag_od02_boundary.py` | `--ro-bind` | Approved OD-02 boundary diagnostic harness module. |
| `/workspace/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv` | `${REPO_DIR}/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv` | `--ro-bind` | Approved 2024-EVEN canonical fold assignment matrix. |
| `/workspace/data/POLARIS_v0_1_future_weather_forecasts_2024.csv` | `${REPO_DIR}/data/POLARIS_v0_1_future_weather_forecasts_2024.csv` | `--ro-bind` | Approved 2024 historical weather forecast input. |
| `/workspace/data/POLARIS_v0_1_clearsky_decomposition.csv` | `${REPO_DIR}/data/POLARIS_v0_1_clearsky_decomposition.csv` | `--ro-bind` | Approved Nuolja station clear-sky solar geometry input. |
| `/workspace/experiments/diagnostics/diag_od02_boundary_2024` | `${APPROVED_HOST_OUT}` | `--bind` | **Sole persistent writable host-backed mount** for diagnostic output JSON (ephemeral `/`, `/tmp`, `/dev` remain in-memory only). |

### Exact Visible Directory Allowlists:
- `/workspace`: `{".venv", "system", "scratch", "data", "experiments", "STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv"}`
- `/workspace/scratch`: `{"run_isolation_probes.py", "run_od02_boundary_diagnostic.py", "diag_od02_boundary.py"}`
- `/workspace/data`: `{"POLARIS_v0_1_future_weather_forecasts_2024.csv", "POLARIS_v0_1_clearsky_decomposition.csv"}`

---

## 4. Static Verification of Python & Virtual Environment Layout

From `pyvenv.cfg` and `OD02_DIAGNOSTIC_ISOLATION_SPEC.md`:
- `home = /usr/bin`, `version = 3.12.3`, `executable = /usr/bin/python3.12`, `include-system-site-packages = false`.
- Inside the container, `/workspace/.venv/bin/python3` points to `/usr/bin/python3` $\to$ `/usr/bin/python3.12` (available via `--ro-bind /usr /usr`).
- Python 3.12 determines `sys.prefix` by locating `/workspace/.venv/pyvenv.cfg` adjacent to the parent directory of `/workspace/.venv/bin/python3`, so packages in `/workspace/.venv/lib/python3.12/site-packages` resolve without relying on the historical host path comment inside `pyvenv.cfg`.
- Invoking Python with `-B -E -s` (`PYTHONDONTWRITEBYTECODE=1`, ignore `PYTHON*` environment variables, and disable user site-packages) prevents bytecode write attempts and prevents host environment variables (such as `PYTHONPATH`) from injecting unapproved code into `sys.path` on startup.
- **Static Inspection Caveat:** Dynamic library loading, C-extension initialization (`highspy`), and kernel user-namespace creation are **not** claimed as proved until runtime execution is authorized.

---

## 5. Proposed Commands (NOT AUTHORIZED / DO NOT RUN)

### 5.1 Proposed Gate C.1 Preflight-Only Command (Runs ONLY `run_isolation_probes.py`)

```bash
# ==============================================================================
# NOT AUTHORIZED / DO NOT RUN — PROPOSED GATE C.1 PREFLIGHT-ONLY COMMAND
# Tracking ID: SPEC-2026-OD02-ISOLATION-03
# Executes ONLY scratch/run_isolation_probes.py (P1-P7).
# Does NOT import or invoke the diagnostic runner or production optimizer.
# ==============================================================================

export REPO_DIR="/home/punith-bs/01polaris (Copy)"
export APPROVED_HOST_OUT="${REPO_DIR}/experiments/diagnostics/diag_od02_boundary_2024"

# --- Host-Side Pre-Checks (H2-H4: Read-only assertions, zero host writes) ---
test -d "${REPO_DIR}/system" || { echo "Host error: system/ missing"; exit 1; }
test -d "${REPO_DIR}/.venv" || { echo "Host error: .venv/ missing"; exit 1; }
test -f "${REPO_DIR}/scratch/run_isolation_probes.py" || { echo "Host error: probe script missing"; exit 1; }
test -f "${REPO_DIR}/scratch/run_od02_boundary_diagnostic.py" || { echo "Host error: runner missing"; exit 1; }
test -f "${REPO_DIR}/scratch/diag_od02_boundary.py" || { echo "Host error: harness missing"; exit 1; }
test -f "${REPO_DIR}/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv" || { echo "Host error: fold CSV missing"; exit 1; }
test -f "${REPO_DIR}/data/POLARIS_v0_1_future_weather_forecasts_2024.csv" || { echo "Host error: 2024 weather CSV missing"; exit 1; }
test -f "${REPO_DIR}/data/POLARIS_v0_1_clearsky_decomposition.csv" || { echo "Host error: clearsky CSV missing"; exit 1; }
test -d "${APPROVED_HOST_OUT}" || { echo "Host error: Approved output dir missing; Owner provisioning required"; exit 1; }

# Independent host-side SHA-256 verification before container launch (H3):
/usr/bin/sha256sum -c - <<EOF
0cfc8002e6bf0e8ad11d9ec9832b45a1f085c9d435934a24a3c4edb6b51d62ad  ${REPO_DIR}/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv
596345aa330313414ba41f63ad65278914c6ed1e179965162439e6139a70e52a  ${REPO_DIR}/data/POLARIS_v0_1_clearsky_decomposition.csv
8d24dc72e19e3e42de61485f64299b8fd5ec1888a22ab2f8866b332526e3aa16  ${REPO_DIR}/data/POLARIS_v0_1_future_weather_forecasts_2024.csv
EOF

# --- Proposed Gate C.1 Bubblewrap Preflight Invocation ---
/usr/bin/timeout --signal=KILL 60s \
  /usr/bin/prlimit --as=8589934592 --cpu=300 \
    /usr/bin/bwrap \
      --tmpfs / \
      --ro-bind /usr /usr \
      --symlink usr/bin /bin \
      --symlink usr/lib /lib \
      --symlink usr/lib64 /lib64 \
      --ro-bind /etc /etc \
      --proc /proc \
      --dev /dev \
      --tmpfs /tmp \
      --dir /workspace \
      --dir /workspace/scratch \
      --dir /workspace/data \
      --dir /workspace/experiments \
      --dir /workspace/experiments/diagnostics \
      --dir /workspace/experiments/diagnostics/diag_od02_boundary_2024 \
      --ro-bind "${REPO_DIR}/.venv" "/workspace/.venv" \
      --ro-bind "${REPO_DIR}/system" "/workspace/system" \
      --ro-bind "${REPO_DIR}/scratch/run_isolation_probes.py" "/workspace/scratch/run_isolation_probes.py" \
      --ro-bind "${REPO_DIR}/scratch/run_od02_boundary_diagnostic.py" "/workspace/scratch/run_od02_boundary_diagnostic.py" \
      --ro-bind "${REPO_DIR}/scratch/diag_od02_boundary.py" "/workspace/scratch/diag_od02_boundary.py" \
      --ro-bind "${REPO_DIR}/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv" "/workspace/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv" \
      --ro-bind "${REPO_DIR}/data/POLARIS_v0_1_future_weather_forecasts_2024.csv" "/workspace/data/POLARIS_v0_1_future_weather_forecasts_2024.csv" \
      --ro-bind "${REPO_DIR}/data/POLARIS_v0_1_clearsky_decomposition.csv" "/workspace/data/POLARIS_v0_1_clearsky_decomposition.csv" \
      --bind "${APPROVED_HOST_OUT}" "/workspace/experiments/diagnostics/diag_od02_boundary_2024" \
      --unshare-pid \
      --unshare-net \
      --die-with-parent \
      --new-session \
      --chdir "/workspace" \
      /workspace/.venv/bin/python3 -B -E -s /workspace/scratch/run_isolation_probes.py
```

### 5.2 Proposed Diagnostic Batch Command (Requires Separate Gate C Authorization)

```bash
# /usr/bin/timeout --signal=KILL 600s \
#   /usr/bin/prlimit --as=8589934592 --cpu=300 \
#     /usr/bin/bwrap \
#       --tmpfs / \
#       --ro-bind /usr /usr \
#       --symlink usr/bin /bin \
#       --symlink usr/lib /lib \
#       --symlink usr/lib64 /lib64 \
#       --ro-bind /etc /etc \
#       --proc /proc \
#       --dev /dev \
#       --tmpfs /tmp \
#       --dir /workspace \
#       --dir /workspace/scratch \
#       --dir /workspace/data \
#       --dir /workspace/experiments \
#       --dir /workspace/experiments/diagnostics \
#       --dir /workspace/experiments/diagnostics/diag_od02_boundary_2024 \
#       --ro-bind "${REPO_DIR}/.venv" "/workspace/.venv" \
#       --ro-bind "${REPO_DIR}/system" "/workspace/system" \
#       --ro-bind "${REPO_DIR}/scratch/run_isolation_probes.py" "/workspace/scratch/run_isolation_probes.py" \
#       --ro-bind "${REPO_DIR}/scratch/run_od02_boundary_diagnostic.py" "/workspace/scratch/run_od02_boundary_diagnostic.py" \
#       --ro-bind "${REPO_DIR}/scratch/diag_od02_boundary.py" "/workspace/scratch/diag_od02_boundary.py" \
#       --ro-bind "${REPO_DIR}/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv" "/workspace/STAGE8_1_CANONICAL_FOLD_ASSIGNMENT.csv" \
#       --ro-bind "${REPO_DIR}/data/POLARIS_v0_1_future_weather_forecasts_2024.csv" "/workspace/data/POLARIS_v0_1_future_weather_forecasts_2024.csv" \
#       --ro-bind "${REPO_DIR}/data/POLARIS_v0_1_clearsky_decomposition.csv" "/workspace/data/POLARIS_v0_1_clearsky_decomposition.csv" \
#       --bind "${APPROVED_HOST_OUT}" "/workspace/experiments/diagnostics/diag_od02_boundary_2024" \
#       --unshare-pid \
#       --unshare-net \
#       --die-with-parent \
#       --new-session \
#       --chdir "/workspace" \
#       /workspace/.venv/bin/python3 -B -E -s /workspace/scratch/run_od02_boundary_diagnostic.py
```
