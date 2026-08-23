from workers.market_data.market_data_validator import (
    MarketDataValidator
)

from workers.market_data.market_data_cache import (
    MarketDataCache
)

from workers.data_provider.yahoo_provider import (
    YahooMarketDataProvider
)


def main():

    print("=" * 60)
    print("PHASE 5 MARKET DATA INTEGRATION TEST")
    print("=" * 60)

    print()
    print("1. VALIDATOR")
    print("-" * 60)

    validator = MarketDataValidator()

    valid_candle = {
        "timestamp": "2026-08-24T09:15:00",
        "open": 100,
        "high": 105,
        "low": 99,
        "close": 103,
        "volume": 1000,
    }

    valid, reason = validator.validate_candle(
        valid_candle
    )

    print(
        "Valid candle:",
        valid,
        reason
    )

    assert valid is True

    invalid_candle = {
        "timestamp": "2026-08-24T09:20:00",
        "open": 100,
        "high": 95,
        "low": 99,
        "close": 103,
    }

    valid, reason = validator.validate_candle(
        invalid_candle
    )

    print(
        "Invalid candle:",
        valid,
        reason
    )

    assert valid is False

    print()
    print("2. CACHE")
    print("-" * 60)

    cache = MarketDataCache(
        "data/market"
    )

    candles = [
        valid_candle
    ]

    path = cache.save(
        "PHASE5_TEST",
        candles
    )

    loaded = cache.load(
        "PHASE5_TEST"
    )

    print(
        "Cache file:",
        path
    )

    print(
        "Loaded candles:",
        len(loaded)
    )

    assert len(loaded) == 1

    print()
    print("3. PROVIDER")
    print("-" * 60)

    provider = YahooMarketDataProvider()

    resolved = provider.resolve_symbol(
        "NIFTY"
    )

    print(
        "NIFTY provider symbol:",
        resolved
    )

    assert resolved == "^NSEI"

    print()
    print("4. REAL MARKET DATA")
    print("-" * 60)

    try:

        candles = provider.get_candles(
            "NIFTY",
            period="1d",
            interval="5m",
        )

        print(
            "Real candles received:",
            len(candles)
        )

        if candles:

            print(
                "Latest candle:",
                candles[-1]
            )

    except Exception as exc:

        print(
            "Provider unavailable:",
            exc
        )

        print(
            "This test can continue because "
            "provider availability depends on network/data service."
        )

    print()
    print("=" * 60)
    print("PHASE 5 INTEGRATION TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()