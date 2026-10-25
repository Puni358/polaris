"""Offline tests for CLI origin selection. No network. Regression coverage for the bug
found during the Phase 1 safety review: an earlier revision duplicated a single origin
`origin_count` times instead of selecting distinct origins from the local inventory."""
import pytest

from .. import cli as C
from .. import fetcher as F
from .. import planner as P


def test_select_pilot_origins_returns_five_distinct_real_origins():
    origins = C.select_pilot_origins("2024-01-20", 5)
    assert len(origins) == 5
    assert len(set(o.isoformat() for o in origins)) == 5, "origins must be distinct, not repeated"


def test_select_pilot_origins_each_maps_to_correct_prior_day_18z_run():
    origins = C.select_pilot_origins("2024-01-20", 5)
    for o in origins:
        run_init = F.run_init_time_for_origin(o)
        assert run_init.hour == 18
        assert run_init.date() == (o - __import__("datetime").timedelta(days=1)).date()
        assert run_init == o - __import__("datetime").timedelta(hours=6)


def test_select_pilot_origins_are_drawn_from_local_inventory_not_assumed_consecutive():
    inventory = set(P._load_local_origins(P.MATRIX_2024)) | set(P._load_local_origins(P.MATRIX_2025))
    origins = C.select_pilot_origins("2024-01-20", 5)
    for o in origins:
        assert o.strftime("%Y-%m-%d %H:%M:%S+00:00") in inventory, \
            "every selected origin must be a real local-inventory origin, not a fabricated consecutive date"


def test_select_pilot_origins_raises_if_not_enough_available():
    with pytest.raises(ValueError):
        C.select_pilot_origins("2099-01-01", 5)
