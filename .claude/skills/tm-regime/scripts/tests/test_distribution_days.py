#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Tests for distribution_days.py."""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from distribution_days import calculate_distribution_days


def make_day(date, open_, high, low, close, volume):
    return {
        "date": date,
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    }


class TestDistributionDays(unittest.TestCase):
    def test_no_distribution_days(self):
        data = [
            make_day("2026-01-01", 100, 102, 99, 101, 1000000),
            make_day("2026-01-02", 101, 103, 100, 102, 900000),
            make_day("2026-01-03", 102, 104, 101, 103, 800000),
        ]
        result = calculate_distribution_days(data)
        self.assertEqual(result["distribution_days"], 0)
        self.assertEqual(result["flag"], "green")

    def test_distribution_day_detected(self):
        data = [
            make_day("2026-01-01", 100, 102, 99, 100, 1000000),
            make_day("2026-01-02", 100, 101, 98, 99.5, 1200000),  # -0.5%, higher vol
        ]
        result = calculate_distribution_days(data)
        self.assertEqual(result["distribution_days"], 1)
        self.assertEqual(len(result["distribution_details"]), 1)
        self.assertAlmostEqual(
            result["distribution_details"][0]["pct_change"], -0.5, places=1
        )

    def test_no_distribution_if_volume_lower(self):
        data = [
            make_day("2026-01-01", 100, 102, 99, 100, 1200000),
            make_day("2026-01-02", 100, 101, 98, 99.5, 1000000),  # -0.5%, lower vol
        ]
        result = calculate_distribution_days(data)
        self.assertEqual(result["distribution_days"], 0)

    def test_no_distribution_if_small_drop(self):
        data = [
            make_day("2026-01-01", 100, 102, 99, 100, 1000000),
            make_day("2026-01-02", 100, 101, 99.5, 99.9, 1200000),  # -0.1%, higher vol
        ]
        result = calculate_distribution_days(data)
        self.assertEqual(result["distribution_days"], 0)

    def test_yellow_flag_at_4_days(self):
        data = [make_day("2026-01-01", 100, 102, 99, 100, 1000000)]
        for i in range(4):
            prev_close = data[-1]["close"]
            new_close = prev_close * 0.995  # -0.5%
            data.append(
                make_day(
                    f"2026-01-{i+2:02d}",
                    prev_close,
                    prev_close + 0.5,
                    new_close - 0.5,
                    new_close,
                    1000000 + (i + 1) * 100000,
                )
            )
        result = calculate_distribution_days(data)
        self.assertEqual(result["distribution_days"], 4)
        self.assertEqual(result["flag"], "yellow")

    def test_red_flag_at_6_days(self):
        data = [make_day("2026-01-01", 100, 102, 99, 100, 1000000)]
        for i in range(6):
            prev_close = data[-1]["close"]
            new_close = prev_close * 0.995
            data.append(
                make_day(
                    f"2026-01-{i+2:02d}",
                    prev_close,
                    prev_close + 0.5,
                    new_close - 0.5,
                    new_close,
                    1000000 + (i + 1) * 100000,
                )
            )
        result = calculate_distribution_days(data)
        self.assertEqual(result["distribution_days"], 6)
        self.assertEqual(result["flag"], "red")

    def test_stalling_day_detected(self):
        data = [
            make_day("2026-01-01", 100, 102, 99, 100, 1000000),
            make_day("2026-01-02", 100, 101, 99, 100.1, 1200000),  # +0.1%, upper half, higher vol
        ]
        result = calculate_distribution_days(data)
        self.assertEqual(result["stalling_days"], 1)

    def test_insufficient_data(self):
        data = [make_day("2026-01-01", 100, 102, 99, 100, 1000000)]
        result = calculate_distribution_days(data)
        self.assertEqual(result["distribution_days"], 0)
        self.assertIn("error", result)

    def test_lookback_window(self):
        data = [make_day("2026-01-01", 100, 102, 99, 100, 1000000)]
        for i in range(30):
            prev_close = data[-1]["close"]
            new_close = prev_close * 0.995
            data.append(
                make_day(
                    f"2026-01-{i+2:02d}",
                    prev_close,
                    prev_close + 0.5,
                    new_close - 0.5,
                    new_close,
                    1000000 + (i + 1) * 50000,
                )
            )
        result_25 = calculate_distribution_days(data, lookback=25)
        result_10 = calculate_distribution_days(data, lookback=10)
        self.assertGreater(
            result_25["distribution_days"], result_10["distribution_days"]
        )


if __name__ == "__main__":
    unittest.main()
