from agents.daily_trading_agent import DailyTradingAgent
from workers.scheduler.trading_scheduler import TradingScheduler


def main():

    print("=" * 60)
    print("TRADING SCHEDULER INTEGRATION TEST")
    print("=" * 60)

    candles = [
        {"open": 100, "high": 101, "low": 99, "close": 100},
        {"open": 100, "high": 102, "low": 99, "close": 101},
        {"open": 101, "high": 103, "low": 100, "close": 102},
        {"open": 102, "high": 104, "low": 101, "close": 103},
        {"open": 103, "high": 105, "low": 102, "close": 104},
        {"open": 104, "high": 106, "low": 103, "close": 105},
        {"open": 105, "high": 107, "low": 104, "close": 106},
        {"open": 106, "high": 108, "low": 105, "close": 107},
        {"open": 107, "high": 109, "low": 106, "close": 108},
        {"open": 108, "high": 110, "low": 107, "close": 109},
        {"open": 109, "high": 111, "low": 108, "close": 110},
        {"open": 110, "high": 112, "low": 109, "close": 111},
    ]

    symbol = "NIFTY"

    # -------------------------------------------------
    # CREATE DAILY AGENT
    # -------------------------------------------------

    agent = DailyTradingAgent()

    agent.load_market_data(
        symbol=symbol,
        candles=candles
    )

    agent.start()

    # -------------------------------------------------
    # CREATE SCHEDULER
    # -------------------------------------------------

    scheduler = TradingScheduler(
        daily_agent=agent,
        symbol=symbol
    )

    scheduler.start()

    # -------------------------------------------------
    # TRADING CYCLE
    # -------------------------------------------------

    print()
    print("RUNNING TRADING CYCLE")
    print("-" * 60)

    trading_result = agent.run_trading_cycle(
        symbol=symbol,
        quantity=1,
        short_period=3,
        long_period=5
    )

    print("Decision:")
    print(trading_result["decision"])

    print("Execution:")
    print(trading_result["execution"])

    print()
    print("POSITION")
    print("-" * 60)

    print(agent.get_position(symbol))
    print("Realized P&L:", agent.get_realized_pnl())

    # -------------------------------------------------
    # RUN SCHEDULER
    # -------------------------------------------------

    result = scheduler.run_cycle()

    print()
    print("SCHEDULER RESULT")
    print("-" * 60)

    print(result)

    # -------------------------------------------------
    # FINAL STATE
    # -------------------------------------------------

    print()
    print("FINAL STATE")
    print("-" * 60)

    print("Position:", agent.get_position(symbol))
    print("Realized P&L:", agent.get_realized_pnl())

    scheduler.stop()
    agent.stop()

    print()
    print("=" * 60)
    print("TRADING SCHEDULER TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()