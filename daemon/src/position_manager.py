"""Manages open positions: trailing stops, pyramid entries, partial exits."""

import logging
from alpaca.trading.client import TradingClient

logger = logging.getLogger(__name__)


class PositionManager:
    def __init__(self, trading_client: TradingClient):
        self.client = trading_client

    def check_open_positions(self) -> list[dict]:
        """
        Scan open positions and flag any that need action.
        Returns action items consumed by the watcher loop.
        """
        actions = []
        try:
            positions = self.client.get_all_positions()
            for p in positions:
                action = self._evaluate(p)
                if action:
                    actions.append(action)
        except Exception as e:
            logger.error(f"PositionManager: failed to fetch positions: {e}")
        return actions

    def _evaluate(self, position) -> dict | None:
        try:
            unrealized_pnl_pct = float(getattr(position, "unrealized_plpc", 0)) * 100
            symbol = getattr(position, "symbol", "")

            # Flag for trailing stop upgrade when >6% in profit
            if unrealized_pnl_pct > 6.0:
                return {
                    "action": "upgrade_trailing_stop",
                    "symbol": symbol,
                    "unrealized_pnl_pct": unrealized_pnl_pct,
                    "note": "Move stop to breakeven or trail at 2%",
                }

            # Flag for review when approaching stop loss
            if unrealized_pnl_pct < -5.0:
                return {
                    "action": "review_stop",
                    "symbol": symbol,
                    "unrealized_pnl_pct": unrealized_pnl_pct,
                    "note": "Approaching stop. Check thesis integrity.",
                }
        except Exception:
            pass
        return None
