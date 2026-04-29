"""Enforces portfolio heat and per-strategy position limits before order submission."""

import logging
from alpaca.trading.client import TradingClient
from .config_loader import ConfigLoader, STRATEGY_MAX_POSITIONS

logger = logging.getLogger(__name__)


class RiskMonitor:
    def __init__(self, trading_client: TradingClient, config: ConfigLoader):
        self.client = trading_client
        self.config = config

    def check(self, trigger: dict) -> tuple[bool, str]:
        """
        Run all risk gates. Returns (approved: bool, reason: str).

        Gates:
          1. Portfolio heat — would new trade exceed $3K total risk?
          2. Strategy count — would this exceed max concurrent positions for the strategy?
          3. Account buying power — can we afford the trade?
        """
        trade = trigger.get("trade", {})
        new_risk = float(trade.get("max_risk", 300))
        strategy = trigger.get("strategy", "")

        try:
            positions = self.client.get_all_positions()
            account = self.client.get_account()
        except Exception as e:
            logger.error(f"RiskMonitor: failed to fetch account data: {e}")
            return False, f"Account data unavailable: {e}"

        # Gate 1: Portfolio heat
        current_heat = sum(self._position_risk(p) for p in positions)
        max_heat = self.config.get_max_heat()
        if current_heat + new_risk > max_heat:
            return False, (
                f"Portfolio heat block: current ${current_heat:.0f} + "
                f"new ${new_risk:.0f} > max ${max_heat:.0f}"
            )

        # Gate 2: Per-strategy position count
        strategy_count = sum(
            1 for p in positions
            if getattr(p, "asset_class", "") == strategy
            or self._get_strategy_tag(p) == strategy
        )
        max_positions = STRATEGY_MAX_POSITIONS.get(strategy, 2)
        if strategy_count >= max_positions:
            return False, (
                f"Strategy limit: {strategy} already has {strategy_count}/{max_positions} positions"
            )

        # Gate 3: Buying power
        buying_power = float(getattr(account, "buying_power", 0))
        price = trigger.get("_last_price", 0)
        shares = trade.get("shares", 0)
        required_capital = price * shares if price and shares else new_risk * 10
        if buying_power < required_capital:
            return False, (
                f"Insufficient buying power: ${buying_power:.0f} < ${required_capital:.0f}"
            )

        return True, "ok"

    def _position_risk(self, position) -> float:
        """Estimate dollar risk on an open position (unrealized loss potential)."""
        try:
            market_value = abs(float(getattr(position, "market_value", 0)))
            # Conservative: assume 3% stop = 3% of position value at risk
            return market_value * 0.03
        except Exception:
            return 0.0

    def _get_strategy_tag(self, position) -> str:
        """Read strategy tag from position metadata if available."""
        # Alpaca doesn't natively tag positions by strategy.
        # The order router writes a client_order_id prefix like "TM-ERP-AAPL-..."
        # We can't read that from the position object directly.
        # Future: maintain a local positions.json that maps symbol → strategy.
        return ""
