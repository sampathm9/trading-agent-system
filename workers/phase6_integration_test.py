from workers.strategy.indicator_worker import (
    IndicatorWorker
)

from workers.strategy.strategy_config import (
    StrategyConfig
)

from workers.strategy.trend_strategy import (
    TrendStrategy
)

from workers.signals.signal_worker import (
    SignalWorker
)

from workers.strategy.strategy_engine import (
    StrategyEngine
)

from workers.strategy.strategy_report import (
    StrategyReport
)


def build_bullish_candles():

    candles = []

    for i in range(22):

        close = 100 + i

        candles.append({
            "timestamp": (
                f"2026-08-24T09:{15 + i:02d}:00"
            ),
            "open": close - 1,
            "high": close + 1,
            "low": close - 2,
            "close": close,
            "volume": 1000 + i,
        })

    return candles


def build_bearish_candles():

    candles = []

    for i in range(22):

        close = 200 - i

        candles.append({
            "timestamp": (
                f"2026-08-24T09:{15 + i:02d}:00"
            ),
            "open": close + 1,
            "high": close + 2,
            "low": close - 1,
            "close": close,
            "volume": 1000 + i,
        })

    return candles


def main():

    print("=" * 60)
    print("PHASE 6 STRATEGY & SIGNAL INTEGRATION TEST")
    print("=" * 60)

    print()
    print("1. INDICATORS")
    print("-" * 60)

    indicators = IndicatorWorker()

    values = [
        100,
        101,
        102,
        103,
        104,
        105,
        106,
        107,
        108,
        109,
    ]

    sma = indicators.sma(
        values,
        5
    )

    momentum = indicators.momentum(
        values,
        5
    )

    print(
        "SMA:",
        sma
    )

    print(
        "Momentum:",
        momentum
    )

    assert sma == 107.0
    assert momentum > 0

    print()
    print("2. BULLISH TREND")
    print("-" * 60)

    trend_strategy = TrendStrategy()

    bullish_candles = (
        build_bullish_candles()
    )

    bullish_trend = (
        trend_strategy.analyze(
            bullish_candles,
            short_period=5,
            long_period=10,
            momentum_period=5,
        )
    )

    print(
        bullish_trend
    )

    assert (
        bullish_trend["trend"]
        == "BULLISH"
    )

    print()
    print("3. BEARISH TREND")
    print("-" * 60)

    bearish_candles = (
        build_bearish_candles()
    )

    bearish_trend = (
        trend_strategy.analyze(
            bearish_candles,
            short_period=5,
            long_period=10,
            momentum_period=5,
        )
    )

    print(
        bearish_trend
    )

    assert (
        bearish_trend["trend"]
        == "BEARISH"
    )

    print()
    print("4. SIGNAL GENERATION")
    print("-" * 60)

    signal_worker = SignalWorker(
        minimum_confidence=0.60
    )

    bullish_signal = (
        signal_worker.generate(
            bullish_trend
        )
    )

    bearish_signal = (
        signal_worker.generate(
            bearish_trend
        )
    )

    print(
        "Bullish signal:",
        bullish_signal
    )

    print(
        "Bearish signal:",
        bearish_signal
    )

    assert (
        bullish_signal["action"]
        == "BUY"
    )

    assert (
        bearish_signal["action"]
        == "SELL"
    )

    print()
    print("5. STRATEGY ENGINE")
    print("-" * 60)

    engine = StrategyEngine(
        config=StrategyConfig(
            short_period=5,
            long_period=10,
            momentum_period=5,
            minimum_confidence=0.60,
        )
    )

    result = engine.analyze(
        bullish_candles
    )

    print(
        result
    )

    assert (
        result["status"]
        == "COMPLETED"
    )

    assert (
        result["signal"]["action"]
        == "BUY"
    )

    print()
    print("6. SIGNAL HISTORY")
    print("-" * 60)

    history = (
        engine.get_signal_history()
    )

    print(
        "Signals:",
        len(history)
    )

    assert len(history) == 1

    print()
    print("7. REPORTS")
    print("-" * 60)

    reporter = StrategyReport()

    json_path = reporter.save_json(
        result
    )

    csv_path = (
        reporter.save_signal_history(
            history
        )
    )

    print(
        "JSON:",
        json_path
    )

    print(
        "CSV:",
        csv_path
    )

    print()
    print("=" * 60)
    print("PHASE 6 INTEGRATION TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()