from datetime import datetime

from workers.data_provider.yahoo_provider import (
    YahooMarketDataProvider
)

from workers.market_data.market_data_validator import (
    MarketDataValidator
)

from workers.market_data.market_data_cache import (
    MarketDataCache
)


class LiveMarketDataWorker:

    def __init__(
        self,
        provider=None,
        validator=None,
        cache=None,
    ):

        self.provider = (
            provider
            or YahooMarketDataProvider()
        )

        self.validator = (
            validator
            or MarketDataValidator()
        )

        self.cache = (
            cache
            or MarketDataCache()
        )

    def fetch_candles(
        self,
        symbol,
        period="5d",
        interval="5m",
    ):

        candles = self.provider.get_candles(
            symbol=symbol,
            period=period,
            interval=interval,
        )

        cleaned = (
            self.validator.clean_candles(
                candles
            )
        )

        validation = (
            self.validator.validate_candles(
                cleaned
            )
        )

        if not validation["valid"]:

            raise RuntimeError(
                "Market data validation failed"
            )

        self.cache.save(
            symbol,
            cleaned
        )

        return cleaned

    def fetch_intraday(
        self,
        symbol,
        interval="5m",
    ):

        return self.fetch_candles(
            symbol=symbol,
            period="1d",
            interval=interval,
        )

    def latest_price(self, symbol):

        price = self.provider.get_latest_price(
            symbol
        )

        if price <= 0:

            raise RuntimeError(
                "Invalid latest market price"
            )

        return price

    def refresh(
        self,
        symbol,
        period="5d",
        interval="5m",
    ):

        try:

            candles = self.fetch_candles(
                symbol=symbol,
                period=period,
                interval=interval,
            )

            return {
                "status": "UPDATED",
                "symbol": symbol,
                "candles": len(candles),
                "latest_price": (
                    float(
                        candles[-1]["close"]
                    )
                    if candles
                    else None
                ),
                "timestamp": (
                    datetime.now().isoformat()
                ),
            }

        except Exception as exc:

            cached = self.cache.load(
                symbol
            )

            return {
                "status": "ERROR",
                "symbol": symbol,
                "error": str(exc),
                "cached_candles": len(cached),
                "timestamp": (
                    datetime.now().isoformat()
                ),
            }