"""Fetches live market data from Alpaca for condition evaluation."""

import logging
from datetime import datetime, timezone, timedelta
import pandas as pd

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame

logger = logging.getLogger(__name__)

# 9:30 AM ET = 13:30 UTC (EST) / 14:30 UTC (EDT)
MARKET_OPEN_HOUR_UTC = 13   # adjust to 14 during EDT (Apr-Oct)
MARKET_OPEN_MINUTE_UTC = 30


def _market_open_today() -> datetime:
    """Return today's 9:30 AM ET as UTC datetime."""
    now_utc = datetime.now(timezone.utc)
    # Apr-Oct: EDT = UTC-4, so 9:30 ET = 13:30 UTC
    # Nov-Mar: EST = UTC-5, so 9:30 ET = 14:30 UTC
    month = now_utc.month
    offset_hours = 4 if 3 <= month <= 11 else 5
    return now_utc.replace(
        hour=9 + offset_hours,
        minute=30,
        second=0,
        microsecond=0,
    )


class MarketDataFetcher:
    def __init__(self, api_key: str, api_secret: str):
        self.client = StockHistoricalDataClient(api_key, api_secret)

    def get_metrics(self, ticker: str) -> dict | None:
        """
        Fetch live metrics for condition evaluation.
        Returns None if data is unavailable.

        Metrics returned:
          price             — latest close price
          gap_pct           — % gap from prior day close
          price_above_vwap  — bool
          price_below_vwap  — bool
          vwap              — intraday VWAP since open
          volume_ratio      — cumulative volume vs expected pace
          rsi_14            — RSI(14) from minute bars
          ema21             — 21-period EMA from minute bars
          price_vs_ema21    — price relative to 21 EMA in %
          or_high           — opening range high (first 15 min)
          or_low            — opening range low (first 15 min)
          or_breakout_long  — bool: price > or_high
          or_breakout_short — bool: price < or_low
          time_utc          — timestamp of data
        """
        try:
            now_utc = datetime.now(timezone.utc)
            open_utc = _market_open_today()

            # Need at least 2 days to get prior close
            start = now_utc - timedelta(days=5)

            req = StockBarsRequest(
                symbol_or_symbols=ticker,
                timeframe=TimeFrame.Minute,
                start=start,
                end=now_utc,
                limit=1000,
            )
            bars_raw = self.client.get_stock_bars(req)
            df = bars_raw.df

            if df.empty:
                logger.warning(f"No bars returned for {ticker}")
                return None

            # Flatten multi-index if present
            if isinstance(df.index, pd.MultiIndex):
                df = df.xs(ticker, level="symbol") if ticker in df.index.get_level_values("symbol") else df

            df = df.sort_index()

            # Split today vs prior
            today_date = now_utc.date()
            today_mask = df.index.date == today_date
            today_bars = df[today_mask]
            prior_bars = df[~today_mask]

            if today_bars.empty:
                logger.warning(f"No intraday bars yet for {ticker}")
                return None

            current_price = float(today_bars["close"].iloc[-1])

            # Prior close
            if not prior_bars.empty:
                prior_close = float(prior_bars["close"].iloc[-1])
            else:
                prior_close = current_price
            gap_pct = (current_price - prior_close) / prior_close * 100

            # VWAP = Σ(typical_price × volume) / Σ(volume)
            today_bars = today_bars.copy()
            today_bars["typical"] = (
                today_bars["high"] + today_bars["low"] + today_bars["close"]
            ) / 3
            total_vol = today_bars["volume"].sum()
            vwap = (
                float((today_bars["typical"] * today_bars["volume"]).sum() / total_vol)
                if total_vol > 0
                else current_price
            )

            # Volume ratio: actual volume vs expected pace
            minutes_elapsed = max(1, (now_utc - open_utc).seconds // 60)
            daily_avg_volume = float(df["volume"].resample("D").sum().mean())
            expected_volume = daily_avg_volume * minutes_elapsed / 390
            volume_ratio = total_vol / expected_volume if expected_volume > 0 else 0.0

            # Opening range (first 15 min)
            or_cutoff = open_utc + timedelta(minutes=15)
            or_bars = today_bars[today_bars.index <= or_cutoff]
            if not or_bars.empty:
                or_high = float(or_bars["high"].max())
                or_low = float(or_bars["low"].min())
            else:
                or_high = current_price
                or_low = current_price

            # EMA21 and RSI14 from today's minute bars
            closes = today_bars["close"]
            ema21 = float(closes.ewm(span=21, adjust=False).mean().iloc[-1])

            rsi14 = None
            if len(closes) >= 15:
                delta = closes.diff()
                gain = delta.clip(lower=0).rolling(14).mean()
                loss = (-delta.clip(upper=0)).rolling(14).mean()
                rs = gain / loss.replace(0, float("nan"))
                rsi_series = 100 - (100 / (1 + rs))
                rsi14 = float(rsi_series.iloc[-1])

            return {
                "ticker": ticker,
                "price": current_price,
                "gap_pct": round(gap_pct, 3),
                "prior_close": prior_close,
                "vwap": round(vwap, 4),
                "price_above_vwap": current_price > vwap,
                "price_below_vwap": current_price < vwap,
                "volume_ratio": round(volume_ratio, 3),
                "or_high": round(or_high, 4),
                "or_low": round(or_low, 4),
                "or_breakout_long": current_price > or_high,
                "or_breakout_short": current_price < or_low,
                "ema21": round(ema21, 4),
                "price_vs_ema21": round((current_price - ema21) / ema21 * 100, 3),
                "rsi_14": round(rsi14, 2) if rsi14 is not None else None,
                "time_utc": now_utc.isoformat(),
            }

        except Exception as e:
            logger.error(f"MarketDataFetcher.get_metrics({ticker}) failed: {e}")
            return None
