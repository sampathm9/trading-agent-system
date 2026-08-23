import json

from workers.backtest.backtest_worker import BacktestWorker


def main():

    print("=" * 60)
    print("BACKTEST V2 TEST")
    print("=" * 60)

    with open("data/historical/nifty_sample.json", "r") as f:
        candles = json.load(f)

    print(f"Loaded candles: {len(candles)}")

    backtest = BacktestWorker()

    result = backtest.run(
        candles=candles,
        symbol="NIFTY",
        quantity=1,
        short_period=5,
        long_period=10,
        stop_loss_pct=0.02,
        take_profit_pct=0.04,
        max_daily_loss=1000
    )

    print()
    print("BACKTEST RESULT")
    print("-" * 60)

    print(f"Symbol           : {result['symbol']}")
    print(f"Total candles    : {result['total_candles']}")
    print(f"Total orders     : {result['total_orders']}")
    print(f"Completed trades : {result['completed_trades']}")
    print(f"Winning trades   : {result['winning_trades']}")
    print(f"Losing trades    : {result['losing_trades']}")
    print(f"Win rate         : {result['win_rate']:.2f}%")
    print(f"Average win      : {result['average_win']:.2f}")
    print(f"Average loss     : {result['average_loss']:.2f}")
    print(f"Max drawdown     : {result['max_drawdown']:.2f}")
    print(f"Total P&L        : {result['total_realized_pnl']:.2f}")

    print()
    print("TRADES")
    print("-" * 60)

    for trade in result["trades"]:
        print(trade)

    print()
    print("=" * 60)
    print("BACKTEST V2 TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()