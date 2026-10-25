"""
Fail-closed preflight checks for EXP-THREE-ARM-2024 (research only).

Every check returns a list of failure strings; an empty list means the check passed. `run_preflight`
collects all of them. The runner and the calibration module call this BEFORE constructing any
optimizer, forecaster or calibration fit, and exit nonzero on any failure.

There is no override. A missing record, an unsigned field, a placeholder, a null configuration value,
a decision whose status is not in PASSING_STATUSES, or a hash mismatch is always a failure. A passing dry run or a passing test
does not authorize anything.

Limitation (documented, not hidden): AUTHORIZATION_RECORD.json is a plain file. These checks verify
that it is complete and that it binds the exact package/config/artifact hashes; they cannot prove who
wrote it.
"""
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

PKG_REL = "experiments/exp_three_arm_2024"
CONFIG_REL = f"{PKG_REL}/config/EXPERIMENT_CONFIG.json"

# Statuses that satisfy a required decision or method entry (M9, 2026-10-11). Each records who decided:
#   APPROVED                                  explicit project-lead approval (M5-M8 messages)
#   APPROVED BY EXISTING AUTHORITY            covered by a project-lead statement already on record
#   RESOLVED BY DELEGATED TECHNICAL AUTHORITY decided by the technical PM under the project lead's M9 delegation
# The last two must name their authority in an "authority" field. Every other status (PENDING, PROPOSED,
# RECOMMENDED, CONDITIONALLY APPROVED, BLOCKED, ...) fails. None of these statuses signs an authorization.
PASSING_STATUSES = ("APPROVED", "APPROVED BY EXISTING AUTHORITY", "RESOLVED BY DELEGATED TECHNICAL AUTHORITY")
_NEEDS_AUTHORITY = PASSING_STATUSES[1:]


def status_failure(where: str, entry: Any) -> Optional[str]:
    """None if `entry` carries a passing status (and, for the non-explicit ones, a named authority)."""
    st = entry.get("status") if isinstance(entry, dict) else None
    if st not in PASSING_STATUSES:
        return f"{where} is {st!r}, not one of {PASSING_STATUSES}"
    if st in _NEEDS_AUTHORITY and not str(entry.get("authority") or "").strip():
        return f"{where} is {st!r} but names no authority"
    return None


# Decisions that must pass before any real-data calibration or evaluation solve.
CALIBRATION_DECISIONS = ("D1", "D5", "D7", "D7a", "D8", "D11")
EXECUTION_DECISIONS = ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D7a", "D8", "D10", "D10a", "D11", "BUD")

# Authorization record schema v2 (D9 boundary, 2026-10-11). Preflight authorization and execute authorization are
# separate sections with fixed scopes. `--preflight` accepts a valid execution_preflight OR execution section;
# `--execute` accepts ONLY a valid execution section, which must also reference the project lead's separate,
# explicit execute instruction. `history` entries are never read for authorization.
RECORD_SCHEMA_VERSION = 2
SCOPE_PREFLIGHT = "PREFLIGHT_ONLY"
SCOPE_EXECUTE = "EXECUTE_EXPERIMENT"
EXECUTION_SECTION_SCOPES = {"execution_preflight": SCOPE_PREFLIGHT, "execution": SCOPE_EXECUTE}
AUTHORIZATION_MODES = ("preflight", "execute")

# Files excluded from PACKAGE_MANIFEST.sha256 because they record the freeze or the manifest hash itself,
# or are created later. HANDOVER.md records the current manifest hash (M9), so it cannot be inside it.
MANIFEST_EXCLUDED = ("PACKAGE_MANIFEST.sha256", "PREREGISTRATION.md", "AUTHORIZATION.md",
                     "AUTHORIZATION_RECORD.json", "HANDOVER.md")
MANIFEST_EXCLUDED_DIRS = ("logs/", "results/", "calibration/")

SHA_RE = re.compile(r"^[0-9a-f]{64}$")
VALID_ARMS = ("PC-Control", "A", "A_FIX", "B", "C")
DECISION_BEARING_CANDIDATES = ("A", "A_FIX", "C")  # B is NONCAUSAL and can never be in an E1 family


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class PreflightReport:
    stage: str
    failures: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures

    def extend(self, name: str, fails: Iterable[str]) -> None:
        self.failures.extend(f"[{name}] {f}" for f in fails)


def load_config(repo: Path) -> Dict[str, Any]:
    with open(repo / CONFIG_REL) as f:
        return json.load(f)


# ---------------------------------------------------------------------------- decisions
def check_decisions(cfg: Dict[str, Any], required: Iterable[str]) -> List[str]:
    out = []
    dec = cfg.get("decisions", {})
    for d in required:
        entry = dec.get(d)
        if entry is None:
            out.append(f"decision {d} missing from config")
            continue
        bad = status_failure(f"decision {d}", entry)
        if bad:
            out.append(bad)
        if not entry.get("evidence"):
            out.append(f"decision {d} has no approval evidence")
    if cfg.get("frozen") is not True:
        out.append("configuration is not marked frozen")
    return out


# ---------------------------------------------------------------------------- gates
def check_gates(cfg: Dict[str, Any]) -> List[str]:
    out = []
    g = cfg.get("gates", {})
    fam = g.get("E1_holm_family")
    if fam is None:
        out.append("E1_holm_family is unresolved (D10)")
    else:
        if not isinstance(fam, list) or not fam:
            out.append("E1_holm_family must be a non-empty list of arm names")
        else:
            for a in fam:
                if a not in DECISION_BEARING_CANDIDATES:
                    out.append(f"E1_holm_family contains {a!r}, which is not an eligible causal candidate")
    for k in ("S4", "S4_strict"):
        if g.get(k) not in ("ADOPTED", "NOT_ADOPTED"):
            out.append(f"{k} status is {g.get(k)!r}; must be 'ADOPTED' or 'NOT_ADOPTED' by decision (D2/D6)")
    if g.get("S4_strict") == "ADOPTED" and g.get("S4") != "ADOPTED":
        out.append("S4_strict adopted without S4")
    if g.get("S4_strict") == "ADOPTED" and not isinstance(g.get("S4_strict_bootstrap_seed"), int):
        out.append("S4_strict adopted but no integer bootstrap seed recorded")
    if g.get("S4_strict") == "ADOPTED":
        if g.get("S4_strict_interval") not in ("two_sided_95_upper", "one_sided_95_upper"):
            out.append("S4_strict adopted but S4_strict_interval unresolved")
        for k in ("S4_strict_mean_block_days", "S4_strict_resamples"):
            v = g.get(k)
            if status_failure(k, v):
                out.append(f"S4_strict adopted but {k} not APPROVED")
    if g.get("primary_fuel_metric") != "unadjusted":
        out.append(f"primary_fuel_metric is {g.get('primary_fuel_metric')!r}; D4 fixes it to 'unadjusted'")
    sec = g.get("soc_parity_secondary")
    if not isinstance(sec, dict) or (sec.get("status") != "NOT_PREREGISTERED" and status_failure("s", sec)):
        out.append("soc_parity_secondary must be APPROVED (fully specified) or explicitly NOT_PREREGISTERED (D4)")
    elif sec["status"] != "NOT_PREREGISTERED":
        if sec.get("application") != "per_origin" or sec.get("f_values_l_per_kwh") != [0.30, 0.75]:
            out.append("soc_parity_secondary approved without application 'per_origin' and f = [0.30, 0.75]")
    if g.get("S4_strict") == "ADOPTED" and g.get("S4_strict_interval") is None and g.get("S4_strict_interval_recommendation"):
        out.append(f"S4_strict_interval is only recommended ({g['S4_strict_interval_recommendation']!r}), not decided (D6)")
    return out


# ---------------------------------------------------------------------------- arms
def check_arms(cfg: Dict[str, Any], arm_configs: Dict[str, Dict[str, Any]]) -> List[str]:
    out = []
    if tuple(arm_configs) != VALID_ARMS:
        out.append(f"runner arms {tuple(arm_configs)} != {VALID_ARMS}")
    for arm, spec in arm_configs.items():
        if spec.get("rule_d") is not False:
            out.append(f"arm {arm}: Rule D is not OFF")
        if spec.get("promotion_eligible") is not False:
            out.append(f"arm {arm}: promotion_eligible must be False in this experiment")
        c = cfg.get("arms", {}).get(arm, {})
        if c.get("rule_d") is not False:
            out.append(f"config arm {arm}: Rule D is not OFF")
        if c.get("causal") != spec.get("causal"):
            out.append(f"arm {arm}: causal flag differs between config and runner")
    b = arm_configs.get("B", {})
    if b.get("causal") is not False or "NONCAUSAL" not in str(b.get("result_label", "")):
        out.append("arm B must be tagged NONCAUSAL")
    a, f = dict(arm_configs.get("A", {})), dict(arm_configs.get("A_FIX", {}))
    for k in ("solar_label_correction", "result_label"):
        a.pop(k, None)
        f.pop(k, None)
    if a != f:
        out.append("arms A and A_FIX differ in more than solar_label_correction and result_label")
    return out


# ---------------------------------------------------------------------------- calibration method
def check_arm_c_method(cfg: Dict[str, Any]) -> List[str]:
    out = []
    m = cfg.get("arm_c_method", {})
    for k, v in m.items():
        if k.startswith("_"):
            continue
        if v is None:
            out.append(f"arm_c_method.{k} is unresolved")
        elif not isinstance(v, dict) or "status" not in v:
            out.append(f"arm_c_method.{k} has no recorded status")
        else:
            bad = status_failure(f"arm_c_method.{k} status", v)
            if bad:
                out.append(bad)
    return out


# ---------------------------------------------------------------------------- hashes
def check_hashes(repo: Path, cfg: Dict[str, Any]) -> List[str]:
    out = []
    groups = cfg.get("expected_sha256", {})
    for grp in ("frozen_code", "inputs", "configuration"):
        entries = groups.get(grp)
        if not entries:
            out.append(f"expected_sha256.{grp} missing")
            continue
        for rel, exp in entries.items():
            if not isinstance(exp, str) or not SHA_RE.match(exp):
                out.append(f"{rel}: expected hash missing or malformed")
                continue
            p = repo / rel
            if not p.is_file():
                out.append(f"{rel}: file missing")
                continue
            got = sha256_file(p)
            if got != exp:
                out.append(f"{rel}: sha256 {got} != expected {exp}")
    return out


def manifest_files(pkg: Path) -> List[str]:
    files = []
    for p in sorted(pkg.rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts or p.suffix == ".pyc":
            continue
        rel = p.relative_to(pkg).as_posix()
        if rel in MANIFEST_EXCLUDED or rel.startswith(MANIFEST_EXCLUDED_DIRS) or rel.startswith(".pytest_cache"):
            continue
        files.append(rel)
    return files


def check_package_manifest(repo: Path) -> List[str]:
    out = []
    pkg = repo / PKG_REL
    man = pkg / "PACKAGE_MANIFEST.sha256"
    if not man.is_file():
        return ["PACKAGE_MANIFEST.sha256 missing"]
    listed = {}
    for line in man.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or not SHA_RE.match(parts[0]):
            out.append(f"malformed manifest line: {line!r}")
            continue
        listed[parts[1].strip()] = parts[0]
    actual = manifest_files(pkg)
    for rel in actual:
        if rel not in listed:
            out.append(f"{rel}: present in package but not in manifest")
        elif sha256_file(pkg / rel) != listed[rel]:
            out.append(f"{rel}: hash differs from manifest")
    for rel in listed:
        if rel not in actual:
            out.append(f"{rel}: listed in manifest but missing")
    return out


# ---------------------------------------------------------------------------- authorization
def _is_iso_utc(s: Any) -> bool:
    if not isinstance(s, str) or not s.endswith("Z"):
        return False
    try:
        datetime.fromisoformat(s[:-1])
        return True
    except ValueError:
        return False


def _load_record(repo: Path, cfg: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    path = repo / cfg.get("paths", {}).get("authorization_record", f"{PKG_REL}/AUTHORIZATION_RECORD.json")
    if not path.is_file():
        return None, ["authorization record missing"]
    try:
        rec = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return None, [f"authorization record is not valid JSON: {e}"]
    out = []
    if rec.get("experiment_id") != cfg.get("experiment_id"):
        out.append("authorization record is for a different experiment")
    if rec.get("schema_version") != RECORD_SCHEMA_VERSION:
        out.append(f"authorization record schema_version is {rec.get('schema_version')!r}, not {RECORD_SCHEMA_VERSION}")
    return rec, out


def _signature_failures(sec: Dict[str, Any], stage: str) -> List[str]:
    out = []
    if sec.get("decision") != "APPROVE":
        out.append(f"{stage} decision is {sec.get('decision')!r}, not 'APPROVE'")
    if not (isinstance(sec.get("signer_name"), str) and sec["signer_name"].strip()):
        out.append(f"{stage} is unsigned (signer_name empty)")
    if str(sec.get("signer_role", "")).strip().lower() != "project lead":
        out.append(f"{stage} signer_role is {sec.get('signer_role')!r}, not 'project lead'")
    if not _is_iso_utc(sec.get("signed_at_utc")):
        out.append(f"{stage} signed_at_utc missing or not ISO-8601 UTC ('...Z')")
    return out


def _execution_history(repo: Path) -> Tuple[Dict[str, Tuple[str, Optional[str]]], List[str]]:
    """Scans results/run_* for execution history. Returns (consumed, ambiguous).

    `consumed` maps every `execute_instruction_ref` found in a well-formed RUN_STATUS.json to the
    (run directory name, status) that recorded it. A run counts regardless of outcome (FAILED,
    COMPLETE, RUNNING, or any other status): once an execution authorization has been acted on --
    the runner started against it -- it is consumed and must never authorize a second run.

    `ambiguous` lists one description per run_* directory whose status evidence could not be read
    and interpreted as a specific, known ref: a missing RUN_STATUS.json (e.g. a crash between
    `run_dir.mkdir()` and the first `_status()` write in `execute()`), a file that cannot be read
    (OS/permission error), invalid JSON, a JSON value that is not an object, or an object with no
    usable `execute_instruction_ref`. Absence or unreadability of evidence is never treated as proof
    that a reference is unused -- the caller must fail closed on a non-empty `ambiguous` list,
    globally, because an unreadable record could have consumed any reference."""
    consumed: Dict[str, Tuple[str, Optional[str]]] = {}
    ambiguous: List[str] = []
    results_dir = repo / PKG_REL / "results"
    if not results_dir.is_dir():
        return consumed, ambiguous
    for run_dir in sorted(results_dir.glob("run_*")):
        if not run_dir.is_dir():
            continue  # stray non-directory entry, not something execute() could have created
        status_path = run_dir / "RUN_STATUS.json"
        if not status_path.is_file():
            ambiguous.append(f"{run_dir.name}: RUN_STATUS.json missing (possible crash before the "
                             "first status write)")
            continue
        try:
            text = status_path.read_text()
        except OSError as e:
            ambiguous.append(f"{run_dir.name}: RUN_STATUS.json unreadable ({type(e).__name__}: {e})")
            continue
        try:
            st = json.loads(text)
        except json.JSONDecodeError as e:
            ambiguous.append(f"{run_dir.name}: RUN_STATUS.json is not valid JSON ({e})")
            continue
        if not isinstance(st, dict):
            ambiguous.append(f"{run_dir.name}: RUN_STATUS.json content is not a JSON object")
            continue
        ref = st.get("execute_instruction_ref")
        if not (isinstance(ref, str) and ref.strip()):
            ambiguous.append(f"{run_dir.name}: RUN_STATUS.json has no usable execute_instruction_ref")
            continue
        if ref not in consumed:
            consumed[ref] = (run_dir.name, st.get("status"))
    return consumed, ambiguous


def _consumed_execute_refs(repo: Path) -> Dict[str, Tuple[str, Optional[str]]]:
    """Backward-compatible accessor: the consumed-ref mapping alone. Callers that must fail closed
    on ambiguous execution history (see `check_authorization`'s 'execution' stage) use
    `_execution_history` directly instead, since this wrapper discards the ambiguity signal."""
    consumed, _ = _execution_history(repo)
    return consumed


def check_authorization(repo: Path, cfg: Dict[str, Any], stage: str,
                        calibration_artifact_sha: Optional[str] = None) -> List[str]:
    """Validates one section: 'calibration', 'execution_preflight' or 'execution'. Never reads `history`."""
    if stage != "calibration" and stage not in EXECUTION_SECTION_SCOPES:
        raise ValueError(f"unknown authorization stage {stage!r}")
    rec, out = _load_record(repo, cfg)
    if rec is None:
        return out
    sec = rec.get(stage)
    if not isinstance(sec, dict):
        return out + [f"authorization record has no '{stage}' section"]
    out += _signature_failures(sec, stage)
    pm = repo / PKG_REL / "PACKAGE_MANIFEST.sha256"
    if not pm.is_file() or sec.get("package_manifest_sha256") != sha256_file(pm):
        out.append(f"{stage} package_manifest_sha256 does not match the current manifest")
    if sec.get("experiment_config_sha256") != sha256_file(repo / CONFIG_REL):
        out.append(f"{stage} experiment_config_sha256 does not match the current config")
    if stage in EXECUTION_SECTION_SCOPES:
        if sec.get("scope") != EXECUTION_SECTION_SCOPES[stage]:
            out.append(f"{stage} scope is {sec.get('scope')!r}, not {EXECUTION_SECTION_SCOPES[stage]!r}")
        if calibration_artifact_sha is None or sec.get("calibration_artifact_sha256") != calibration_artifact_sha:
            out.append(f"{stage} calibration_artifact_sha256 does not match the calibration artifact")
        if type(sec.get("solve_ceiling")) is not int or sec.get("solve_ceiling") != cfg.get("budget", {}).get("total_ceiling"):
            out.append(f"{stage} solve_ceiling does not equal the configured total ceiling")
    if stage == "execution":
        ref = sec.get("execute_instruction_ref")
        if not (isinstance(ref, str) and ref.strip()):
            out.append("execution execute_instruction_ref is empty (must reference the project lead's explicit "
                       "execute instruction)")
        else:
            consumed, ambiguous = _execution_history(repo)
            if ambiguous:
                out.append(
                    "execution authorization refused: ambiguous run history in results/ makes it "
                    "impossible to confirm execute_instruction_ref is unused (" + "; ".join(ambiguous) +
                    "); this blocks ALL execution authorization, not just this reference, until a "
                    "human investigates and resolves the ambiguous evidence -- absence of a readable "
                    "status record is never treated as proof a reference was never used")
            if ref in consumed:
                run_name, run_status = consumed[ref]
                out.append(f"execution execute_instruction_ref has already been consumed by {run_name} "
                           f"(status {run_status!r}); a consumed authorization cannot authorize another "
                           "execution -- a new explicit instruction and signature are required")
        pre = rec.get("execution_preflight")
        if isinstance(pre, dict) and _is_iso_utc(pre.get("signed_at_utc")) and _is_iso_utc(sec.get("signed_at_utc")):
            if _utc(sec["signed_at_utc"]) < _utc(pre["signed_at_utc"]):
                out.append("execution signed_at_utc precedes execution_preflight signed_at_utc")
    return out


def check_execution_authorization(repo: Path, cfg: Dict[str, Any], mode: str,
                                  calibration_artifact_sha: Optional[str]) -> List[str]:
    """mode 'execute': only a valid `execution` section (scope EXECUTE_EXPERIMENT) passes.
    mode 'preflight': a valid `execution_preflight` section or a valid `execution` section passes.
    Any other mode raises; there is no default."""
    if mode not in AUTHORIZATION_MODES:
        raise ValueError(f"unknown authorization mode {mode!r}")
    exe = check_authorization(repo, cfg, "execution", calibration_artifact_sha)
    if mode == "execute" or not exe:
        return exe
    pre = check_authorization(repo, cfg, "execution_preflight", calibration_artifact_sha)
    if not pre:
        return []
    return pre + exe


def prior_freezes(repo: Path) -> List[str]:
    """Superseded PACKAGE_MANIFEST hashes recorded in PREREGISTRATION.md, one line each:
    `Prior freeze (superseded): <64 hex> ...`."""
    p = repo / PKG_REL / "PREREGISTRATION.md"
    if not p.is_file():
        return []
    return re.findall(r"^Prior freeze \(superseded\):\s*([0-9a-f]{64})", p.read_text(), re.M)


def check_calibration_authorization(repo: Path, cfg: Dict[str, Any], artifact: Optional[Dict[str, Any]]) -> List[str]:
    """The calibration artifact must have been produced under a signed calibration authorization: decision APPROVE
    by the project lead, bound to the current config, signed no later than the artifact was created, and bound to
    the current manifest or to a prior freeze recorded in PREREGISTRATION.md (the freeze it was authorized under)."""
    rec, out = _load_record(repo, cfg)
    if rec is None:
        return out
    sec = rec.get("calibration")
    if not isinstance(sec, dict):
        return out + ["authorization record has no 'calibration' section"]
    out += _signature_failures(sec, "calibration")
    if sec.get("experiment_config_sha256") != sha256_file(repo / CONFIG_REL):
        out.append("calibration experiment_config_sha256 does not match the current config")
    pm = repo / PKG_REL / "PACKAGE_MANIFEST.sha256"
    current = sha256_file(pm) if pm.is_file() else None
    if sec.get("package_manifest_sha256") not in [current] + prior_freezes(repo):
        out.append("calibration package_manifest_sha256 matches neither the current manifest nor a recorded prior freeze")
    created = (artifact or {}).get("created_at_utc")
    if not _is_iso_utc(created):
        out.append("calibration artifact has no created_at_utc to bind the calibration authorization to")
    elif _is_iso_utc(sec.get("signed_at_utc")) and _utc(sec["signed_at_utc"]) > _utc(created):
        out.append("calibration authorization was signed after the calibration artifact was created")
    return out


def check_preregistration_frozen(repo: Path) -> List[str]:
    p = repo / PKG_REL / "PREREGISTRATION.md"
    if not p.is_file():
        return ["PREREGISTRATION.md missing"]
    text = p.read_text()
    m = re.search(r"PACKAGE_MANIFEST\.sha256 SHA-256:\s*([0-9a-f]{64})", text)
    if not m:
        return ["PREREGISTRATION.md freeze record has no package manifest hash"]
    pm = repo / PKG_REL / "PACKAGE_MANIFEST.sha256"
    if not pm.is_file() or m.group(1) != sha256_file(pm):
        return ["PREREGISTRATION.md freeze hash does not match PACKAGE_MANIFEST.sha256"]
    return []


def _utc(s: str) -> datetime:
    return datetime.fromisoformat(s[:-1])


# ---------------------------------------------------------------------------- budget / output
def check_budget(cfg: Dict[str, Any], expected_per_arm: int, expected_total: int) -> List[str]:
    out = []
    b = cfg.get("budget", {})
    if b.get("per_arm_ceiling") != expected_per_arm:
        out.append(f"per-arm ceiling {b.get('per_arm_ceiling')} != derived per-arm count {expected_per_arm}")
    if b.get("total_ceiling") != expected_total:
        out.append(f"total ceiling {b.get('total_ceiling')} != derived total count {expected_total}")
    if b.get("retries") != 0:
        out.append("retries must be 0")
    if b.get("repeat_check_included") is not False or b.get("rule_d_subarm_included") is not False:
        out.append("repeat check and Rule D sub-arm must be excluded unless separately approved")
    return out


def check_output_root(repo: Path, cfg: Dict[str, Any]) -> List[str]:
    root = repo / cfg.get("paths", {}).get("results_root", f"{PKG_REL}/results")
    if not root.is_dir():
        return [f"results root {root} missing"]
    if root.resolve().parent != (repo / PKG_REL).resolve():
        return ["results root is outside the package"]
    return []
