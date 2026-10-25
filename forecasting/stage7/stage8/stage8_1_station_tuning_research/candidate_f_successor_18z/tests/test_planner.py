"""Offline tests for the acquisition planner. Verifies plan-only mode makes no network
call, mutates no cache, and never writes a feature matrix or touches experiment state."""
import shutil
import tempfile
from pathlib import Path

from .. import planner as P
from .. import fetcher as F


def test_plan_reads_local_matrices_without_network(monkeypatch):
    """Guard against any accidental network call: monkeypatch urlopen to raise if ever
    invoked anywhere during plan()."""
    import urllib.request

    def _poison(*a, **k):
        raise AssertionError("planner must never touch the network")

    monkeypatch.setattr(urllib.request, "urlopen", _poison)
    result = P.plan()
    assert result.origins_2024 == 347
    assert result.origins_2025 == 364
    assert result.origins_total == 711
    assert result.total_requests == 711


def test_plan_does_not_mutate_cache_dir():
    tmp_cache = Path(tempfile.mkdtemp(prefix="cf18z_plan_test_"))
    try:
        before = list(tmp_cache.iterdir())
        cfg = F.FetcherConfig(cache_dir=tmp_cache)
        P.plan(cfg)
        after = list(tmp_cache.iterdir())
        assert before == after == []
    finally:
        shutil.rmtree(tmp_cache, ignore_errors=True)


def test_plan_counts_cache_hits_when_entries_exist():
    tmp_cache = Path(tempfile.mkdtemp(prefix="cf18z_plan_test2_"))
    try:
        cfg = F.FetcherConfig(cache_dir=tmp_cache)
        origins_2024 = P._load_local_origins(P.MATRIX_2024)
        first_origin = P._parse_origin(origins_2024[0])
        F.write_cache_atomic(cfg, first_origin, {
            "forecast_start": first_origin.isoformat(), "retrieval_status": F.FetchStatus.OK,
            "payload": {"pressure_hpa": 700.0, "per_horizon": []}, "content_sha256": "x",
        })
        result = P.plan(cfg)
        assert result.cache_hits == 1
        assert result.cache_misses == result.origins_total - 1
    finally:
        shutil.rmtree(tmp_cache, ignore_errors=True)


def test_plan_output_is_json_serializable():
    import json

    result = P.plan()
    json.dumps(result.to_dict())  # must not raise
