import json

from workers.data.market_data_worker import MarketDataWorker
from workers.trading.trading_cycle_worker import TradingCycleWorker


def main():
    print("=" * 60)
    print("TRADING AGENT SYSTEM")
    print("=" * 60)
    print("Starting paper-trading mode...")
    print()

    print("System components:")
    print("- Market data worker     : READY")
    print("- Intelligence workers   : READY")
    print("- Strategy worker        : READY")
    print("- Risk worker            : READY")
    print("- Execution worker       : READY")
    print("- Position manager       : READY")
    print("- Backtest worker        : READY")
    print()

    market_data = MarketDataWorker()
    trading_cycle = TradingCycleWorker()

    with open("data/historical/nifty_sample.json", "r") as f:
        candles = json.load(f)

    market_data.load_candles("NIFTY", candles)

    symbol = "NIFTY"
    quantity = 1

    latest_price = market_data.latest_price(symbol)

    print("Trading agent initialized.")
    print(f"Loaded candles           : {len(candles)}")
    print(f"Latest {symbol} price    : {latest_price}")
    print()

    result = trading_cycle.run(
        candles=candles,
        symbol=symbol,
        quantity=quantity,
        price=latest_price,
        short_period=5,
        long_period=10,
        daily_loss=0.0,
        position=None
    )

    print("TRADING CYCLE RESULT")
    print("-" * 60)

    print("TREND")
    print(result["trend"])
    print()

    print("DECISION")
    print(result["decision"])
    print()

    print("EXECUTION")
    print(result["execution"])
    print()

    print("=" * 60)
    print("PAPER TRADING CYCLE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()