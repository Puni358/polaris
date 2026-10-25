"""
Protected-artifact hash guards for Planner-CF v1 (EXP-PLANNER-CF-CONSISTENCY-2025, §9, G8, G11).

Pins are the SHA-256 values recorded in the preregistration §9 table. Each path is relative to the
repository root. The check is read-only.
"""

import hashlib
from pathlib import Path
from typing import Dict, List

PROTECTED_PINS: Dict[str, str] = {
    "system/optimization/implementations/gap19_highs_native.py":
        "fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737",
    "system/simulation/research_realization_executor.py":
        "c1ab56bf92eab7c1bacb2108b241d97d84f4e935dff9a33fd8f6bd0675b73a6b",
    "system/schemas/dispatch_plan.py":
        "21c0b83e878debf1e7d4c4ee9d472bb17aa84ef545a2f1b9cbb222940fd7fb0b",
    "system/forecasting/implementations/causal_nwp_physics.py":
        "14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710",
    "experiments/candidate_s_sw_campaign_2024/research_numerical_extractor.py":
        "95b2f3b53609a6e420a18692b4b0e3927cb47841d9e1200cce04677094a5950e",
    "experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_123_ORIGIN_RESULTS.csv":
        "8c13b904e286e25167a8eca5144e545627b6c598f36716e93fcf9ee95a2ab57e",
    "experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_123_ORIGIN_HOURLY_TELEMETRY.csv":
        "6b3636d7ae4d596016f4e7b3b5fc63e9a26e374041b586b619b49afc2eec7d2e",
    "experiments/STAGE4_2025_SW_LOW_SUN_RESEARCH_FREEZE.md":
        "e73558cfd03acd35fc55d24a055f7ccc6a31d0d973a3cc2e4443a8665ac21cd7",
    "experiments/STAGE4_2025_SW_LOW_SUN_RESEARCH_FREEZE.json":
        "6b0bb6f7af44ef06731180d50239de222f301fa571c5862d115f7644d3be7b87",
    "experiments/stage4_sw_low_sun_2025_holdout/STAGE4_123_ORIGIN_RESULTS.csv":
        "18d13dec71eab82919c900da52b5248699e4b5b8fa4c4ed8499aff494f4fa62b",
    "experiments/POST_STAGE4_GOVERNANCE_DECISION_RECORD.md":
        "d3239b3ac9209644606014d1d52e63d2c3103560771b9c6c42924942f93d977f",
    "data/POLARIS_v0_1_SITES_Nuolja_2025_hourly_SW_IN.csv":
        "d457facdbeb57b9c582b623c524c0f50717306ca083ab93028f1bd700d1e7a2e",
}

# Frozen corrected-reproduction artifacts that the paired D1/D2 comparisons read (G11: not modified).
CORRECTED_RESULTS_PATH = "experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_123_ORIGIN_RESULTS.csv"
CORRECTED_TELEMETRY_PATH = "experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_123_ORIGIN_HOURLY_TELEMETRY.csv"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_protected_hashes(repo: Path, pins: Dict[str, str] = None) -> List[str]:
    """Returns a list of mismatch messages (empty list = all protected artifacts intact)."""
    pins = PROTECTED_PINS if pins is None else pins
    out: List[str] = []
    for rel, expected in pins.items():
        p = Path(repo) / rel
        if not p.exists():
            out.append(f"missing: {rel}")
            continue
        got = sha256_file(p)
        if got != expected:
            out.append(f"hash mismatch: {rel}: {got} != {expected}")
    return out
