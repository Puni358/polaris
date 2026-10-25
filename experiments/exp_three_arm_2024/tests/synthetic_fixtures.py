"""Synthetic fixtures for EXP-THREE-ARM-2024 preparation tests. No repository data file is read.

- synthetic_weather(): a weather-shaped frame for chosen 2024 dates with made-up cloud and SW_IN values.
- build_fake_repo(): a throw-away repo tree under tmp_path holding this package's real config and a NULL
  schema-v2 authorization template (null_record(); never the live record, so tests do not depend on what the
  project lead has signed), plus small dummy files standing in for frozen code and inputs, with the
  config's expected hashes rewritten to match the dummies.
- approve_everything(): a TEST-ONLY fully resolved config and a TEST-ONLY signed authorization record,
  used as a positive control so each negative test isolates one failure. Neither is ever written to
  the package; both live only under tmp_path.
- FakeOptimizer: returns a zero-dispatch plan without any solver, and counts calls.
"""
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

PKG = Path(__file__).resolve().parents[1]
PKG_REL = "experiments/exp_three_arm_2024"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def synthetic_weather(days: List[str], cloud: Optional[Dict[str, float]] = None) -> pd.DataFrame:
    rows = []
    for d in days:
        fs = pd.Timestamp(d)
        c = (cloud or {}).get(d, 40.0)
        for h in range(1, 25):
            t = fs + pd.Timedelta(hours=h - 1)
            sw = max(0.0, 400.0 * math.sin(math.pi * (t.hour - 2) / 22.0))
            rows.append({"forecast_start": fs.strftime("%Y-%m-%d %H:%M:%S"), "horizon_hour": h,
                         "timestamp": t.strftime("%Y-%m-%d %H:%M:%S"),
                         "fc_cloud_cover": float(c) if c >= 90 else float(c) + (h % 5),
                         "actual_SW_IN": round(sw, 3)})
    return pd.DataFrame(rows)


def load_real_cfg() -> Dict[str, Any]:
    return json.loads((PKG / "config" / "EXPERIMENT_CONFIG.json").read_text())


def _write(path: Path, data: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return sha(data)


def build_fake_repo(tmp_path: Path, cfg: Optional[Dict[str, Any]] = None) -> Path:
    repo = tmp_path / "repo"
    pkg = repo / PKG_REL
    cfg = copy.deepcopy(cfg if cfg is not None else load_real_cfg())
    for grp, entries in cfg["expected_sha256"].items():
        for rel in list(entries):
            entries[rel] = _write(repo / rel, f"dummy {grp} {rel}\n".encode())
    (pkg / "config").mkdir(parents=True, exist_ok=True)
    (pkg / "results").mkdir(parents=True, exist_ok=True)
    (pkg / "AUTHORIZATION_RECORD.json").write_text(json.dumps(null_record(cfg), indent=2))
    write_cfg(repo, cfg)
    (pkg / "scripts").mkdir(exist_ok=True)
    (pkg / "scripts" / "placeholder.py").write_text("# synthetic package file\n")
    write_manifest(repo)
    return repo


def null_record(cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Unsigned schema-v2 authorization record (same shape as the package record)."""
    import preflight as pf
    keys = ("decision", "signer_name", "signer_role", "signed_at_utc", "package_manifest_sha256",
            "experiment_config_sha256")
    ex = keys + ("calibration_artifact_sha256", "solve_ceiling")
    return {"experiment_id": (cfg or load_real_cfg())["experiment_id"], "schema_version": pf.RECORD_SCHEMA_VERSION,
            "calibration": {k: None for k in keys},
            "execution_preflight": {"scope": pf.SCOPE_PREFLIGHT, **{k: None for k in ex}},
            "execution": {"scope": pf.SCOPE_EXECUTE, **{k: None for k in ex}, "execute_instruction_ref": None},
            "history": []}


def write_cfg(repo: Path, cfg: Dict[str, Any]) -> None:
    (repo / PKG_REL / "config" / "EXPERIMENT_CONFIG.json").write_text(json.dumps(cfg, indent=2))


def write_manifest(repo: Path) -> str:
    import preflight as pf
    pkg = repo / PKG_REL
    lines = [f"{pf.sha256_file(pkg / rel)}  {rel}" for rel in pf.manifest_files(pkg)]
    (pkg / "PACKAGE_MANIFEST.sha256").write_text("\n".join(lines) + "\n")
    return pf.sha256_file(pkg / "PACKAGE_MANIFEST.sha256")


def approve_everything(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """TEST-ONLY resolved configuration. The values are arbitrary placeholders, not recommendations."""
    c = copy.deepcopy(cfg)
    for d in c["decisions"].values():
        d["status"] = "APPROVED"
        d["evidence"] = "TEST-ONLY synthetic approval"
    c["frozen"] = True
    m = c["arm_c_method"]
    for k, v in list(m.items()):
        if k.startswith("_"):
            continue
        assert isinstance(v, dict), f"arm_c_method.{k} has no value/status record"
        v["status"] = "APPROVED"
    g = c["gates"]
    g.update({"E1_holm_family": ["A", "C"], "S4": "ADOPTED", "S4_strict": "ADOPTED",
              "S4_strict_interval": "two_sided_95_upper", "S4_strict_bootstrap_seed": 42,
              "primary_fuel_metric": "unadjusted"})
    g["soc_parity_secondary"].update(status="APPROVED", application="per_origin")
    return c


def sign(repo: Path, stage: str, calibration_sha: Optional[str] = None, solve_ceiling: Optional[int] = None,
         **override) -> None:
    import preflight as pf
    pkg = repo / PKG_REL
    rec = json.loads((pkg / "AUTHORIZATION_RECORD.json").read_text())
    sec = rec[stage]
    sec.update({"decision": "APPROVE", "signer_name": "TEST-ONLY SIGNER", "signer_role": "project lead",
                "signed_at_utc": "2026-10-11T00:00:00Z",
                "package_manifest_sha256": pf.sha256_file(pkg / "PACKAGE_MANIFEST.sha256"),
                "experiment_config_sha256": pf.sha256_file(pkg / "config" / "EXPERIMENT_CONFIG.json")})
    if stage in pf.EXECUTION_SECTION_SCOPES:
        sec["scope"] = pf.EXECUTION_SECTION_SCOPES[stage]
        sec["calibration_artifact_sha256"] = calibration_sha
        sec["solve_ceiling"] = solve_ceiling
    if stage == "execution":
        sec["execute_instruction_ref"] = "TEST-ONLY instruction"
    sec.update(override)
    (pkg / "AUTHORIZATION_RECORD.json").write_text(json.dumps(rec, indent=2))


def freeze_prereg(repo: Path) -> None:
    import preflight as pf
    pkg = repo / PKG_REL
    h = pf.sha256_file(pkg / "PACKAGE_MANIFEST.sha256")
    (pkg / "PREREGISTRATION.md").write_text(f"# TEST-ONLY\n\nPACKAGE_MANIFEST.sha256 SHA-256: {h}\n")


class FakeOptimizer:
    """No solver. Returns a zero-dispatch plan with the requested status and records each call."""

    def __init__(self, status: str = "OPTIMAL"):
        self.status = status
        self.calls: List[Dict[str, Any]] = []
        self.last_planned: List[Dict[str, Any]] = []
        self.last_diagnostics: List[Dict[str, Any]] = []
        self.last_em_rows_built = 0

    def optimize(self, bundle, state, cfg):
        from system.schemas.dispatch_plan import DispatchPlan
        self.calls.append({"bundle_t1": bundle.timestamps[0], "state_ts": state.timestamp,
                           "ebr": list(cfg["ebr_target_wh"]), "solar_w": list(bundle.solar_generation.point),
                           "terminal": cfg["terminal_target_wh"]})
        z = [0.0] * 24
        self.last_planned = [{"t": i, "diesel": 0.0, "served_c": 0.0, "served_nc": 0.0, "unmet_crit": 0.0,
                              "unmet_nc": 0.0, "charge": 0.0} for i in range(24)]
        self.last_diagnostics = [{"solver_status": self.status, "j2_shortfall_wh": 0.0}]
        return DispatchPlan("1.0.0", list(bundle.timestamps), z, z, z, z, [50.0] * 24, z, z, z, z, z, 0.0,
                            self.status, z)
