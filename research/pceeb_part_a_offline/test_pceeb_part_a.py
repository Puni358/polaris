#!/usr/bin/env python3
"""
Focused, bounded unit tests for PCEEB Part (a)'s pure computational core
(empirical_quantile, prefix-sum-by-step, missing-data skip rule).

Scope: this test module exercises ONLY the functions in compute_pceeb_part_a.py
on small synthetic in-memory fixtures. It does NOT read the real historical
dataset, does NOT invoke replay_harness.py, does NOT run any campaign, and
does NOT touch any protected or production file. Run with:
    python3 -I -m unittest research/pceeb_part_a_offline/test_pceeb_part_a.py -v
"""

import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compute_pceeb_part_a import (  # noqa: E402
    empirical_quantile,
    _load_origin_sequences,
    _prefix_sums_by_step,
    _build_envelope,
)


class TestEmpiricalQuantile(unittest.TestCase):
    def test_median_of_odd_sequence(self):
        self.assertAlmostEqual(empirical_quantile([1.0, 2.0, 3.0, 4.0, 5.0], 0.5), 3.0)

    def test_median_of_even_sequence_interpolates(self):
        self.assertAlmostEqual(empirical_quantile([1.0, 2.0, 3.0, 4.0], 0.5), 2.5)

    def test_q0_and_q1_are_extremes(self):
        values = [10.0, 20.0, 30.0]
        self.assertAlmostEqual(empirical_quantile(values, 0.0), 10.0)
        self.assertAlmostEqual(empirical_quantile(values, 1.0), 30.0)

    def test_single_value_returns_itself_for_any_quantile(self):
        self.assertAlmostEqual(empirical_quantile([42.0], 0.1), 42.0)
        self.assertAlmostEqual(empirical_quantile([42.0], 0.9), 42.0)

    def test_empty_sequence_raises(self):
        with self.assertRaises(ValueError):
            empirical_quantile([], 0.5)

    def test_known_type7_value(self):
        # Type-7 quantile of [1..10] at q=0.25 is 1 + 0.25*9 = 3.25
        self.assertAlmostEqual(empirical_quantile(list(range(1, 11)), 0.25), 3.25)


class TestPrefixSumsByStep(unittest.TestCase):
    def test_prefix_sum_accumulates_in_horizon_order(self):
        sequences = {
            "origin_A": [(6, 1.0), (7, 2.0), (8, -0.5)],
        }
        step_to_values, step_to_horizons, per_origin = _prefix_sums_by_step(sequences)
        self.assertEqual(per_origin["origin_A"], [1.0, 3.0, 2.5])
        self.assertEqual(step_to_values[1], [1.0])
        self.assertEqual(step_to_values[2], [3.0])
        self.assertEqual(step_to_values[3], [2.5])
        self.assertEqual(step_to_horizons[1], [6])
        self.assertEqual(step_to_horizons[3], [8])

    def test_multiple_origins_pooled_at_each_step(self):
        sequences = {
            "origin_A": [(1, 2.0), (2, 2.0)],
            "origin_B": [(1, -1.0), (2, 5.0)],
        }
        step_to_values, _, per_origin = _prefix_sums_by_step(sequences)
        self.assertEqual(sorted(step_to_values[1]), [-1.0, 2.0])
        # origin_A: 2.0, then 2.0+2.0=4.0; origin_B: -1.0, then -1.0+5.0=4.0
        self.assertEqual(sorted(step_to_values[2]), [4.0, 4.0])
        self.assertEqual(per_origin["origin_A"], [2.0, 4.0])
        self.assertEqual(per_origin["origin_B"], [-1.0, 4.0])

    def test_different_length_sequences_only_contribute_where_present(self):
        sequences = {
            "origin_short": [(1, 1.0)],
            "origin_long": [(1, 1.0), (2, 1.0), (3, 1.0)],
        }
        step_to_values, _, _ = _prefix_sums_by_step(sequences)
        self.assertEqual(len(step_to_values[1]), 2)
        self.assertEqual(len(step_to_values[2]), 1)
        self.assertEqual(len(step_to_values[3]), 1)


class TestBuildEnvelope(unittest.TestCase):
    def test_envelope_quantiles_match_direct_computation(self):
        step_to_values = {1: [1.0, 2.0, 3.0, 4.0, 5.0]}
        step_to_horizons = {1: [6, 6, 6, 6, 6]}
        envelope = _build_envelope(step_to_values, step_to_horizons)
        self.assertEqual(envelope["1"]["n_origins"], 5)
        self.assertAlmostEqual(envelope["1"]["quantiles_wh_m2"]["q50"], 3.0)
        self.assertAlmostEqual(envelope["1"]["min_wh_m2"], 1.0)
        self.assertAlmostEqual(envelope["1"]["max_wh_m2"], 5.0)

    def test_envelope_is_monotonic_sample_size_non_increasing_when_sequences_vary(self):
        step_to_values = {1: [0.0, 0.0, 0.0], 2: [0.0, 0.0]}
        step_to_horizons = {1: [1, 1, 1], 2: [2, 2]}
        envelope = _build_envelope(step_to_values, step_to_horizons)
        self.assertGreaterEqual(envelope["1"]["n_origins"], envelope["2"]["n_origins"])


class TestLoadOriginSequencesMissingDataRule(unittest.TestCase):
    def test_nonnumeric_row_is_skipped_and_counted(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "fixture.csv"
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["origin", "horizon", "prediction", "actual", "residual"])
                writer.writerow(["o1", "1", "1.0", "2.0", "1.0"])
                writer.writerow(["o1", "2", "NaN", "2.0", "NaN"])  # malformed -> skipped
                writer.writerow(["o2", "1", "3.0", "3.0", "0.0"])

            sequences, skipped = _load_origin_sequences(
                csv_path, "origin", "horizon", "prediction", "actual", "residual"
            )
            self.assertEqual(skipped, 1)
            self.assertEqual(sequences["o1"], [(1, 1.0)])
            self.assertEqual(sequences["o2"], [(1, 0.0)])

    def test_residual_computed_when_no_residual_column(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "fixture.csv"
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["origin_id", "horizon", "y_pred", "y_true"])
                writer.writerow(["1", "1", "5.0", "7.0"])

            sequences, skipped = _load_origin_sequences(
                csv_path, "origin_id", "horizon", "y_pred", "y_true", None
            )
            self.assertEqual(skipped, 0)
            # realized minus forecast = y_true - y_pred = 7.0 - 5.0 = 2.0
            self.assertEqual(sequences["1"], [(1, 2.0)])


if __name__ == "__main__":
    unittest.main()
