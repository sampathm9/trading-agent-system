import json
from datetime import datetime
from pathlib import Path


class HybridHistoricalLiveBacktestWorker:

    def __init__(
        self,
        data_provider=None,
        historical_manager=None,
        realistic_backtest_worker=None,
        trend_worker=None,
        decision_worker=None
    ):

        from workers.data_provider.yahoo_provider import (
            YahooMarketDataProvider
        )

        from workers.historical.historical_data_manager import (
            HistoricalDataManager
        )

        from workers.backtest.phase3.realistic_backtest_worker import (
            RealisticBacktestWorker
        )

        from workers.intelligence.trend_worker import (
            TrendWorker
        )

        from workers.decision.decision_worker import (
            DecisionWorker
        )

        self.data_provider = (
            data_provider
            or YahooMarketDataProvider()
        )

        self.historical_manager = (
            historical_manager
            or HistoricalDataManager()
        )

        self.realistic_backtest_worker = (
            realistic_backtest_worker
            or RealisticBacktestWorker()
        )

        self.trend_worker = (
            trend_worker
            or TrendWorker()
        )

        self.decision_worker = (
            decision_worker
            or DecisionWorker()
        )

    # ---------------------------------------------------------
    # TIMESTAMP
    # ---------------------------------------------------------

    def _timestamp(self, candle):

        return (
            candle.get("timestamp")
            or candle.get("datetime")
            or candle.get("date")
        )

    # ---------------------------------------------------------
    # DATE
    # ---------------------------------------------------------

    def _date_from_candle(self, candle):

        timestamp = self._timestamp(candle)

        if timestamp is None:
            return None

        try:

            return (
                datetime.fromisoformat(
                    str(timestamp)
                ).date()
            )

        except ValueError:

            return str(timestamp)[:10]

    # ---------------------------------------------------------
    # LOAD HISTORICAL DATA
    # ---------------------------------------------------------

    def load_historical_data(
        self,
        symbol="NIFTY",
        filename="nifty_1y_real.json"
    ):

        path = (
            self.historical_manager
            .get_file_path(
                symbol=symbol,
                filename=filename
            )
        )

        if not path.exists():

            raise FileNotFoundError(
                f"Historical data not found: {path}"
            )

        with path.open(
            "r",
            encoding="utf-8"
        ) as file:

            payload = json.load(file)

        if isinstance(payload, list):

            candles = payload

        else:

            candles = payload.get(
                "candles",
                []
            )

        if not candles:

            raise ValueError(
                "Historical data contains no candles"
            )

        return candles

    # ---------------------------------------------------------
    # REMOVE TODAY'S DAILY CANDLE
    # ---------------------------------------------------------

    def remove_current_day_from_historical(
        self,
        candles
    ):

        today = datetime.now().date()

        filtered = []

        removed = []

        for candle in candles:

            candle_date = (
                self._date_from_candle(
                    candle
                )
            )

            if candle_date == today:

                removed.append(
                    candle
                )

                continue

            filtered.append(
                candle
            )

        return filtered, removed

    # ---------------------------------------------------------
    # FETCH LIVE DATA
    # ---------------------------------------------------------

    def load_live_data(
        self,
        symbol="NIFTY",
        interval="5m"
    ):

        candles = (
            self.data_provider
            .get_intraday_candles(
                symbol=symbol,
                interval=interval
            )
        )

        if not candles:

            raise ValueError(
                "No live intraday candles returned"
            )

        return candles

    # ---------------------------------------------------------
    # REMOVE DUPLICATE TIMESTAMPS
    # ---------------------------------------------------------

    def deduplicate_candles(
        self,
        candles
    ):

        seen = set()

        result = []

        for candle in candles:

            timestamp = self._timestamp(
                candle
            )

            if timestamp in seen:

                continue

            seen.add(timestamp)

            result.append(candle)

        return result

    # ---------------------------------------------------------
    # CURRENT LIVE SIGNAL
    # ---------------------------------------------------------

    def calculate_live_signal(
        self,
        candles,
        short_period=5,
        long_period=10
    ):

        if len(candles) <= long_period:

            raise ValueError(
                "Not enough live candles for signal calculation"
            )

        trend_result = (
            self.trend_worker.analyze(
                candles,
                short_period=short_period,
                long_period=long_period
            )
        )

        trend = trend_result.get(
            "trend"
        )

        decision = (
            self.decision_worker.decide(
                trend
            )
        )

        latest = candles[-1]

        return {

            "timestamp": self._timestamp(
                latest
            ),

            "price": float(
                latest["close"]
            ),

            "trend": trend,

            "short_average": trend_result.get(
                "short_average"
            ),

            "long_average": trend_result.get(
                "long_average"
            ),

            "action": decision.get(
                "action"
            ),

            "confidence": decision.get(
                "confidence"
            )
        }

    # ---------------------------------------------------------
    # HISTORICAL BACKTEST
    # ---------------------------------------------------------

    def run_historical_backtest(
        self,
        candles,
        symbol,
        quantity=1,
        short_period=5,
        long_period=10,
        stop_loss_pct=0.02,
        take_profit_pct=0.04,
        max_daily_loss=None
    ):

        if not candles:

            raise ValueError(
                "No historical candles available"
            )

        return (
            self.realistic_backtest_worker.run(
                candles=candles,
                symbol=symbol,
                quantity=quantity,
                short_period=short_period,
                long_period=long_period,
                stop_loss_pct=stop_loss_pct,
                take_profit_pct=take_profit_pct,
                max_daily_loss=max_daily_loss
            )
        )

    # ---------------------------------------------------------
    # MAIN HYBRID RUN
    # ---------------------------------------------------------

    def run(
        self,
        symbol="NIFTY",
        historical_filename="nifty_1y_real.json",
        interval="5m",
        quantity=1,
        short_period=5,
        long_period=10,
        stop_loss_pct=0.02,
        take_profit_pct=0.04,
        max_daily_loss=None
    ):

        # -----------------------------------------------------
        # 1. LOAD HISTORICAL DATA
        # -----------------------------------------------------

        historical_candles = (
            self.load_historical_data(
                symbol=symbol,
                filename=historical_filename
            )
        )

        original_historical_count = (
            len(historical_candles)
        )

        # -----------------------------------------------------
        # 2. REMOVE TODAY'S DAILY CANDLE
        # -----------------------------------------------------

        historical_candles, removed_today = (
            self.remove_current_day_from_historical(
                historical_candles
            )
        )

        # -----------------------------------------------------
        # 3. FETCH LIVE INTRADAY DATA
        # -----------------------------------------------------

        live_candles = (
            self.load_live_data(
                symbol=symbol,
                interval=interval
            )
        )

        # -----------------------------------------------------
        # 4. REMOVE DUPLICATES
        # -----------------------------------------------------

        live_candles = (
            self.deduplicate_candles(
                live_candles
            )
        )

        # -----------------------------------------------------
        # 5. HISTORICAL BACKTEST
        # -----------------------------------------------------

        historical_result = (
            self.run_historical_backtest(
                candles=historical_candles,
                symbol=symbol,
                quantity=quantity,
                short_period=short_period,
                long_period=long_period,
                stop_loss_pct=stop_loss_pct,
                take_profit_pct=take_profit_pct,
                max_daily_loss=max_daily_loss
            )
        )

        # -----------------------------------------------------
        # 6. LIVE SIGNAL
        # -----------------------------------------------------

        live_signal = (
            self.calculate_live_signal(
                candles=live_candles,
                short_period=short_period,
                long_period=long_period
            )
        )

        # -----------------------------------------------------
        # 7. LATEST LIVE CANDLE
        # -----------------------------------------------------

        latest_live = live_candles[-1]

        # -----------------------------------------------------
        # 8. RETURN HYBRID RESULT
        # -----------------------------------------------------

        return {

            "status": "COMPLETED",

            "symbol": symbol,

            "mode": "HISTORICAL_PLUS_LIVE",

            "historical": {

                "original_candles": (
                    original_historical_count
                ),

                "removed_current_day_candles": (
                    len(removed_today)
                ),

                "backtest_candles": (
                    len(historical_candles)
                ),

                "first_timestamp": (
                    self._timestamp(
                        historical_candles[0]
                    )
                    if historical_candles
                    else None
                ),

                "last_timestamp": (
                    self._timestamp(
                        historical_candles[-1]
                    )
                    if historical_candles
                    else None
                ),

                "backtest": historical_result

            },

            "live": {

                "interval": interval,

                "candles": len(
                    live_candles
                ),

                "first_timestamp": (
                    self._timestamp(
                        live_candles[0]
                    )
                ),

                "last_timestamp": (
                    self._timestamp(
                        live_candles[-1]
                    )
                ),

                "latest_candle": latest_live,

                "signal": live_signal

            },

            "current_market": {

                "timestamp": live_signal[
                    "timestamp"
                ],

                "price": live_signal[
                    "price"
                ],

                "trend": live_signal[
                    "trend"
                ],

                "action": live_signal[
                    "action"
                ],

                "confidence": live_signal[
                    "confidence"
                ]

            }

        }