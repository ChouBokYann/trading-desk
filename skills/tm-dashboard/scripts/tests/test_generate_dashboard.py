#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from generate_dashboard import generate_html, render_portfolio, render_regime, render_risk, render_correlation


SAMPLE_DATA = {
    "portfolio": {
        "account_value": 100000.00,
        "cash": 35000.00,
        "positions": [
            {"ticker": "AAPL", "shares": 45, "avg_entry": 195.50, "current_price": 200.00,
             "market_value": 9000.00, "unrealized_pnl": 202.50, "unrealized_pnl_pct": 2.30},
            {"ticker": "MSFT", "shares": 20, "avg_entry": 400.00, "current_price": 390.00,
             "market_value": 7800.00, "unrealized_pnl": -200.00, "unrealized_pnl_pct": -2.50},
        ],
    },
    "regime": {"macro": "bull", "flag": "green", "vix": 16.5, "distribution_days": 2,
               "safety_car": False, "implications": {"max_position_size": "full", "new_entries": "allowed", "recommended_cash": "20%"}},
    "risk": {"portfolio_heat_pct": 5.2, "heat_limit_pct": 8.0, "drawdown_pct": 1.3,
             "positions": [
                 {"ticker": "AAPL", "distance_to_stop_pct": 6.2, "current_r": "0.5R", "heat_contribution_pct": 1.80, "days_in_trade": 5},
                 {"ticker": "MSFT", "distance_to_stop_pct": 2.1, "current_r": "-0.3R", "heat_contribution_pct": 3.40, "days_in_trade": 12},
             ]},
    "correlation": {"pairs": [
        {"ticker_a": "AAPL", "ticker_b": "MSFT", "correlation": 0.85},
    ]},
}


def test_full_dashboard_renders():
    """Full dashboard produces valid HTML."""
    html = generate_html(SAMPLE_DATA)
    assert "<!DOCTYPE html>" in html
    assert "The Money" in html
    assert "AAPL" in html
    assert "MSFT" in html


def test_empty_data():
    """Empty data produces valid HTML with no panels."""
    html = generate_html({})
    assert "<!DOCTYPE html>" in html
    assert "<div class=\"grid\">" in html


def test_portfolio_section():
    """Portfolio section renders positions and P&L."""
    html = render_portfolio(SAMPLE_DATA)
    assert "AAPL" in html
    assert "+$202.50" in html or "202.50" in html
    assert "MSFT" in html


def test_regime_green():
    """Green regime renders with green styling."""
    html = render_regime(SAMPLE_DATA)
    assert "GREEN" in html
    assert "#22c55e" in html


def test_regime_red():
    """Red regime renders with red styling."""
    data = {"regime": {"macro": "bear", "flag": "red", "vix": 32, "distribution_days": 6,
                       "safety_car": False, "implications": {"max_position_size": "none", "new_entries": "halted", "recommended_cash": "40%"}}}
    html = render_regime(data)
    assert "RED" in html
    assert "#ef4444" in html


def test_risk_colors():
    """Risk section colors positions near stop in red."""
    html = render_risk(SAMPLE_DATA)
    assert "MSFT" in html
    # MSFT has 2.1% to stop — should be red
    assert "#ef4444" in html


def test_tcas_warning():
    """Correlation >0.8 triggers TCAS warning."""
    html = render_correlation(SAMPLE_DATA)
    assert "TCAS" in html
    assert "0.85" in html


def test_missing_sections_graceful():
    """Missing optional sections don't crash."""
    partial = {"portfolio": SAMPLE_DATA["portfolio"]}
    html = generate_html(partial)
    assert "AAPL" in html
    assert "Regime" not in html


def test_portfolio_missing_returns_empty():
    """No portfolio key returns empty string."""
    assert render_portfolio({}) == ""


if __name__ == "__main__":
    tests = [name for name in sorted(dir()) if name.startswith("test_")]
    passed = failed = 0
    for name in tests:
        try:
            globals()[name]()
            passed += 1
            print(f"  PASS  {name}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {name}: {e}")
        except Exception as e:
            failed += 1
            print(f"  FAIL  {name}: {type(e).__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
