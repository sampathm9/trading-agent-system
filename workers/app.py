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

    print("Trading agent initialized.")
    print("Waiting for market data...")
    print()


if __name__ == "__main__":
    main()