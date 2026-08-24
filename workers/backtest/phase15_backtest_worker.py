import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from config.phase15_config import (
    COMMISSION_PER_TRADE,
    DEFAULT_QUANTITY,
    INITIAL_CAPITAL,
    MAX_TRADES,
    REPORT_DIRECTORY,
    SLIPPAGE_PER_TRADE,
)

from workers.backtest.historical_replay import HistoricalReplay
from workers.backtest.performance_analyzer import (
    PerformanceAnalyzer,
)


class Phase15BacktestWorker:

    def __init__(
        self,
        intelligence_worker,
        initial_capital: float = INITIAL_CAPITAL,
    ):

        self.intelligence = intelligence_worker

        self.initial_capital = float(
            initial_capital
        )

        self.performance = (
            PerformanceAnalyzer()
        )

        self.trades: List[Dict] = []

        self.position = 0

        self.entry_price: Optional[float] = None

        self.entry_timestamp = None

    # ---------------------------------------------------------
    # RESET
    # ---------------------------------------------------------

    def reset(self):

        self.trades = []

        self.position = 0

        self.entry_price = None

        self.entry_timestamp = None

    # ---------------------------------------------------------
    # ENTRY
    # ---------------------------------------------------------

    def _open_position(
        self,
        timestamp,
        price: float,
        quantity: int,
    ):

        if self.position != 0:
            return False

        self.position = quantity

        self.entry_price = (
            float(price)
            + SLIPPAGE_PER_TRADE
        )

        self.entry_timestamp = timestamp

        return True

    # ---------------------------------------------------------
    # EXIT
    # ---------------------------------------------------------

    def _close_position(
        self,
        timestamp,
        price: float,
    ):

        if self.position == 0:
            return False

        exit_price = (
            float(price)
            - SLIPPAGE_PER_TRADE
        )

        pnl = (
            exit_price
            - self.entry_price
        ) * self.position

        pnl -= COMMISSION_PER_TRADE

        self.trades.append(
            {
                "timestamp": timestamp,
                "entry_timestamp": self.entry_timestamp,
                "entry_price": self.entry_price,
                "exit_price": exit_price,
                "quantity": self.position,
                "side": "LONG",
                "pnl": pnl,
            }
        )

        self.position = 0
        self.entry_price = None
        self.entry_timestamp = None

        return True

    # ---------------------------------------------------------
    # CANDLE
    # ---------------------------------------------------------

    def process_candle(
        self,
        candles: List[Dict],
        candle: Dict,
        symbol: str,
        quantity: int,
        news: Optional[Iterable[Dict | str]],
    ):

        if len(self.trades) >= MAX_TRADES:
            return

        if len(candles) < 3:
            return

        intelligence = (
            self.intelligence.analyze_market(
                candles,
                news,
            )
        )

        strategy = (
            self.intelligence.create_strategy_signal(
                intelligence
            )
        )

        risk = (
            self.intelligence.validate_risk(
                strategy,
                quantity,
            )
        )

        if not risk["approved"]:
            return

        action = strategy["action"]

        timestamp = candle.get(
            "timestamp"
        )

        price = float(
            candle["close"]
        )

        if action == "BUY":

            self._open_position(
                timestamp=timestamp,
                price=price,
                quantity=quantity,
            )

        elif action == "SELL":

            self._close_position(
                timestamp=timestamp,
                price=price,
            )
    # ---------------------------------------------------------
    # RUN
    # ---------------------------------------------------------

    def run(
        self,
        candles: List[Dict],
        symbol: str = "NIFTY",
        quantity: int = DEFAULT_QUANTITY,
        news: Optional[Iterable[Dict | str]] = None,
        final_exit_price: Optional[float] = None,
    ):

        self.reset()

        replay = HistoricalReplay(
            candles
        )

        replay.replay(
            lambda history, candle:
            self.process_candle(
                history,
                candle,
                symbol,
                quantity,
                news,
            )
        )

        # -----------------------------------------------------
        # FORCE EOD EXIT
        # -----------------------------------------------------

        if self.position != 0:

            last_price = (
                final_exit_price
                if final_exit_price is not None
                else float(
                    candles[-1]["close"]
                )
            )

            self._close_position(
                timestamp=candles[-1].get(
                    "timestamp"
                ),
                price=last_price,
            )

        metrics = (
            self.performance.analyze(
                self.initial_capital,
                self.trades,
            )
        )

        return {
            "symbol": symbol,
            "candles": len(candles),
            "trades": self.trades,
            "metrics": metrics,
        }

    # ---------------------------------------------------------
    # REPORT
    # ---------------------------------------------------------

    def save_report(
        self,
        result: Dict,
        filename: str = (
            "phase15_backtest_report.json"
        ),
    ):

        directory = Path(
            REPORT_DIRECTORY
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        path = directory / filename

        path.write_text(
            json.dumps(
                result,
                indent=2,
                default=str,
            )
        )

        return str(path)
