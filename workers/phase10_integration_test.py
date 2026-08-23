from datetime import date, timedelta
from copy import deepcopy

from workers.intraday.candle_replay import (
    CandleReplay,
)

from workers.intraday.intraday_controller import (
    IntradayController,
)

from agents.daily_trading_agent import (
    DailyTradingAgent,
)

from workers.runtime.paper_runtime import (
    PaperTradingRuntime,
)

from workers.calendar.market_calendar import (
    NSEMarketCalendar,
)

from workers.pipeline.trading_pipeline import (
    TradingPipeline,
)

from workers.strategy.strategy_engine import (
    StrategyEngine,
)

from workers.paper_testing.multi_day_paper_tester import (
    MultiDayPaperTester,
)

from workers.paper_testing.phase10_report import (
    Phase10Report,
)


class TestMarketDataWorker:

    def __init__(self, candles):

        self.candles = list(
            candles
        )

    def get_candles(
        self,
        symbol,
    ):

        return list(
            self.candles
        )


def shift_candles(
    candles,
    trading_date,
):

    shifted = []

    for candle in candles:

        item = deepcopy(
            candle
        )

        timestamp = item.get(
            "timestamp"
        )

        if timestamp:

            original = (
                timestamp
                if hasattr(
                    timestamp,
                    "date",
                )
                else None
            )

            if original is not None:

                item["timestamp"] = (
                    original.replace(
                        year=trading_date.year,
                        month=trading_date.month,
                        day=trading_date.day,
                    )
                )

            else:

                text = str(
                    timestamp
                )

                if "T" in text:

                    clock = text.split(
                        "T",
                        1,
                    )[1]

                    item["timestamp"] = (
                        trading_date.isoformat()
                        + "T"
                        + clock
                    )

        shifted.append(
            item
        )

    return shifted


def build_controller():

    base_candles = (
        CandleReplay.build_test_day()
    )

    agent = DailyTradingAgent()

    agent.load_market_data(
        "NIFTY",
        base_candles,
    )

    runtime = PaperTradingRuntime(
        agent=agent,
        market_calendar=NSEMarketCalendar(),
        symbol="NIFTY",
        quantity=1,
        stop_loss_pct=0.02,
        take_profit_pct=0.04,
        max_daily_loss=1000,
    )

    market_data_worker = (
        TestMarketDataWorker(
            base_candles
        )
    )

    strategy_engine = StrategyEngine()

    pipeline = TradingPipeline(
        runtime=runtime,
        market_data_worker=market_data_worker,
        strategy_engine=strategy_engine,
        market_calendar=NSEMarketCalendar(),
        symbol="NIFTY",
    )

    return IntradayController(
        pipeline=pipeline,
        market_calendar=NSEMarketCalendar(),
        symbol="NIFTY",
        entry_cutoff="15:00",
        market_close="15:30",
    )


def build_replay(
    trading_date,
):

    base = CandleReplay.build_test_day()

    return shift_candles(
        base,
        trading_date,
    )


def verify_price_ledger(
    results,
):

    checked = 0

    for result in results:

        for trade in result.get(
            "trades",
            [],
        ):

            price = trade.get(
                "price"
            )

            if price is None:

                return False

            try:

                numeric_price = float(
                    price
                )

            except (
                TypeError,
                ValueError,
            ):

                return False

            if numeric_price <= 0:

                return False

            checked += 1

    return checked > 0


def main():

    print("=" * 60)
    print(
        "PHASE 10 EXTENDED PAPER TRADING TEST"
    )
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. BUILD
    # ---------------------------------------------------------

    print()
    print("1. BUILD COMPONENTS")
    print("-" * 60)

    base = (
        CandleReplay.build_test_day()
    )

    print(
        "Base replay candles:",
        len(base),
    )

    assert len(base) == 76

    tester = MultiDayPaperTester(
        controller_factory=(
            build_controller
        ),
        replay_factory=(
            build_replay
        ),
    )

    print(
        "Extended paper tester: READY"
    )

    # ---------------------------------------------------------
    # 2. WEEKEND PROTECTION
    # ---------------------------------------------------------

    print()
    print("2. WEEKEND PROTECTION")
    print("-" * 60)

    controller = build_controller()

    weekend = controller.start(
        date(2026, 8, 23)
    )

    print(weekend)

    assert (
        weekend["status"]
        == "MARKET_CLOSED"
    )

    print(
        "Weekend protection: PASS"
    )

    # ---------------------------------------------------------
    # 3. MULTIPLE MARKET DAYS
    # ---------------------------------------------------------

    print()
    print("3. MULTIPLE MARKET DAYS")
    print("-" * 60)

    trading_dates = [
        date(2026, 8, 24),
        date(2026, 8, 25),
        date(2026, 8, 26),
        date(2026, 8, 27),
        date(2026, 8, 28),
    ]

    results = tester.run_days(
        trading_dates
    )

    for result in results:

        print(
            result["date"],
            "=>",
            result["status"],
            "candles=",
            result["processed_candles"],
            "trades=",
            result["trade_count"],
            "P&L=",
            result["realized_pnl"],
        )

    assert len(results) == 5

    assert all(
        result["status"]
        == "COMPLETED"
        for result in results
    )

    assert all(
        result["processed_candles"]
        == 76
        for result in results
    )

    print(
        "Multiple market days: PASS"
    )

    # ---------------------------------------------------------
    # 4. POSITION SAFETY
    # ---------------------------------------------------------

    print()
    print("4. POSITION SAFETY")
    print("-" * 60)

    for result in results:

        print(
            result["date"],
            "position_open=",
            result["position_open"],
        )

        assert (
            result["position_open"]
            is False
        )

    print(
        "All positions closed: PASS"
    )

    # ---------------------------------------------------------
    # 5. ENTRY CUTOFF
    # ---------------------------------------------------------

    print()
    print("5. ENTRY CUTOFF")
    print("-" * 60)

    for result in results:

        print(
            result["date"],
            "entries_stopped=",
            result["entries_stopped"],
        )

        assert (
            result["entries_stopped"]
            is True
        )

    print(
        "Entry cutoff protection: PASS"
    )

    # ---------------------------------------------------------
    # 6. TRADE GENERATION
    # ---------------------------------------------------------

    print()
    print("6. TRADE GENERATION")
    print("-" * 60)

    total_entries = sum(
        result["entries"]
        for result in results
    )

    total_exits = sum(
        result["exits"]
        for result in results
    )

    print(
        "Total entries:",
        total_entries,
    )

    print(
        "Total exits:",
        total_exits,
    )

    assert total_entries > 0
    assert total_exits > 0

    print(
        "Trade generation: PASS"
    )

    # ---------------------------------------------------------
    # 7. P&L
    # ---------------------------------------------------------

    print()
    print("7. P&L VERIFICATION")
    print("-" * 60)

    summary = tester.summary()

    print(
        "Days:",
        summary["days"],
    )

    print(
        "Candles:",
        summary["total_candles"],
    )

    print(
        "Trades:",
        summary["total_trades"],
    )

    print(
        "Realized P&L:",
        summary["total_realized_pnl"],
    )

    assert (
        summary["days"]
        == 5
    )

    assert (
        summary["total_candles"]
        == 380
    )

    assert (
        summary["all_sessions_completed"]
        is True
    )

    print(
        "P&L aggregation: PASS"
    )

    # ---------------------------------------------------------
    # 8. RISK VERIFICATION
    # ---------------------------------------------------------

    print()
    print("8. RISK VERIFICATION")
    print("-" * 60)

    assert all(
        result["position_open"]
        is False
        for result in results
    )

    assert all(
        result["entries_stopped"]
        is True
        for result in results
    )

    print(
        "Risk controls: PASS"
    )

    # ---------------------------------------------------------
    # 9. EXECUTION / LEDGER
    # ---------------------------------------------------------

    print()
    print(
        "9. EXECUTION PRICE / LEDGER"
    )
    print("-" * 60)

    ledger_ok = (
        verify_price_ledger(
            results
        )
    )

    print(
        "Trade ledger valid:",
        ledger_ok,
    )

    assert ledger_ok is True

    print(
        "Execution ledger: PASS"
    )

    # ---------------------------------------------------------
    # 10. EOD
    # ---------------------------------------------------------

    print()
    print("10. EOD EXIT VERIFICATION")
    print("-" * 60)

    eod_verified = True

    for result in results:

        if result["position_open"]:

            eod_verified = False

        print(
            result["date"],
            "EOD position closed:",
            not result["position_open"],
        )

    assert eod_verified

    print(
        "EOD exits: PASS"
    )

    # ---------------------------------------------------------
    # 11. FAILURE PROTECTION
    # ---------------------------------------------------------

    print()
    print("11. FAILURE PROTECTION")
    print("-" * 60)

    invalid_dates = [
        date(2026, 8, 23),
    ]

    for invalid_date in invalid_dates:

        failure_controller = (
            build_controller()
        )

        failure = (
            failure_controller.start(
                invalid_date
            )
        )

        print(
            invalid_date,
            "=>",
            failure["status"],
        )

        assert (
            failure["status"]
            == "MARKET_CLOSED"
        )

    print(
        "Failure protection: PASS"
    )

    # ---------------------------------------------------------
    # 12. REPORTS
    # ---------------------------------------------------------

    print()
    print("12. REPORTS")
    print("-" * 60)

    report_writer = Phase10Report(
        "reports/phase10"
    )

    report_files = (
        report_writer.save(
            results,
            summary,
        )
    )

    print(
        "JSON:",
        report_files["json"],
    )

    print(
        "Daily CSV:",
        report_files["daily_csv"],
    )

    print(
        "Trades CSV:",
        report_files["trades_csv"],
    )

    # ---------------------------------------------------------
    # 13. FINAL VALIDATION
    # ---------------------------------------------------------

    print()
    print("13. FINAL VALIDATION")
    print("-" * 60)

    assert (
        summary["all_sessions_completed"]
        is True
    )

    assert (
        summary["all_positions_closed"]
        is True
    )

    assert (
        summary["all_entry_cutoffs"]
        is True
    )

    assert ledger_ok is True

    print(
        "All Phase 10 requirements: PASS"
    )

    # ---------------------------------------------------------
    # COMPLETE
    # ---------------------------------------------------------

    print()
    print("=" * 60)
    print(
        "PHASE 10 INTEGRATION TEST PASSED"
    )
    print("=" * 60)


if __name__ == "__main__":

    main()
