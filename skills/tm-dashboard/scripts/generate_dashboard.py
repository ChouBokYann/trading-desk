#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Generate a single-file HTML trading dashboard from structured JSON data.

Reads a JSON object from stdin with optional keys: portfolio, risk, regime,
greeks, correlation, performance, strategy_allocation, watchlist, queue.
Missing keys simply hide that panel. Outputs styled HTML to stdout or -o file.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from html import escape

FLAG_COLORS = {"green": "#22c55e", "yellow": "#eab308", "red": "#ef4444", "black": "#1f2937"}
FLAG_BG = {"green": "#f0fdf4", "yellow": "#fefce8", "red": "#fef2f2", "black": "#f3f4f6"}


def pnl_color(val: float) -> str:
    if val > 0:
        return "#22c55e"
    if val < 0:
        return "#ef4444"
    return "#6b7280"


def heat_color(pct: float, limit: float) -> str:
    ratio = pct / limit if limit > 0 else 1
    if ratio >= 0.9:
        return "#ef4444"
    if ratio >= 0.7:
        return "#eab308"
    return "#22c55e"


def render_portfolio(data: dict) -> str:
    p = data.get("portfolio", {})
    if not p:
        return ""
    positions = p.get("positions", [])
    acct = p.get("account_value", 0)
    cash = p.get("cash", 0)
    cash_pct = (cash / acct * 100) if acct > 0 else 0
    total_pnl = sum(pos.get("unrealized_pnl", 0) for pos in positions)

    rows = ""
    for pos in positions:
        pnl = pos.get("unrealized_pnl", 0)
        pnl_pct = pos.get("unrealized_pnl_pct", 0)
        rows += f"""<tr>
            <td><strong>{escape(pos.get('ticker',''))}</strong></td>
            <td>{pos.get('shares',0)}</td>
            <td>${pos.get('avg_entry',0):,.2f}</td>
            <td>${pos.get('current_price',0):,.2f}</td>
            <td>${pos.get('market_value',0):,.2f}</td>
            <td style="color:{pnl_color(pnl)}">${pnl:+,.2f} ({pnl_pct:+.1f}%)</td>
        </tr>"""

    return f"""<section class="panel">
        <h2>Portfolio Overview</h2>
        <div class="metrics-row">
            <div class="metric"><span class="metric-label">Account Value</span><span class="metric-value">${acct:,.2f}</span></div>
            <div class="metric"><span class="metric-label">Cash</span><span class="metric-value">${cash:,.2f} ({cash_pct:.1f}%)</span></div>
            <div class="metric"><span class="metric-label">Positions</span><span class="metric-value">{len(positions)}</span></div>
            <div class="metric"><span class="metric-label">Unrealized P&amp;L</span><span class="metric-value" style="color:{pnl_color(total_pnl)}">${total_pnl:+,.2f}</span></div>
        </div>
        <table><thead><tr><th>Ticker</th><th>Shares</th><th>Entry</th><th>Current</th><th>Value</th><th>P&amp;L</th></tr></thead>
        <tbody>{rows}</tbody></table>
    </section>"""


def render_regime(data: dict) -> str:
    r = data.get("regime", {})
    if not r:
        return ""
    flag = r.get("flag", "green")
    color = FLAG_COLORS.get(flag, "#6b7280")
    bg = FLAG_BG.get(flag, "#f9fafb")
    impl = r.get("implications", {})

    return f"""<section class="panel" style="border-left:4px solid {color};background:{bg}">
        <h2>Regime: <span style="color:{color}">{flag.upper()}</span></h2>
        <div class="metrics-row">
            <div class="metric"><span class="metric-label">Macro</span><span class="metric-value">{escape(str(r.get('macro','--')))}</span></div>
            <div class="metric"><span class="metric-label">VIX</span><span class="metric-value">{r.get('vix','--')}</span></div>
            <div class="metric"><span class="metric-label">Dist. Days</span><span class="metric-value">{r.get('distribution_days','--')}</span></div>
            <div class="metric"><span class="metric-label">Safety Car</span><span class="metric-value">{'ACTIVE' if r.get('safety_car') else 'Off'}</span></div>
        </div>
        <div class="metrics-row">
            <div class="metric"><span class="metric-label">Position Size</span><span class="metric-value">{escape(str(impl.get('max_position_size','--')))}</span></div>
            <div class="metric"><span class="metric-label">New Entries</span><span class="metric-value">{escape(str(impl.get('new_entries','--')))}</span></div>
            <div class="metric"><span class="metric-label">Cash Target</span><span class="metric-value">{escape(str(impl.get('recommended_cash','--')))}</span></div>
        </div>
    </section>"""


def render_risk(data: dict) -> str:
    risk = data.get("risk", {})
    if not risk:
        return ""
    heat = risk.get("portfolio_heat_pct", 0)
    limit = risk.get("heat_limit_pct", 8)
    drawdown = risk.get("drawdown_pct", 0)
    positions = risk.get("positions", [])

    rows = ""
    for pos in positions:
        dist = pos.get("distance_to_stop_pct", 0)
        dist_color = "#ef4444" if dist < 3 else "#eab308" if dist < 5 else "#22c55e"
        days = pos.get("days_in_trade", 0)
        decay_flag = " *" if days > 10 else ""
        rows += f"""<tr>
            <td><strong>{escape(pos.get('ticker',''))}</strong></td>
            <td style="color:{dist_color}">{dist:.1f}%</td>
            <td>{pos.get('current_r','--')}</td>
            <td>{pos.get('heat_contribution_pct',0):.2f}%</td>
            <td>{days}d{decay_flag}</td>
        </tr>"""

    return f"""<section class="panel">
        <h2>Risk Telemetry</h2>
        <div class="metrics-row">
            <div class="metric"><span class="metric-label">Portfolio Heat</span><span class="metric-value" style="color:{heat_color(heat, limit)}">{heat:.1f}% / {limit:.0f}%</span></div>
            <div class="metric"><span class="metric-label">Drawdown</span><span class="metric-value" style="color:{pnl_color(-drawdown)}">{drawdown:.1f}%</span></div>
        </div>
        <table><thead><tr><th>Ticker</th><th>To Stop</th><th>R-Mult</th><th>Heat</th><th>Days</th></tr></thead>
        <tbody>{rows}</tbody></table>
    </section>"""


def render_greeks(data: dict) -> str:
    g = data.get("greeks", {})
    if not g:
        return ""
    positions = g.get("positions", [])
    summary = g.get("portfolio_summary", {})

    rows = ""
    for pos in positions:
        rows += f"""<tr>
            <td><strong>{escape(pos.get('ticker',''))}</strong></td>
            <td>{pos.get('delta','--')}</td>
            <td>{pos.get('gamma','--')}</td>
            <td>{pos.get('theta','--')}</td>
            <td>{pos.get('vega','--')}</td>
            <td>{pos.get('dte','--')}</td>
        </tr>"""

    return f"""<section class="panel">
        <h2>Greeks</h2>
        <div class="metrics-row">
            <div class="metric"><span class="metric-label">Net Delta</span><span class="metric-value">{summary.get('net_delta','--')}</span></div>
            <div class="metric"><span class="metric-label">Theta/Day</span><span class="metric-value">${summary.get('theta_per_day','--')}</span></div>
        </div>
        <table><thead><tr><th>Position</th><th>&Delta;</th><th>&Gamma;</th><th>&Theta;</th><th>Vega</th><th>DTE</th></tr></thead>
        <tbody>{rows}</tbody></table>
    </section>"""


def render_correlation(data: dict) -> str:
    c = data.get("correlation", {})
    if not c:
        return ""
    pairs = c.get("pairs", [])
    warnings = [p for p in pairs if p.get("correlation", 0) > 0.8]

    rows = ""
    for p in pairs:
        corr = p.get("correlation", 0)
        color = "#ef4444" if corr > 0.8 else "#eab308" if corr > 0.6 else "#22c55e"
        label = " TCAS" if corr > 0.8 else ""
        rows += f"""<tr>
            <td>{escape(p.get('ticker_a',''))}</td>
            <td>{escape(p.get('ticker_b',''))}</td>
            <td style="color:{color}">{corr:.2f}{label}</td>
        </tr>"""

    warning_html = ""
    if warnings:
        warning_html = f'<div class="alert">TCAS WARNING: {len(warnings)} pair(s) exceed 0.8 correlation</div>'

    return f"""<section class="panel">
        <h2>Correlation</h2>
        {warning_html}
        <table><thead><tr><th>Ticker A</th><th>Ticker B</th><th>Correlation</th></tr></thead>
        <tbody>{rows}</tbody></table>
    </section>"""


def render_allocation(data: dict) -> str:
    a = data.get("strategy_allocation", {})
    if not a:
        return ""
    strategies = a.get("strategies", [])

    rows = ""
    for s in strategies:
        actual = s.get("actual_pct", 0)
        target = s.get("target_pct", 0)
        drift = actual - target
        drift_color = "#ef4444" if abs(drift) > 5 else "#eab308" if abs(drift) > 2 else "#6b7280"
        rows += f"""<tr>
            <td><strong>{escape(s.get('name',''))}</strong></td>
            <td>{actual:.1f}%</td>
            <td>{target:.1f}%</td>
            <td style="color:{drift_color}">{drift:+.1f}%</td>
        </tr>"""

    return f"""<section class="panel">
        <h2>Strategy Allocation</h2>
        <table><thead><tr><th>Strategy</th><th>Actual</th><th>Target</th><th>Drift</th></tr></thead>
        <tbody>{rows}</tbody></table>
    </section>"""


def render_watchlist(data: dict) -> str:
    w = data.get("watchlist", {})
    if not w:
        return ""
    items = w.get("items", [])
    if not items:
        return ""

    rows = ""
    for item in items:
        gates = item.get("gates_passed", 0)
        total = item.get("gates_total", 7)
        dist = item.get("distance_to_trigger_pct", 0)
        rows += f"""<tr>
            <td><strong>{escape(item.get('ticker',''))}</strong></td>
            <td>${item.get('current_price',0):,.2f}</td>
            <td>${item.get('trigger_price',0):,.2f}</td>
            <td>{dist:.1f}%</td>
            <td>{gates}/{total} gates</td>
        </tr>"""

    return f"""<section class="panel">
        <h2>Active Watchlist</h2>
        <table><thead><tr><th>Ticker</th><th>Current</th><th>Trigger</th><th>Distance</th><th>Clearance</th></tr></thead>
        <tbody>{rows}</tbody></table>
    </section>"""


def render_queue(data: dict) -> str:
    q = data.get("queue", {})
    if not q:
        return ""
    orders = q.get("orders", [])
    if not orders:
        return ""

    rows = ""
    for o in orders:
        rows += f"""<tr>
            <td><strong>{escape(o.get('ticker',''))}</strong></td>
            <td>{escape(o.get('direction',''))}</td>
            <td>{o.get('shares',0)}</td>
            <td>${o.get('entry_price',0):,.2f}</td>
            <td>{escape(o.get('time_remaining',''))}</td>
        </tr>"""

    return f"""<section class="panel">
        <h2>Confirmation Queue</h2>
        <table><thead><tr><th>Ticker</th><th>Direction</th><th>Shares</th><th>Entry</th><th>Veto Window</th></tr></thead>
        <tbody>{rows}</tbody></table>
    </section>"""


STYLES = """
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:#0f172a; color:#e2e8f0; padding:24px; }
h1 { font-size:1.5rem; margin-bottom:20px; color:#f8fafc; }
h2 { font-size:1.1rem; margin-bottom:12px; color:#f1f5f9; }
.timestamp { color:#64748b; font-size:0.85rem; margin-bottom:20px; }
.grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(480px,1fr)); gap:16px; }
.panel { background:#1e293b; border-radius:8px; padding:16px; }
.metrics-row { display:flex; gap:16px; margin-bottom:12px; flex-wrap:wrap; }
.metric { flex:1; min-width:100px; }
.metric-label { display:block; font-size:0.75rem; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; }
.metric-value { display:block; font-size:1.25rem; font-weight:600; margin-top:2px; }
table { width:100%; border-collapse:collapse; font-size:0.875rem; }
th { text-align:left; padding:6px 8px; color:#94a3b8; border-bottom:1px solid #334155; font-weight:500; }
td { padding:6px 8px; border-bottom:1px solid #1e293b; }
tr:hover { background:#334155; }
.alert { background:#7f1d1d; color:#fecaca; padding:8px 12px; border-radius:4px; margin-bottom:12px; font-weight:500; }
"""


def generate_html(data: dict) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    sections = [
        render_regime(data),
        render_portfolio(data),
        render_risk(data),
        render_greeks(data),
        render_correlation(data),
        render_allocation(data),
        render_watchlist(data),
        render_queue(data),
    ]

    body = "\n".join(s for s in sections if s)

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>The Money -- Dashboard</title>
<style>{STYLES}</style>
</head>
<body>
<h1>The Money -- Portfolio Telemetry</h1>
<div class="timestamp">Generated {ts}</div>
<div class="grid">{body}</div>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Generate HTML trading dashboard from JSON data")
    parser.add_argument("-o", dest="output_file", default=None, help="Output HTML file (default: stdout)")
    parser.add_argument("--verbose", action="store_true", help="Print diagnostics to stderr")
    args = parser.parse_args()

    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f'{{"error": "Invalid JSON: {e}"}}', file=sys.stderr)
        sys.exit(2)

    if args.verbose:
        keys = list(data.keys())
        print(f"Sections present: {keys}", file=sys.stderr)

    html = generate_html(data)

    if args.output_file:
        with open(args.output_file, "w", encoding="utf-8") as f:
            f.write(html)
        if args.verbose:
            print(f"Dashboard written to {args.output_file}", file=sys.stderr)
    else:
        print(html)


if __name__ == "__main__":
    main()
