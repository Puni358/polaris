"""
POLARIS -- Cross-Arm Reproducibility Manifest (Schema & Fail-Closed Builder)
=============================================================================
Resolves `ems/reports/diesel_and_loads/DIESEL_COMPARISON_PREREQUISITE_PLAN.md` Table row 12: "today the
two hash sets [N6's own model-hash manifest, and the existing three-arm
experiment's config/code/input manifests] live in separate, unrelated
locations... and were never cross-referenced against each other." This
module defines the SCHEMA for the single combined manifest a future,
separately authorized N6-vs-baseline comparison run would need to produce as
part of its own provenance record, and a BUILDER that assembles one -- but
only ever from caller-supplied values.

GOVERNANCE STATUS: DOCUMENTATION / SCHEMA ONLY -- NO FABRICATION
-------------------------------------------------------------------
- `build_cross_arm_reproducibility_manifest` NEVER invents, defaults, or
  silently fills in a missing hash, version string, or origin. Every
  required field must be supplied by the caller from an already-computed,
  cited source (a `.sha256` manifest already on disk, a frozen-artifact
  manifest already on disk, `pip freeze`/`python --version` output, etc.).
  A missing REQUIRED field raises `ValueError` -- it is never coerced to an
  empty string, `None`-as-if-it-were-a-value, or a placeholder that could be
  mistaken for a real hash.
- `output_hashes` is explicitly OPTIONAL and empty by default, because no
  campaign has been executed (`replay_harness.py`'s
  `CampaignExecutionNotAuthorizedError` remains unconditional) -- there are
  no output artifacts to hash yet. Supplying a non-empty `output_hashes`
  before a real, authorized run has actually produced those outputs would be
  exactly the kind of fabricated provenance this module exists to prevent;
  nothing in this module encourages or automates that.
- `load_known_existing_hash_sources` (bottom of this file) reads, BY EXACT
  PATH, the two hash/manifest sources that already exist in this repository
  today (the N6 model's own frozen-artifact manifest, and the existing
  three-arm baseline experiment's CODE/CONFIGURATION/INPUTS `.sha256` files)
  and returns their contents verbatim for citation. It performs no campaign
  execution, no dispatch, and no model loading -- it is a read-only file
  parse of already-existing, already-committed-to-disk hash manifests from
  prior, already-completed passes (FOR-03's N6-manifest consolidation;
  `exp_three_arm_2024`'s own manifest-generation step).
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Tuple

__all__ = [
    "CrossArmReproducibilityManifest",
    "build_cross_arm_reproducibility_manifest",
    "load_known_existing_hash_sources",
]

_SHA256_RE = re.compile(r"^[0-9a-f]{64,66}$")  # some manifests in this repo carry 65/66-hex-char hashes verbatim


@dataclass(frozen=True)
class CrossArmReproducibilityManifest:
    """
    The combined, cross-arm provenance record a future authorized
    N6-vs-baseline comparison run would need to produce. Every hash field is
    a plain string the caller computed or read elsewhere -- this dataclass
    does no hashing itself and performs no I/O.
    """

    n6_model_sha256: str
    n6_model_manifest_source: str
    baseline_code_sha256: Dict[str, str]
    baseline_configuration_sha256: Dict[str, str]
    baseline_inputs_sha256: Dict[str, str]
    baseline_manifest_source: str
    origins: Tuple[str, ...]
    experiment_configuration_sha256: str
    runtime_dependency_versions: Dict[str, str]
    authorization_reference: Optional[str]
    output_hashes: Dict[str, str] = field(default_factory=dict)
    assembled_at_utc: Optional[str] = None
    notes: Tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.n6_model_sha256:
            raise ValueError("Fail-closed: n6_model_sha256 is required and must be non-empty.")
        if not self.baseline_code_sha256:
            raise ValueError("Fail-closed: baseline_code_sha256 must contain at least one entry.")
        if not self.baseline_configuration_sha256:
            raise ValueError("Fail-closed: baseline_configuration_sha256 must contain at least one entry.")
        if not self.baseline_inputs_sha256:
            raise ValueError("Fail-closed: baseline_inputs_sha256 must contain at least one entry.")
        if not self.origins:
            raise ValueError("Fail-closed: at least one origin is required.")
        if not self.experiment_configuration_sha256:
            raise ValueError("Fail-closed: experiment_configuration_sha256 is required and must be non-empty.")
        if not self.runtime_dependency_versions:
            raise ValueError("Fail-closed: runtime_dependency_versions must contain at least one entry.")
        if self.authorization_reference is None:
            raise ValueError(
                "Fail-closed: authorization_reference is required -- a reproducibility manifest for an "
                "actual run must cite the authorization record that permitted it (e.g. the record this "
                "repository's forecasting/n6/reports/N6_CONSOLIDATED_READINESS_REMEDIATION_REPORT.md Workstream 2 proposes). "
                "Pass an explicit string stating 'NOT_YET_AUTHORIZED' if assembling this manifest only as "
                "a pre-authorization dry run -- never a real-looking placeholder."
            )


def build_cross_arm_reproducibility_manifest(
    n6_model_sha256: str,
    n6_model_manifest_source: str,
    baseline_code_sha256: Dict[str, str],
    baseline_configuration_sha256: Dict[str, str],
    baseline_inputs_sha256: Dict[str, str],
    baseline_manifest_source: str,
    origins: Tuple[str, ...],
    experiment_configuration_sha256: str,
    runtime_dependency_versions: Dict[str, str],
    authorization_reference: Optional[str],
    output_hashes: Optional[Dict[str, str]] = None,
    assembled_at_utc: Optional[str] = None,
    notes: Optional[Tuple[str, ...]] = None,
) -> CrossArmReproducibilityManifest:
    """
    Thin, explicit constructor wrapper (so callers do not need to know the
    dataclass carries its own `__post_init__` validation) around
    `CrossArmReproducibilityManifest`. Every argument must come from an
    already-computed, cited source; this function performs no hashing, no
    file I/O, and no network access.
    """
    return CrossArmReproducibilityManifest(
        n6_model_sha256=n6_model_sha256,
        n6_model_manifest_source=n6_model_manifest_source,
        baseline_code_sha256=dict(baseline_code_sha256),
        baseline_configuration_sha256=dict(baseline_configuration_sha256),
        baseline_inputs_sha256=dict(baseline_inputs_sha256),
        baseline_manifest_source=baseline_manifest_source,
        origins=tuple(origins),
        experiment_configuration_sha256=experiment_configuration_sha256,
        runtime_dependency_versions=dict(runtime_dependency_versions),
        authorization_reference=authorization_reference,
        output_hashes=dict(output_hashes) if output_hashes else {},
        assembled_at_utc=assembled_at_utc,
        notes=tuple(notes) if notes else (),
    )


def _parse_sha256_manifest_file(path: Path) -> Dict[str, str]:
    """
    Parses one of this repository's existing `<name>.sha256` manifest files
    (plain `<hash>  <repo-relative-path>` lines, `#`-prefixed comment lines
    ignored) into a `{path: hash}` dict. Read-only; raises if the file does
    not exist -- never substitutes an empty or synthetic result for a
    missing manifest.
    """
    if not path.is_file():
        raise ValueError(f"Fail-closed: expected hash manifest not found at '{path}'.")
    result: Dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or not _SHA256_RE.match(parts[0]):
            continue  # skip any malformed/non-hash line rather than guessing its meaning
        digest, rel_path = parts
        result[rel_path.strip()] = digest
    if not result:
        raise ValueError(f"Fail-closed: '{path}' parsed to zero hash entries -- refusing to cite an empty manifest.")
    return result


def load_known_existing_hash_sources(repo_root: Path) -> Dict[str, object]:
    """
    Read-only loader for the two hash/manifest sources that already exist in
    this repository (no fabrication, no hashing performed here -- every
    value returned was already computed and committed to disk by a prior,
    already-completed pass):

    - The N6 model's own frozen-artifact manifest
      (`forecasting/stage7/.../candidate_n_additive_physics/artifacts/CANDIDATE_N_MANIFEST.json`,
      `models.candidate_n6.sha256`, FOR-03-consolidated single source of
      truth).
    - The existing three-arm baseline experiment's `CODE.sha256`,
      `CONFIGURATION.sha256`, and `INPUTS.sha256` manifests
      (`experiments/exp_three_arm_2024/manifests/`).

    Returns a dict with keys `n6_model_sha256`, `n6_model_manifest_source`,
    `baseline_code_sha256`, `baseline_configuration_sha256`,
    `baseline_inputs_sha256`, `baseline_manifest_source` -- ready to splice
    into `build_cross_arm_reproducibility_manifest`'s matching arguments.
    Raises `ValueError` (fail-closed) if either source is missing or
    unparseable; never returns a partial or synthesized substitute.
    """
    n6_manifest_path = (
        repo_root
        / "forecasting/stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/artifacts/CANDIDATE_N_MANIFEST.json"
    )
    if not n6_manifest_path.is_file():
        raise ValueError(f"Fail-closed: N6 model manifest not found at '{n6_manifest_path}'.")
    n6_manifest = json.loads(n6_manifest_path.read_text())
    try:
        n6_model_sha256 = n6_manifest["models"]["candidate_n6"]["sha256"]
    except KeyError as exc:
        raise ValueError(
            f"Fail-closed: '{n6_manifest_path}' does not contain models.candidate_n6.sha256."
        ) from exc
    if not n6_model_sha256:
        raise ValueError(f"Fail-closed: models.candidate_n6.sha256 in '{n6_manifest_path}' is empty.")

    manifests_dir = repo_root / "experiments/exp_three_arm_2024/manifests"
    baseline_code = _parse_sha256_manifest_file(manifests_dir / "CODE.sha256")
    baseline_configuration = _parse_sha256_manifest_file(manifests_dir / "CONFIGURATION.sha256")
    baseline_inputs = _parse_sha256_manifest_file(manifests_dir / "INPUTS.sha256")

    return {
        "n6_model_sha256": n6_model_sha256,
        "n6_model_manifest_source": str(n6_manifest_path.relative_to(repo_root)),
        "baseline_code_sha256": baseline_code,
        "baseline_configuration_sha256": baseline_configuration,
        "baseline_inputs_sha256": baseline_inputs,
        "baseline_manifest_source": str(manifests_dir.relative_to(repo_root)),
    }
