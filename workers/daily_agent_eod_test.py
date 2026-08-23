import json

from agents.daily_trading_agent import DailyTradingAgent


def main():

    print("=" * 60)
    print("DAILY AGENT EOD INTEGRATION TEST")
    print("=" * 60)

    # -------------------------------------------------
    # LOAD DATA
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
    print("Latest price:", price)

    # -------------------------------------------------
    # RUN TRADING CYCLE
    # -------------------------------------------------

    print()
    print("=" * 60)
    print("TRADING CYCLE")
    print("=" * 60)

    result = agent.run_trading_cycle(
        symbol="NIFTY",
        quantity=1
    )

    print()
    print("Decision:")
    print(result["decision"])

    print()
    print("Execution:")
    print(result["execution"])

    # -------------------------------------------------
    # CHECK POSITION
    # -------------------------------------------------

    print()
    print("=" * 60)
    print("POSITION BEFORE EOD")
    print("=" * 60)

    position = agent.get_position("NIFTY")

    print("Position:", position)
    print("Realized P&L:", agent.get_realized_pnl())

    # -------------------------------------------------
    # EOD EXIT
    # -------------------------------------------------

    print()
    print("=" * 60)
    print("EOD EXIT")
    print("=" * 60)

    eod_result = agent.close_all_positions(
        current_prices={
            "NIFTY": 150
        }
    )

    print()
    print("EOD RESULT:")
    print(eod_result)

    # -------------------------------------------------
    # CHECK FINAL STATE
    # -------------------------------------------------

    print()
    print("=" * 60)
    print("FINAL STATE")
    print("=" * 60)

    print("Position:", agent.get_position("NIFTY"))
    print("Realized P&L:", agent.get_realized_pnl())

    agent.stop()

    print()
    print("=" * 60)
    print("DAILY AGENT EOD TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()