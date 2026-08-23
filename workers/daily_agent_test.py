import json

from agents.daily_trading_agent import DailyTradingAgent


def main():

    print("=" * 60)
    print("DAILY TRADING AGENT TEST")
    print("=" * 60)

    # -------------------------------------------------
    # LOAD HISTORICAL / PAPER MARKET DATA
    # -------------------------------------------------

    with open(
        "data/historical/nifty_sample.json",
        "r"
    ) as f:
        candles = json.load(f)

    print()
    print("Loaded candles:", len(candles))

    # -------------------------------------------------
    # CREATE AGENT
    # -------------------------------------------------

    agent = DailyTradingAgent()

    agent.start()

    # -------------------------------------------------
    # LOAD MARKET DATA
    # -------------------------------------------------

    agent.load_market_data(
        symbol="NIFTY",
        candles=candles
    )

    price = agent.get_latest_price("NIFTY")

    print()
    print("Latest NIFTY price:", price)

    # -------------------------------------------------
    # TRADING CYCLE
    # -------------------------------------------------

    print()
    print("=" * 60)
    print("TRADING CYCLE")
    print("=" * 60)

    cycle_result = agent.run_trading_cycle(
        symbol="NIFTY",
        quantity=1,
        short_period=5,
        long_period=10,
        daily_loss=0.0
    )

    print()
    print("TREND")
    print(cycle_result["trend"])

    print()
    print("DECISION")
    print(cycle_result["decision"])

    print()
    print("EXECUTION")
    print(cycle_result["execution"])

    # -------------------------------------------------
    # BACKTEST
    # -------------------------------------------------

    print()
    print("=" * 60)
    print("BACKTEST")
    print("=" * 60)

    backtest_result = agent.run_backtest(
        symbol="NIFTY",
        quantity=1,
        short_period=5,
        long_period=10,
        stop_loss_pct=0.02,
        take_profit_pct=0.04,
        max_daily_loss=1000
    )

    print()
    print("Total candles    :", backtest_result["total_candles"])
    print("Completed trades :", backtest_result["completed_trades"])
    print("Winning trades   :", backtest_result["winning_trades"])
    print("Losing trades    :", backtest_result["losing_trades"])
    print("Win rate         :", backtest_result["win_rate"])
    print("Total P&L        :", backtest_result["total_realized_pnl"])

    # -------------------------------------------------
    # STOP AGENT
    # -------------------------------------------------

    agent.stop()

    print()
    print("=" * 60)
    print("DAILY TRADING AGENT TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()