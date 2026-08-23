from datetime import date, time

from agents.daily_trading_agent import DailyTradingAgent
from workers.calendar.market_calendar import NSEMarketCalendar
from workers.runtime.paper_runtime import PaperTradingRuntime
from workers.market_data.market_data_cache import MarketDataCache
from workers.market_data.live_market_data_worker import LiveMarketDataWorker
from workers.strategy.strategy_engine import StrategyEngine
from workers.pipeline.trading_pipeline import TradingPipeline
from workers.pipeline.phase7_report import Phase7Report


def build_candles():
    candles = []

    for i in range(30):
        close = 100 + i

        candles.append(
            {
                "timestamp": (
                    f"2026-08-24T09:{15+i:02d}:00"
                ),
                "open": close - 1,
                "high": close + 1,
                "low": close - 2,
                "close": close,
                "volume": 1000,
            }
        )

    return candles


class TestMarketDataWorker:

    def __init__(self, candles):
        self.candles = candles

    def get_candles(self, symbol):
        return list(self.candles)


def main():

    print("=" * 60)
    print("PHASE 7 FULL PIPELINE INTEGRATION TEST")
    print("=" * 60)

    print()
    print("1. BUILD COMPONENTS")
    print("-" * 60)

    calendar = NSEMarketCalendar()

    agent = DailyTradingAgent()

    candles = build_candles()

    agent.load_market_data(
        "NIFTY",
        candles
    )

    runtime = PaperTradingRuntime(
        agent=agent,
        market_calendar=calendar,
        symbol="NIFTY",
        quantity=1,
        stop_loss_pct=0.02,
        take_profit_pct=0.04,
        max_daily_loss=1000,
    )

    market_data = TestMarketDataWorker(
        candles
    )

    strategy = StrategyEngine()

    pipeline = TradingPipeline(
        runtime=runtime,
        market_data_worker=market_data,
        strategy_engine=strategy,
        market_calendar=calendar,
        symbol="NIFTY",
    )

    print("Components created")

    print()
    print("2. WEEKEND PROTECTION")
    print("-" * 60)

    weekend = pipeline.start(
        date(2026, 8, 23)
    )

    print(weekend)

    assert weekend["status"] == "MARKET_CLOSED"

    print("Weekend protection: PASS")

    print()
    print("3. TRADING DAY START")
    print("-" * 60)

    start = pipeline.start(
        date(2026, 8, 24)
    )

    print(start)

    assert start["status"] == "STARTED"

    print("Trading day start: PASS")

    print()
    print("4. MARKET DATA")
    print("-" * 60)

    loaded = pipeline.get_candles()

    print("Candles:", len(loaded))

    assert len(loaded) == 30

    print("Market data: PASS")

    print()
    print("5. STRATEGY")
    print("-" * 60)

    strategy_result = pipeline.run_strategy(
        loaded
    )

    print(strategy_result)

    assert strategy_result["signal"]["action"] == "BUY"

    print("Strategy: PASS")

    print()
    print("6. ENTRY")
    print("-" * 60)

    entry = pipeline.run_entry()

    print(entry)

    execution = entry.get(
        "execution",
        {}
    )

    assert execution.get("status") == "EXECUTED"

    print("Entry execution: PASS")

    position = runtime.get_position()

    print("Position:", position)

    assert position is not None

    entry_price = position["entry_price"]

    print()
    print("7. POSITION MONITOR")
    print("-" * 60)

    hold = pipeline.monitor(
        entry_price * 1.01
    )

    print(hold)

    assert hold["status"] == "HOLD"

    print("Position monitor: PASS")

    print()
    print("8. TAKE PROFIT")
    print("-" * 60)

    target = pipeline.monitor(
        entry_price * 1.05
    )

    print(target)

    assert target["status"] == "TAKE_PROFIT"

    print("Take profit: PASS")

    print()
    print("9. STOP NEW ENTRIES")
    print("-" * 60)

    stopped = pipeline.stop_new_entries()

    print(stopped)

    assert (
        runtime.entries_enabled
        is False
    )

    print("Entry cutoff protection: PASS")

    print()
    print("10. EOD SAFETY")
    print("-" * 60)

    eod = pipeline.eod_exit(
        entry_price * 1.05
    )

    print(eod)

    assert eod["status"] == "NO_POSITION"

    print("EOD safety: PASS")

    print()
    print("11. REPORT")
    print("-" * 60)

    report = Phase7Report()

    generated = report.generate(
        {
            "status": "COMPLETED",
            "entry": entry,
            "monitor": [
                hold,
                target
            ],
            "eod": eod,
            "final_state": runtime.get_state(),
        },
        pipeline.events
    )

    print(
        "JSON:",
        generated["json"]
    )

    print(
        "CSV:",
        generated["csv"]
    )

    assert generated["json"]
    assert generated["csv"]

    print()
    print("12. STOP")
    print("-" * 60)

    pipeline.stop()

    assert pipeline.running is False

    print("Pipeline stopped")

    print()
    print("=" * 60)
    print("PHASE 7 INTEGRATION TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
