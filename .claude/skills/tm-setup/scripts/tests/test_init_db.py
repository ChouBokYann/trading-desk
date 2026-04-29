#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Tests for init_db.py."""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

sys_path = str(Path(__file__).parent.parent)
import sys

sys.path.insert(0, sys_path)
from init_db import SCHEMA, init_database


class TestInitDb(unittest.TestCase):
    def test_fresh_install_creates_all_tables(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            result = init_database(db_path)

            self.assertEqual(result["status"], "pass")
            self.assertFalse(result["existed"])
            self.assertEqual(len(result["created_tables"]), len(SCHEMA))
            self.assertEqual(result["existing_tables"], [])

            conn = sqlite3.connect(str(db_path))
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = {row[0] for row in cursor.fetchall()}
            conn.close()

            for table_name in SCHEMA:
                self.assertIn(table_name, tables)

    def test_existing_db_preserves_data(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"

            init_database(db_path)

            conn = sqlite3.connect(str(db_path))
            conn.execute(
                "INSERT INTO strategies (name, description) VALUES ('momentum', 'test')"
            )
            conn.commit()
            conn.close()

            result = init_database(db_path)

            self.assertEqual(result["status"], "pass")
            self.assertTrue(result["existed"])
            self.assertEqual(result["created_tables"], [])

            conn = sqlite3.connect(str(db_path))
            cursor = conn.execute("SELECT name FROM strategies WHERE name='momentum'")
            row = cursor.fetchone()
            conn.close()

            self.assertIsNotNone(row)
            self.assertEqual(row[0], "momentum")

    def test_creates_parent_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "nested" / "deep" / "test.db"
            result = init_database(db_path)

            self.assertEqual(result["status"], "pass")
            self.assertTrue(db_path.exists())

    def test_indexes_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            init_database(db_path)

            conn = sqlite3.connect(str(db_path))
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
            )
            indexes = [row[0] for row in cursor.fetchall()]
            conn.close()

            self.assertIn("idx_trades_ticker", indexes)
            self.assertIn("idx_signals_source", indexes)
            self.assertIn("idx_regime_date", indexes)

    def test_trades_table_constraints(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            init_database(db_path)

            conn = sqlite3.connect(str(db_path))

            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO trades (ticker, direction, strategy, conviction_tier, "
                    "entry_date, entry_price, position_size, risk_per_share, stop_price) "
                    "VALUES ('AAPL', 'invalid', 'momentum', 1, '2026-01-01', 150.0, 100, 5.0, 145.0)"
                )

            conn.close()

    def test_output_json_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            result = init_database(db_path)

            self.assertIn("script", result)
            self.assertIn("version", result)
            self.assertIn("status", result)
            self.assertIn("summary", result)
            self.assertIn("total_tables", result["summary"])
            self.assertIn("created", result["summary"])
            self.assertIn("preserved", result["summary"])


if __name__ == "__main__":
    unittest.main()
