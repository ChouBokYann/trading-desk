#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Tests for record_regime.py."""

import sqlite3
import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(
    0,
    str(
        Path(__file__).parent.parent.parent.parent
        / "tm-setup"
        / "scripts"
    ),
)
from record_regime import record_regime
from init_db import init_database


class TestRecordRegime(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.db_path = Path(self.tmpdir) / "test.db"
        init_database(self.db_path)

    def test_record_basic_regime(self):
        regime = {
            "macro": "bull",
            "macro_confidence": 0.8,
            "flag": "green",
            "vix": 15.5,
            "yield_curve_spread": 1.2,
            "breadth_score": 0.72,
            "distribution_days": 2,
            "safety_car": False,
        }
        result = record_regime(self.db_path, regime)
        self.assertEqual(result["status"], "pass")
        self.assertGreater(result["row_id"], 0)

    def test_record_with_sectors(self):
        regime = {
            "macro": "sideways",
            "macro_confidence": 0.5,
            "flag": "yellow",
            "sectors": {"leading": ["XLK", "XLY"], "lagging": ["XLE"]},
            "r0_leading_sectors": {"technology": 1.3, "energy": 0.7},
        }
        result = record_regime(self.db_path, regime)
        self.assertEqual(result["status"], "pass")

        conn = sqlite3.connect(str(self.db_path))
        row = conn.execute(
            "SELECT sector_data, r0_data FROM regime_history WHERE id = ?",
            (result["row_id"],),
        ).fetchone()
        conn.close()

        self.assertIn("XLK", row[0])
        self.assertIn("technology", row[1])

    def test_record_safety_car(self):
        regime = {
            "macro": "bear",
            "macro_confidence": 0.9,
            "flag": "black",
            "safety_car": True,
            "vix": 35.0,
            "notes": "VIX spike above 30",
        }
        result = record_regime(self.db_path, regime)

        conn = sqlite3.connect(str(self.db_path))
        row = conn.execute(
            "SELECT safety_car, flag_level, notes FROM regime_history WHERE id = ?",
            (result["row_id"],),
        ).fetchone()
        conn.close()

        self.assertEqual(row[0], 1)
        self.assertEqual(row[1], "black")
        self.assertIn("VIX", row[2])

    def test_multiple_records(self):
        for flag in ["green", "yellow", "red"]:
            record_regime(
                self.db_path,
                {"macro": "bull", "macro_confidence": 0.5, "flag": flag},
            )

        conn = sqlite3.connect(str(self.db_path))
        count = conn.execute("SELECT COUNT(*) FROM regime_history").fetchone()[0]
        conn.close()

        self.assertEqual(count, 3)


if __name__ == "__main__":
    unittest.main()
