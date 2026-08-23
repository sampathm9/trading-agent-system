from workers.backtest.backtest_worker import BacktestWorker


class FixedDecisionWorker:

    def __init__(self, action):
        self.action = action

    def decide(self, trend):
        return {
            "trend": trend,
            "action": self.action,
            "confidence": 1.0
        }


def run_take_profit_test():

    print()
    print("=" * 60)
    print("TAKE PROFIT TEST")
    print("=" * 60)

    candles = [
        {"open": 100, "high": 101, "low": 99, "close": 100},
        {"open": 100, "high": 102, "low": 99, "close": 100},
        {"open": 100, "high": 102, "low": 99, "close": 100},
        {"open": 100, "high": 102, "low": 99, "close": 100},
        {"open": 100, "high": 102, "low": 99, "close": 100},

        # Entry at 100
        {"open": 100, "high": 101, "low": 99, "close": 100},

        # Price reaches 105 -> Take Profit
        {"open": 100, "high": 106, "low": 104, "close": 105},
    ]

    backtest = BacktestWorker(
        decision_worker=FixedDecisionWorker("BUY")
    )

    result = backtest.run(
        candles=candles,
        symbol="NIFTY",
        quantity=1,
        short_period=2,
        long_period=5,
        stop_loss_pct=0.02,
        take_profit_pct=0.04
    )

    print("Trades:")

    for trade in result["trades"]:
        print(trade)

    print()
    print("Total P&L:", result["total_realized_pnl"])

    return result


def run_stop_loss_test():

    print()
    print("=" * 60)
    print("STOP LOSS TEST")
    print("=" * 60)

    candles = [
        {"open": 100, "high": 101, "low": 99, "close": 100},
        {"open": 100, "high": 102, "low": 99, "close": 100},
        {"open": 100, "high": 102, "low": 99, "close": 100},
        {"open": 100, "high": 102, "low": 99, "close": 100},
        {"open": 100, "high": 102, "low": 99, "close": 100},

        # Entry at 100
        {"open": 100, "high": 101, "low": 99, "close": 100},

        # Price falls to 97 -> Stop Loss
        {"open": 100, "high": 101, "low": 97, "close": 97},
    ]

    backtest = BacktestWorker(
        decision_worker=FixedDecisionWorker("BUY")
    )

    result = backtest.run(
        candles=candles,
        symbol="NIFTY",
        quantity=1,
        short_period=2,
        long_period=5,
        stop_loss_pct=0.02,
        take_profit_pct=0.04
    )

    print("Trades:")

    for trade in result["trades"]:
        print(trade)

    print()
    print("Total P&L:", result["total_realized_pnl"])

    return result


def main():

    print("=" * 60)
    print("EXIT MANAGEMENT TEST")
    print("=" * 60)

    take_profit_result = run_take_profit_test()
    stop_loss_result = run_stop_loss_test()

    print()
    print("=" * 60)
    print("EXIT MANAGEMENT SUMMARY")
    print("=" * 60)

    print(
        "Take profit triggered:",
        any(
            trade["type"] == "TAKE_PROFIT"
            for trade in take_profit_result["trades"]
        )
    )

    print(
        "Stop loss triggered:",
        any(
            trade["type"] == "STOP_LOSS"
            for trade in stop_loss_result["trades"]
        )
    )

    print("=" * 60)
    print("EXIT MANAGEMENT TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()