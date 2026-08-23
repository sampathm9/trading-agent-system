from execution.paper_broker import PaperBroker
from workers.execution.execution_worker import ExecutionWorker
from workers.trading.trading_cycle_worker import TradingCycleWorker


def main():

    print("=" * 60)
    print("MULTI-CANDLE PAPER TRADING TEST")
    print("=" * 60)

    broker = PaperBroker()
    execution_worker = ExecutionWorker(broker=broker)

    trading_cycle = TradingCycleWorker(
        execution_worker=execution_worker
    )

    symbol = "NIFTY"
    quantity = 1

    # Bullish candles -> BUY
    bullish_candles = [
        {"open": 100, "high": 103, "low": 99, "close": 101},
        {"open": 101, "high": 105, "low": 100, "close": 103},
        {"open": 103, "high": 107, "low": 102, "close": 105},
        {"open": 105, "high": 109, "low": 104, "close": 107},
        {"open": 107, "high": 111, "low": 106, "close": 109},
        {"open": 109, "high": 113, "low": 108, "close": 111},
        {"open": 111, "high": 115, "low": 110, "close": 113},
        {"open": 113, "high": 117, "low": 112, "close": 115},
        {"open": 115, "high": 119, "low": 114, "close": 117},
        {"open": 117, "high": 121, "low": 116, "close": 119},
    ]

    print()
    print("CYCLE 1")
    print("-" * 60)

    result = trading_cycle.run(
        candles=bullish_candles,
        symbol=symbol,
        quantity=quantity,
        price=119,
        position=broker.get_position(symbol)
    )

    print("Decision:", result["decision"])
    print("Execution:", result["execution"])
    print("Position:", broker.get_position(symbol))

    print()
    print("CYCLE 2")
    print("-" * 60)

    result = trading_cycle.run(
        candles=bullish_candles,
        symbol=symbol,
        quantity=quantity,
        price=122,
        position=broker.get_position(symbol)
    )

    print("Decision:", result["decision"])
    print("Execution:", result["execution"])
    print("Position:", broker.get_position(symbol))

    print()
    print("FINAL STATE")
    print("-" * 60)
    print("Position:", broker.get_position(symbol))
    print("Realized P&L:", broker.get_realized_pnl())

    print()
    print("=" * 60)
    print("MULTI-CANDLE PAPER TRADING TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()