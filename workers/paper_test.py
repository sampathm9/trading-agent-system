import json

from workers.data.market_data_worker import MarketDataWorker
from workers.trading.trading_cycle_worker import TradingCycleWorker


def main():

    print("=" * 60)
    print("PAPER TRADING TEST")
    print("=" * 60)

    with open("data/historical/nifty_sample.json", "r") as f:
        candles = json.load(f)

    print(f"Loaded candles: {len(candles)}")

    market_data = MarketDataWorker()

    market_data.load_candles(
        symbol="NIFTY",
        candles=candles
    )

    price = market_data.latest_price("NIFTY")

    print(f"Latest NIFTY price: {price}")

    trading_cycle = TradingCycleWorker()

    result = trading_cycle.run(
        candles=candles,
        symbol="NIFTY",
        quantity=1,
        price=price,
        short_period=5,
        long_period=10,
        daily_loss=0.0,
        position=None
    )

    print()
    print("TREND RESULT")
    print(result["trend"])

    print()
    print("DECISION")
    print(result["decision"])

    print()
    print("EXECUTION")
    print(result["execution"])

    print()
    print("=" * 60)
    print("PAPER TRADING TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()