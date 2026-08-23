from datetime import datetime, timedelta


class YahooMarketDataProvider:

    SYMBOL_MAP = {
        "NIFTY": "^NSEI",
        "NIFTY50": "^NSEI",
    }

    def __init__(self):

        try:
            import yfinance
            self.yf = yfinance
        except ImportError as exc:
            raise RuntimeError(
                "yfinance is required for YahooMarketDataProvider"
            ) from exc

    def resolve_symbol(self, symbol):

        symbol = str(symbol).upper().strip()

        return self.SYMBOL_MAP.get(
            symbol,
            symbol
        )

    def get_latest_price(self, symbol):

        ticker_symbol = self.resolve_symbol(symbol)

        ticker = self.yf.Ticker(
            ticker_symbol
        )

        history = ticker.history(
            period="1d",
            interval="1m",
            auto_adjust=False
        )

        if history.empty:
            raise RuntimeError(
                f"No market data returned for {symbol}"
            )

        latest = history.iloc[-1]

        return float(
            latest["Close"]
        )

    def get_candles(
        self,
        symbol,
        period="5d",
        interval="5m"
    ):

        ticker_symbol = self.resolve_symbol(symbol)

        ticker = self.yf.Ticker(
            ticker_symbol
        )

        history = ticker.history(
            period=period,
            interval=interval,
            auto_adjust=False
        )

        if history.empty:
            raise RuntimeError(
                f"No market data returned for {symbol}"
            )

        candles = []

        for timestamp, row in history.iterrows():

            candles.append(
                {
                    "timestamp": timestamp.isoformat(),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": float(row["Volume"]),
                }
            )

        return candles

    def get_intraday_candles(
        self,
        symbol,
        interval="5m"
    ):

        return self.get_candles(
            symbol=symbol,
            period="1d",
            interval=interval
        )