"""
Bounded, resumable batch runner over a list of origins, built on fetcher.fetch_one_origin.

CORRECTED (this revision): `max_requests` is enforced as a single, shared
`fetcher.AttemptBudget` across the ENTIRE batch -- every retry of every origin
consumes from the same budget. The previous revision capped only the number of
*origins started* (`len(results) >= config.max_requests`), which under-counted actual
outbound HTTP attempts whenever any origin retried. That gap is fixed here and is
covered by a regression test (tests/test_fetcher.py::
test_global_attempt_budget_caps_total_outbound_attempts_across_batch).

Enforces: max_requests (as total outbound attempts, via AttemptBudget), max_origins,
concurrency, a wall-clock deadline (max_runtime_s), rate limiting, and safe
interruption/resume (already-cached-OK origins are skipped on rerun; a
KeyboardInterrupt or deadline stops the loop without losing completed work, since every
completed origin's result is already persisted atomically by
fetcher.write_cache_atomic before the batch loop advances).

This module makes a network request only if every one of the following all hold:
  - FetcherConfig.network_opt_in is True
  - FetcherConfig.dry_run is False
  - the origin is not already a verified OK cache hit
  - the shared AttemptBudget has not been exhausted
"""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, List, Optional

from .fetcher import AttemptBudget, FetcherConfig, FetchStatus, ProvenanceRecord, fetch_one_origin


@dataclass
class BatchResult:
    attempted: List[ProvenanceRecord]
    skipped_over_bounds: List[datetime]
    stopped_early_reason: Optional[str]
    wall_time_s: float
    requested_origins: List[str]
    total_outbound_attempts_used: int
    max_outbound_attempts: int

    @property
    def pilot_complete(self) -> bool:
        """True only if EVERY requested origin (not merely every attempted one) ended
        with retrieval_status == OK. A batch that ran out of budget, hit the runtime
        deadline, or left any origin un-attempted or failed is NOT complete -- it must
        be reported as partial, never silently upgraded to success."""
        if len(self.attempted) != len(self.requested_origins):
            return False
        if self.skipped_over_bounds:
            return False
        return all(r.retrieval_status == FetchStatus.OK for r in self.attempted)

    def summary(self) -> dict:
        by_status: dict = {}
        for r in self.attempted:
            by_status[r.retrieval_status] = by_status.get(r.retrieval_status, 0) + 1
        return {
            "requested_origins": len(self.requested_origins),
            "attempted": len(self.attempted),
            "skipped_over_bounds": len(self.skipped_over_bounds),
            "by_status": by_status,
            "stopped_early_reason": self.stopped_early_reason,
            "wall_time_s": round(self.wall_time_s, 3),
            "total_outbound_attempts_used": self.total_outbound_attempts_used,
            "max_outbound_attempts": self.max_outbound_attempts,
            "pilot_complete": self.pilot_complete,
        }


class _RateLimiter:
    def __init__(self, per_second: float):
        self.min_interval = 1.0 / per_second if per_second > 0 else 0.0
        self._last = 0.0

    def wait(self) -> None:
        if self.min_interval <= 0:
            return
        now = time.monotonic()
        elapsed = now - self._last
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last = time.monotonic()


def run_batch(
    origins: List[datetime],
    config: FetcherConfig,
    *,
    fetch_fn: Callable[..., ProvenanceRecord] = fetch_one_origin,
    max_consecutive_failures: Optional[int] = None,
) -> BatchResult:
    """Processes up to config.max_origins origins, with a SINGLE shared AttemptBudget
    (sized config.max_requests) enforced across all of them and all of their retries.
    Returns as soon as any bound is hit, with everything completed so far already
    durably cached. `requested_origins` on the result always reflects the full,
    explicit, fixed-before-the-run origin list passed in -- it is never expanded
    during the run (a retry can consume budget but can never add a new origin).

    `max_consecutive_failures`, if given, is a circuit breaker: if that many origins
    IN A ROW (excluding cache hits, which are not network activity) end in a non-OK
    status, the run stops immediately rather than continuing to burn the attempt
    budget against what is very likely a systemic problem (server outage, a changed
    response format, sustained throttling) rather than origin-specific noise."""
    start = time.monotonic()
    bounded_origins = origins[: config.max_origins]
    skipped = list(origins[config.max_origins :])
    limiter = _RateLimiter(config.rate_limit_per_s)
    budget = AttemptBudget(config.max_requests)
    results: List[ProvenanceRecord] = []
    stopped_reason: Optional[str] = None
    consecutive_failures = 0

    def _one(o: datetime) -> ProvenanceRecord:
        limiter.wait()
        return fetch_fn(o, config, budget=budget)

    try:
        if config.concurrency == 1:
            for o in bounded_origins:
                if time.monotonic() - start > config.max_runtime_s:
                    stopped_reason = "max_runtime_s deadline reached"
                    break
                if budget.remaining <= 0 and read_cache_miss_would_need_network(o, config):
                    stopped_reason = "max_requests (outbound attempt budget) exhausted"
                    break
                rec = _one(o)
                results.append(rec)
                if rec.cache_status == FetchStatus.CACHE_HIT:
                    consecutive_failures = 0
                elif rec.retrieval_status == FetchStatus.OK:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    if max_consecutive_failures is not None and consecutive_failures >= max_consecutive_failures:
                        stopped_reason = (
                            f"circuit breaker: {consecutive_failures} consecutive non-OK "
                            f"results (>= max_consecutive_failures={max_consecutive_failures}); "
                            f"stopping rather than continuing against a likely systemic failure"
                        )
                        break
        else:
            with ThreadPoolExecutor(max_workers=config.concurrency) as pool:
                futures = {pool.submit(_one, o): o for o in bounded_origins}
                for fut in as_completed(futures):
                    if time.monotonic() - start > config.max_runtime_s:
                        stopped_reason = stopped_reason or "max_runtime_s deadline reached"
                        break
                    results.append(fut.result())
    except KeyboardInterrupt:
        stopped_reason = "interrupted (KeyboardInterrupt) -- completed results already persisted via atomic cache writes"

    return BatchResult(
        attempted=results, skipped_over_bounds=skipped,
        stopped_early_reason=stopped_reason, wall_time_s=time.monotonic() - start,
        requested_origins=[o.isoformat() for o in bounded_origins],
        total_outbound_attempts_used=budget.used, max_outbound_attempts=budget.max_attempts,
    )


def read_cache_miss_would_need_network(origin: datetime, config: FetcherConfig) -> bool:
    """Cheap pre-check so a batch that has already exhausted its network budget can
    still correctly report cache hits as complete, rather than refusing to even check
    the cache for the remaining origins."""
    from .fetcher import read_cache

    cached = read_cache(config, origin)
    return not (cached is not None and cached.get("retrieval_status") == FetchStatus.OK)
