"""
Offline-only tests for the Candidate F successor 18Z fetcher.

NONE of these tests make a real network call. Every HTTP-shaped interaction is
monkeypatched or injected via the `_urlopen` parameter / fixture ASCII text. Running
this file performs zero network I/O -- verified by asserting a call counter stays at 0
in every test that could plausibly reach the network path, and by never setting
network_opt_in=True with a real urlopen.
"""
import json
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from .. import fetcher as F
from .. import batch_runner as B
from . import fixtures as fx


@pytest.fixture()
def tmp_cache_dir():
    d = Path(tempfile.mkdtemp(prefix="cf18z_test_cache_"))
    yield d
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture()
def cfg(tmp_cache_dir):
    return F.FetcherConfig(cache_dir=tmp_cache_dir, max_requests=50, max_origins=50)


# ---------------------------------------------------------------------------- URL construction
def test_url_construction_prior_day_18z():
    origin = datetime(2024, 1, 20, 0, 0, 0, tzinfo=timezone.utc)
    url, run_init = F.full_request_url(origin)
    assert run_init == datetime(2024, 1, 19, 18, 0, 0, tzinfo=timezone.utc)
    assert "meps25epsarchive/2024/01/19/meps_det_pl_20240119T18Z.ncml.ascii" in url
    assert F.LWP_VAR in url and F.IWP_VAR in url
    # brackets are percent-encoded (see test_url_construction_percent_encodes_dods_brackets);
    # check the encoded form, not the literal '[' ']'.
    assert f"%5B{F.P700_IDX}:1:{F.P700_IDX}%5D" in url
    assert f"%5B{F.NUOLJA_Y}:1:{F.NUOLJA_Y}%5D" in url and f"%5B{F.NUOLJA_X}:1:{F.NUOLJA_X}%5D" in url


def test_url_construction_percent_encodes_dods_brackets():
    """REGRESSION TEST for a live-pilot-discovered bug: an earlier revision placed
    literal `[`/`]` characters in the query string, which the real THREDDS server
    rejected with HTTP 400 (confirmed via a live, read-only diagnostic request during
    this investigation; the identical, properly percent-encoded URL below was
    separately confirmed via `curl` to return HTTP 200 with a valid DODS response).
    This test pins the exact encoded form so the bug cannot silently regress."""
    origin = datetime(2024, 1, 20, 0, 0, 0, tzinfo=timezone.utc)
    url, _ = F.full_request_url(origin)
    assert "[" not in url and "]" not in url, "raw brackets must never appear in the final URL"
    expected = (
        "https://thredds.met.no/thredds/dodsC/meps25epsarchive/2024/01/19/"
        "meps_det_pl_20240119T18Z.ncml.ascii?"
        "mass_fraction_of_cloud_condensed_water_in_air_pl%5B0:1:30%5D%5B8:1:8%5D%5B760:1:760%5D%5B486:1:486%5D,"
        "mass_fraction_of_cloud_ice_in_air_pl%5B0:1:30%5D%5B8:1:8%5D%5B760:1:760%5D%5B486:1:486%5D,"
        "pressure%5B8:1:8%5D,forecast_reference_time,time%5B0:1:30%5D"
    )
    assert url == expected


def test_url_construction_year_boundary():
    """Origin on Jan 1 must select the prior year's Dec 31 18Z run."""
    origin = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    url, run_init = F.full_request_url(origin)
    assert run_init == datetime(2024, 12, 31, 18, 0, 0, tzinfo=timezone.utc)
    assert "meps25epsarchive/2024/12/31/meps_det_pl_20241231T18Z.ncml.ascii" in url


def test_run_init_rejects_non_00z_origin():
    """The contract assumes a 00:00 UTC origin; a non-midnight origin does not map to
    an admissible 18Z run 6h prior and must be refused, not silently miscalculated."""
    bad_origin = datetime(2024, 1, 20, 3, 0, 0, tzinfo=timezone.utc)
    with pytest.raises(F.FetcherError):
        F.run_init_time_for_origin(bad_origin)


# ---------------------------------------------------------------------------- validation: valid case
def test_parse_ascii_series_handles_real_inline_scalar_format():
    """REGRESSION TEST for the bug found during the live re-pilot, 2026-10-12: a real
    DODS scalar is rendered inline as "var_name, value" on one line (confirmed via a
    real response captured during this investigation: "forecast_reference_time,
    1.7056872E9"), not as the header-then-value-line pattern array/grid variables use.
    The first live pilot run (post URL-encoding fix) got HTTP 200 responses but still
    failed every origin with FAILED_MISSING_VAR because this format was unhandled."""
    real_snippet = "forecast_reference_time, 1.7056872E9\npressure[1]\n700.0"
    result = F.parse_ascii_series(real_snippet, "forecast_reference_time", 1)
    assert result is not None
    assert abs(float(result[0]) - 1.7056872e9) < 1.0


def test_validate_response_accepts_well_formed_data():
    text = fx.make_valid_ascii()
    status, payload, detail = F.validate_response(
        ascii_text=text, forecast_start=fx.ORIGIN, run_init=fx.RUN_INIT
    )
    assert status == F.FetchStatus.OK, detail
    assert len(payload["per_horizon"]) == 24
    h1 = payload["per_horizon"][0]
    assert h1["horizon_hour"] == 1 and h1["lead_hour"] == 7
    assert h1["valid_time_utc"] == (fx.ORIGIN + timedelta(hours=1)).isoformat()


def test_validate_response_accepts_genuine_zero_values_as_ok():
    """Zero is a valid physical value (clear air) and must NOT be treated as missing."""
    text = fx.make_zero_value_ascii()
    status, payload, detail = F.validate_response(
        ascii_text=text, forecast_start=fx.ORIGIN, run_init=fx.RUN_INIT
    )
    assert status == F.FetchStatus.OK, detail
    assert all(h["lwp_mass_fraction"] == 0.0 for h in payload["per_horizon"])
    assert all(h["iwp_mass_fraction"] == 0.0 for h in payload["per_horizon"])


# ---------------------------------------------------------------------------- validation: failure modes
def test_validate_response_rejects_empty_response():
    status, payload, detail = F.validate_response(
        ascii_text=fx.make_empty_ascii(), forecast_start=fx.ORIGIN, run_init=fx.RUN_INIT
    )
    assert status == F.FetchStatus.FAILED_PARSE
    assert payload is None


def test_validate_response_rejects_missing_variable():
    status, payload, detail = F.validate_response(
        ascii_text=fx.make_missing_variable_ascii(), forecast_start=fx.ORIGIN, run_init=fx.RUN_INIT
    )
    assert status == F.FetchStatus.FAILED_MISSING_VAR
    assert payload is None


def test_validate_response_rejects_wrong_run():
    """A response whose forecast_reference_time does not match the required run must
    never be silently accepted -- this is the core causality admissibility gate."""
    status, payload, detail = F.validate_response(
        ascii_text=fx.make_wrong_run_ascii(), forecast_start=fx.ORIGIN, run_init=fx.RUN_INIT
    )
    assert status == F.FetchStatus.FAILED_RUN_MISMATCH
    assert payload is None


def test_validate_response_rejects_duplicate_timestamps():
    status, payload, detail = F.validate_response(
        ascii_text=fx.make_duplicate_time_ascii(), forecast_start=fx.ORIGIN, run_init=fx.RUN_INIT
    )
    assert status == F.FetchStatus.FAILED_DUPLICATE_TIME
    assert payload is None


def test_validate_response_rejects_nonfinite_values():
    status, payload, detail = F.validate_response(
        ascii_text=fx.make_nonfinite_ascii(), forecast_start=fx.ORIGIN, run_init=fx.RUN_INIT
    )
    assert status == F.FetchStatus.FAILED_NONFINITE
    assert payload is None


def test_validate_response_rejects_insufficient_horizon_coverage():
    """A too-short time/variable array must never be silently truncated or padded --
    it must fail closed. (The exact failure code may be FAILED_DIM_MISMATCH or
    FAILED_HORIZON_OUT_OF_RANGE depending on where the shared parser's scan first
    detects the inconsistency; both are acceptable FAIL outcomes, OK is not.)"""
    status, payload, detail = F.validate_response(
        ascii_text=fx.make_short_time_ascii(), forecast_start=fx.ORIGIN, run_init=fx.RUN_INIT
    )
    assert status != F.FetchStatus.OK, f"must not silently accept short/insufficient data, got {status}: {detail}"
    assert payload is None


def test_validate_response_rejects_invalid_origin_to_valid_time_mapping():
    """If forecast_start is perturbed relative to run_init in a way that breaks the
    expected h -> (6+h) lead-hour mapping, validation must fail, not misalign."""
    text = fx.make_valid_ascii()
    wrong_origin = fx.ORIGIN + timedelta(hours=1)  # no longer run_init + 6h
    status, payload, detail = F.validate_response(
        ascii_text=text, forecast_start=wrong_origin, run_init=fx.RUN_INIT
    )
    assert status != F.FetchStatus.OK


# ---------------------------------------------------------------------------- cache identity & resume
def test_cache_key_distinguishes_different_origins():
    o1 = datetime(2024, 1, 20, 0, 0, 0, tzinfo=timezone.utc)
    o2 = datetime(2024, 1, 21, 0, 0, 0, tzinfo=timezone.utc)
    assert F.cache_key(o1) != F.cache_key(o2)


def test_cache_key_stable_for_same_origin():
    o1 = datetime(2024, 1, 20, 0, 0, 0, tzinfo=timezone.utc)
    assert F.cache_key(o1) == F.cache_key(o1)


def test_atomic_write_then_read_round_trip(cfg):
    record = {"forecast_start": fx.ORIGIN.isoformat(), "retrieval_status": F.FetchStatus.OK,
              "payload": {"pressure_hpa": 700.0, "per_horizon": []}, "content_sha256": "deadbeef", "detail": "ok"}
    F.write_cache_atomic(cfg, fx.ORIGIN, record)
    cache_path = cfg.cache_dir / f"{F.cache_key(fx.ORIGIN)}.json"
    assert cache_path.exists()
    # no stray .tmp file left behind
    assert not any(cfg.cache_dir.glob("*.tmp"))
    reread = F.read_cache(cfg, fx.ORIGIN)
    assert reread["retrieval_status"] == F.FetchStatus.OK
    assert reread["content_sha256"] == "deadbeef"


def test_read_cache_rejects_incompatible_cache_entry(cfg):
    """A cache file whose stored cache_key does not match the identity recomputed for
    the current query parameters must be rejected, not reused."""
    key = F.cache_key(fx.ORIGIN)
    path = cfg.cache_dir / f"{key}.json"
    cfg.cache_dir.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as fp:
        json.dump({"cache_key": "WRONG_KEY_DOES_NOT_MATCH", "retrieval_status": F.FetchStatus.OK}, fp)
    result = F.read_cache(cfg, fx.ORIGIN)
    assert result is None


def test_fetch_one_origin_uses_cache_hit_without_any_fetch_call(cfg):
    """Once a verified OK cache entry exists, fetch_one_origin must not attempt any
    network path at all -- demonstrated by never providing a working `_urlopen` and
    still getting a correct CACHE_HIT result."""
    payload = {"pressure_hpa": 700.0, "per_horizon": [
        {"horizon_hour": 1, "lead_hour": 7, "valid_time_utc": (fx.ORIGIN + timedelta(hours=1)).isoformat(),
         "lwp_mass_fraction": 0.0001, "iwp_mass_fraction": 0.00005},
    ]}
    F.write_cache_atomic(cfg, fx.ORIGIN, {
        "forecast_start": fx.ORIGIN.isoformat(), "retrieval_status": F.FetchStatus.OK,
        "payload": payload, "content_sha256": "abc123", "detail": "validated",
    })

    def _poison_urlopen(*a, **k):  # would raise if ever called
        raise AssertionError("network path reached despite an available cache hit")

    rec = F.fetch_one_origin(fx.ORIGIN, cfg, _urlopen=_poison_urlopen)
    assert rec.retrieval_status == F.FetchStatus.OK
    assert rec.cache_status == F.FetchStatus.CACHE_HIT


# ---------------------------------------------------------------------------- dry-run / network authorization
def test_dry_run_default_makes_zero_network_calls(cfg):
    """FetcherConfig() defaults to dry_run=True, network_opt_in=False. Calling
    fetch_one_origin under these defaults must never reach the network path."""
    call_count = {"n": 0}

    def _poison_urlopen(*a, **k):
        call_count["n"] += 1
        raise AssertionError("network path reached during dry-run")

    rec = F.fetch_one_origin(fx.ORIGIN, cfg, _urlopen=_poison_urlopen)
    assert call_count["n"] == 0
    assert rec.retrieval_status == F.FetchStatus.FAILED_NETWORK_NOT_AUTHORIZED


def test_network_opt_in_alone_without_dry_run_false_still_blocks(tmp_cache_dir):
    cfg = F.FetcherConfig(cache_dir=tmp_cache_dir, network_opt_in=True, dry_run=True)
    call_count = {"n": 0}

    def _poison_urlopen(*a, **k):
        call_count["n"] += 1
        raise AssertionError("should never be called")

    rec = F.fetch_one_origin(fx.ORIGIN, cfg, _urlopen=_poison_urlopen)
    assert call_count["n"] == 0
    assert rec.retrieval_status == F.FetchStatus.FAILED_NETWORK_NOT_AUTHORIZED


def test_fetch_one_origin_with_mocked_network_success(tmp_cache_dir):
    """Only test that exercises the 'network' branch, and it is fully mocked: a fake
    opener object returns fixture text, no socket is ever touched."""
    cfg = F.FetcherConfig(cache_dir=tmp_cache_dir, network_opt_in=True, dry_run=False, max_retries=1)

    class _FakeResp:
        status = 200

        def __init__(self, text):
            self._text = text.encode("utf-8")

        def read(self):
            return self._text

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def _fake_urlopen(req, timeout):
        return _FakeResp(fx.make_valid_ascii())

    rec = F.fetch_one_origin(fx.ORIGIN, cfg, _urlopen=_fake_urlopen)
    assert rec.retrieval_status == F.FetchStatus.OK
    assert rec.content_sha256 is not None
    # second call must now be served from cache, not the (still-mocked) network
    called = {"n": 0}

    def _poison(*a, **k):
        called["n"] += 1
        raise AssertionError("should have used cache on second call")

    rec2 = F.fetch_one_origin(fx.ORIGIN, cfg, _urlopen=_poison)
    assert called["n"] == 0
    assert rec2.cache_status == F.FetchStatus.CACHE_HIT


def test_fetch_one_origin_with_mocked_http_failure_records_failed_status(tmp_cache_dir):
    cfg = F.FetcherConfig(cache_dir=tmp_cache_dir, network_opt_in=True, dry_run=False,
                           max_retries=2, backoff_base_s=0.0)

    def _always_fail(req, timeout):
        raise OSError("mocked connection failure, not a real network attempt")

    rec = F.fetch_one_origin(fx.ORIGIN, cfg, _urlopen=_always_fail)
    assert rec.retrieval_status.startswith(F.FetchStatus.FAILED_HTTP)


# ---------------------------------------------------------------------------- bounds: max_requests / max_origins / runtime
def test_batch_runner_respects_max_origins(tmp_cache_dir):
    cfg = F.FetcherConfig(cache_dir=tmp_cache_dir, max_origins=2, max_requests=50,
                           network_opt_in=False, dry_run=True)
    origins = [fx.ORIGIN + timedelta(days=i) for i in range(10)]
    result = B.run_batch(origins, cfg)
    assert len(result.attempted) == 2
    assert len(result.skipped_over_bounds) == 8


def test_batch_runner_max_requests_is_a_vacuous_bound_under_dry_run(tmp_cache_dir):
    """Dry-run makes zero outbound attempts by construction, so the attempt budget is
    never consumed and never the reason processing stops; all origins (bounded only by
    max_origins) are processed, each refused for lack of network authorization."""
    cfg = F.FetcherConfig(cache_dir=tmp_cache_dir, max_origins=50, max_requests=3,
                           network_opt_in=False, dry_run=True)
    origins = [fx.ORIGIN + timedelta(days=i) for i in range(10)]
    result = B.run_batch(origins, cfg)
    assert len(result.attempted) == 10
    assert all(r.retrieval_status == F.FetchStatus.FAILED_NETWORK_NOT_AUTHORIZED for r in result.attempted)
    assert result.total_outbound_attempts_used == 0


def test_global_attempt_budget_caps_total_outbound_attempts_across_batch(tmp_cache_dir):
    """THE KEY REGRESSION TEST for the bug found during the Phase 2 safety review: a
    naive implementation capped the number of ORIGINS started by max_requests, which
    under-counts real outbound attempts whenever any origin retries. Here every mocked
    request fails (forcing max_retries=3 attempts per origin if unbounded), 5 origins
    are requested, and max_requests=5 -- if the cap were origin-count-based, up to
    5 origins x 3 retries = 15 real attempts could occur; the fix must cap TOTAL
    attempts, including retries, at exactly 5."""
    cfg = F.FetcherConfig(cache_dir=tmp_cache_dir, network_opt_in=True, dry_run=False,
                           max_origins=5, max_requests=5, max_retries=3,
                           backoff_base_s=0.0, concurrency=1)
    call_log = []

    def _always_fail(req, timeout):
        call_log.append(req.full_url)
        raise OSError("mocked failure -- every attempt fails, forcing max retries")

    origins = [fx.ORIGIN + timedelta(days=i) for i in range(5)]
    result = B.run_batch(origins, cfg, fetch_fn=lambda o, c, budget=None: F.fetch_one_origin(
        o, c, _urlopen=_always_fail, budget=budget
    ))
    assert len(call_log) == 5, f"expected exactly 5 real outbound attempts total, got {len(call_log)}"
    assert result.total_outbound_attempts_used == 5
    assert result.max_outbound_attempts == 5
    assert not result.pilot_complete
    statuses = {r.retrieval_status for r in result.attempted}
    assert F.FetchStatus.FAILED_BUDGET_EXHAUSTED in statuses or len(result.attempted) < 5


def test_global_attempt_budget_allows_full_retries_for_fewer_origins_within_cap(tmp_cache_dir):
    """Sanity check in the other direction: if the budget is generous enough (5
    origins x 1 retry each = 5 <= max_requests=10), every origin should still get its
    own attempt and the budget should not spuriously starve early origins."""
    cfg = F.FetcherConfig(cache_dir=tmp_cache_dir, network_opt_in=True, dry_run=False,
                           max_origins=5, max_requests=10, max_retries=1,
                           backoff_base_s=0.0, concurrency=1)
    call_log = []

    def _always_fail(req, timeout):
        call_log.append(req.full_url)
        raise OSError("mocked failure")

    origins = [fx.ORIGIN + timedelta(days=i) for i in range(5)]
    result = B.run_batch(origins, cfg, fetch_fn=lambda o, c, budget=None: F.fetch_one_origin(
        o, c, _urlopen=_always_fail, budget=budget
    ))
    assert len(call_log) == 5
    assert len(result.attempted) == 5
    assert result.total_outbound_attempts_used == 5


def test_batch_runner_respects_runtime_deadline(tmp_cache_dir):
    cfg = F.FetcherConfig(cache_dir=tmp_cache_dir, max_origins=50, max_requests=50,
                           network_opt_in=False, dry_run=True, max_runtime_s=0.0)
    origins = [fx.ORIGIN + timedelta(days=i) for i in range(5)]
    result = B.run_batch(origins, cfg)
    assert result.stopped_early_reason == "max_runtime_s deadline reached"
    assert len(result.attempted) == 0


def test_batch_runner_makes_zero_network_calls_in_dry_run(tmp_cache_dir):
    cfg = F.FetcherConfig(cache_dir=tmp_cache_dir, max_origins=5, max_requests=5,
                           network_opt_in=False, dry_run=True)
    origins = [fx.ORIGIN + timedelta(days=i) for i in range(5)]
    result = B.run_batch(origins, cfg)
    assert all(r.retrieval_status == F.FetchStatus.FAILED_NETWORK_NOT_AUTHORIZED for r in result.attempted)


def test_circuit_breaker_stops_on_sustained_consecutive_failures(tmp_cache_dir):
    """Required for the full 711-origin acquisition: if a systemic problem (outage,
    format change, throttling) causes many origins in a row to fail, the run must stop
    well before exhausting the whole attempt budget, rather than burning through it."""
    cfg = F.FetcherConfig(cache_dir=tmp_cache_dir, network_opt_in=True, dry_run=False,
                           max_origins=50, max_requests=50, max_retries=1, backoff_base_s=0.0)

    def _always_fail(req, timeout):
        raise OSError("mocked systemic failure")

    origins = [fx.ORIGIN + timedelta(days=i) for i in range(50)]
    result = B.run_batch(
        origins, cfg,
        fetch_fn=lambda o, c, budget=None: F.fetch_one_origin(o, c, _urlopen=_always_fail, budget=budget),
        max_consecutive_failures=5,
    )
    assert len(result.attempted) == 5, "must stop at exactly 5 consecutive failures, not continue to 50"
    assert result.stopped_early_reason is not None and "circuit breaker" in result.stopped_early_reason
    assert result.total_outbound_attempts_used < 50, "budget must not be exhausted; circuit breaker should trip first"


def test_circuit_breaker_resets_on_success(tmp_cache_dir):
    """A circuit breaker that never resets would stop a long run after a handful of
    transient failures anywhere in its history. It must only count a CONSECUTIVE run of
    failures, resetting on any success. Tests run_batch's bookkeeping directly via a
    canned fetch_fn (fetch_one_origin's own OK/FAILED correctness is covered by other
    tests) -- failures 3-in-a-row, then one success, repeating, so the consecutive
    count never reaches the breaker's threshold of 5."""
    cfg = F.FetcherConfig(cache_dir=tmp_cache_dir, max_origins=50, max_requests=50)
    call_n = {"n": 0}

    def _canned(o, c, budget=None):
        call_n["n"] += 1
        status = F.FetchStatus.OK if call_n["n"] % 4 == 0 else F.FetchStatus.FAILED_HTTP + "_500"
        return F.ProvenanceRecord(
            forecast_start=o.isoformat(), run_init_time_utc="x", product="meps_det_pl",
            url="x", variables=[], pressure_hpa=None, valid_times_utc=[], lead_hours=[],
            retrieval_status=status, cache_status=F.FetchStatus.PENDING, units={},
            validation_outcome="canned for circuit-breaker bookkeeping test",
        )

    origins = [fx.ORIGIN + timedelta(days=i) for i in range(12)]
    result = B.run_batch(origins, cfg, fetch_fn=_canned, max_consecutive_failures=5)
    assert result.stopped_early_reason is None, "breaker must not trip when failures never run 5 in a row"
    assert len(result.attempted) == 12


def test_config_rejects_invalid_concurrency(tmp_cache_dir):
    with pytest.raises(F.FetcherError):
        F.FetcherConfig(cache_dir=tmp_cache_dir, concurrency=0)


# ---------------------------------------------------------------------------- determinism
def test_provenance_record_is_deterministic_for_same_input(tmp_cache_dir):
    cfg1 = F.FetcherConfig(cache_dir=tmp_cache_dir)
    cfg2 = F.FetcherConfig(cache_dir=tmp_cache_dir)
    rec1 = F.fetch_one_origin(fx.ORIGIN, cfg1)
    rec2 = F.fetch_one_origin(fx.ORIGIN, cfg2)
    assert rec1.to_dict() == rec2.to_dict()
