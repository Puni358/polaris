#!/usr/bin/env python3
"""
Focused, bounded unit tests for the EVID-03 reserve-margin analysis's pure
computational core (empirical_quantile, prefix-sum-by-step, overestimate-event
statistics, unit-conversion helpers).

Scope: exercises ONLY the functions in compute_evid03_reserve_margin_analysis.py
on small synthetic in-memory fixtures. Does NOT read the real historical
dataset, does NOT invoke replay_harness.py, does NOT run any campaign, and
does NOT touch any protected or production file. Run with:
    python3 -I -m unittest research/evid03_reserve_margin_analysis/test_evid03_reserve_margin_analysis.py -v
"""

import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compute_evid03_reserve_margin_analysis import (  # noqa: E402
    empirical_quantile,
    _load_origin_sequences,
    _prefix_sums_by_step,
    overestimate_event_stats,
    wh_m2_quantiles_to_generation_wh,
    wh_as_pct_of_ebr_base,
    K_PV_W_PER_WM2,
    EBR_BASE_WH,
)


class TestEmpiricalQuantile(unittest.TestCase):
    def test_median_of_odd_sequence(self):
        self.assertAlmostEqual(empirical_quantile([1.0, 2.0, 3.0, 4.0, 5.0], 0.5), 3.0)

    def test_q0_and_q1_are_extremes(self):
        values = [10.0, 20.0, 30.0]
        self.assertAlmostEqual(empirical_quantile(values, 0.0), 10.0)
        self.assertAlmostEqual(empirical_quantile(values, 1.0), 30.0)

    def test_empty_sequence_raises(self):
        with self.assertRaises(ValueError):
            empirical_quantile([], 0.5)


class TestPrefixSumsByStep(unittest.TestCase):
    def test_prefix_sum_accumulates_in_horizon_order(self):
        sequences = {"origin_A": [(6, 1.0), (7, 2.0), (8, -0.5)]}
        step_to_values = _prefix_sums_by_step(sequences)
        self.assertEqual(step_to_values[1], [1.0])
        self.assertEqual(step_to_values[2], [3.0])
        self.assertEqual(step_to_values[3], [2.5])

    def test_multiple_origins_pooled_at_each_step(self):
        sequences = {
            "origin_A": [(1, 2.0), (2, 2.0)],
            "origin_B": [(1, -1.0), (2, 5.0)],
        }
        step_to_values = _prefix_sums_by_step(sequences)
        self.assertEqual(sorted(step_to_values[1]), [-1.0, 2.0])
        self.assertEqual(sorted(step_to_values[2]), [4.0, 4.0])


class TestOverestimateEventStats(unittest.TestCase):
    def test_no_negative_values_gives_zero_rate(self):
        stats = overestimate_event_stats([0.0, 1.0, 2.0, 3.0])
        self.assertEqual(stats["n_overestimate_events"], 0)
        self.assertAlmostEqual(stats["overestimate_event_rate"], 0.0)
        self.assertIsNone(stats["overestimate_magnitude_wh_m2_quantiles"])

    def test_all_negative_values_gives_rate_one(self):
        stats = overestimate_event_stats([-1.0, -2.0, -3.0])
        self.assertEqual(stats["n_overestimate_events"], 3)
        self.assertAlmostEqual(stats["overestimate_event_rate"], 1.0)
        self.assertAlmostEqual(stats["overestimate_magnitude_wh_m2_quantiles"]["q50"], 2.0)
        self.assertAlmostEqual(stats["overestimate_magnitude_wh_m2_max"], 3.0)

    def test_mixed_values_rate_and_magnitude(self):
        # 2 of 5 values negative: -4.0, -2.0 -> rate 0.4, magnitudes [2.0, 4.0]
        stats = overestimate_event_stats([5.0, -4.0, 0.0, 1.0, -2.0])
        self.assertEqual(stats["n_origins"], 5)
        self.assertEqual(stats["n_overestimate_events"], 2)
        self.assertAlmostEqual(stats["overestimate_event_rate"], 0.4)
        self.assertAlmostEqual(stats["overestimate_magnitude_wh_m2_mean"], 3.0)

    def test_empty_sample_handles_gracefully(self):
        stats = overestimate_event_stats([])
        self.assertEqual(stats["n_origins"], 0)
        self.assertIsNone(stats["overestimate_event_rate"])


class TestUnitConversionHelpers(unittest.TestCase):
    def test_wh_m2_to_generation_wh_applies_k_pv_linearly(self):
        quantiles = {"q05": -10.0, "q50": 0.0, "q95": 20.0}
        converted = wh_m2_quantiles_to_generation_wh(quantiles)
        self.assertAlmostEqual(converted["q05"], -10.0 * K_PV_W_PER_WM2)
        self.assertAlmostEqual(converted["q50"], 0.0)
        self.assertAlmostEqual(converted["q95"], 20.0 * K_PV_W_PER_WM2)

    def test_pct_of_ebr_base_scales_against_existing_constant(self):
        quantiles_wh = {"q50": EBR_BASE_WH / 2.0}
        pct = wh_as_pct_of_ebr_base(quantiles_wh)
        self.assertAlmostEqual(pct["q50"], 50.0)

    def test_k_pv_and_ebr_base_match_repository_constants(self):
        # These must match the EXISTING, independently hard-coded constants
        # in n6_solar.py / polaris_inference_runner.py exactly -- this test
        # guards against silent drift of the cited-not-invented values.
        self.assertEqual(K_PV_W_PER_WM2, 51.0)
        self.assertEqual(EBR_BASE_WH, 15000.0)


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
            self.assertEqual(sequences["1"], [(1, 2.0)])


if __name__ == "__main__":
    unittest.main()
