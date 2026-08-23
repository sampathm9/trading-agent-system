from datetime import datetime


class MarketDataValidator:

    REQUIRED_FIELDS = {
        "timestamp",
        "open",
        "high",
        "low",
        "close",
    }

    def validate_candle(self, candle):

        if not isinstance(candle, dict):

            return False, "CANDLE_NOT_DICTIONARY"

        missing = (
            self.REQUIRED_FIELDS
            - set(candle.keys())
        )

        if missing:

            return False, (
                f"MISSING_FIELDS: {sorted(missing)}"
            )

        try:

            timestamp = candle["timestamp"]

            if isinstance(timestamp, str):
                datetime.fromisoformat(
                    timestamp.replace(
                        "Z",
                        "+00:00"
                    )
                )

            open_price = float(
                candle["open"]
            )

            high_price = float(
                candle["high"]
            )

            low_price = float(
                candle["low"]
            )

            close_price = float(
                candle["close"]
            )

        except Exception:

            return False, "INVALID_CANDLE_VALUES"

        if open_price <= 0:
            return False, "INVALID_OPEN"

        if high_price <= 0:
            return False, "INVALID_HIGH"

        if low_price <= 0:
            return False, "INVALID_LOW"

        if close_price <= 0:
            return False, "INVALID_CLOSE"

        if high_price < low_price:

            return False, "HIGH_BELOW_LOW"

        if high_price < max(
            open_price,
            close_price
        ):

            return False, "HIGH_BELOW_OHLC"

        if low_price > min(
            open_price,
            close_price
        ):

            return False, "LOW_ABOVE_OHLC"

        return True, "VALID"

    def validate_candles(self, candles):

        if not isinstance(candles, list):

            return {
                "valid": False,
                "reason": "CANDLES_NOT_LIST",
                "total": 0,
                "valid_count": 0,
                "invalid_count": 0,
            }

        valid_count = 0
        invalid_count = 0
        errors = []

        previous_timestamp = None

        for index, candle in enumerate(candles):

            valid, reason = self.validate_candle(
                candle
            )

            if not valid:

                invalid_count += 1

                errors.append(
                    {
                        "index": index,
                        "reason": reason,
                    }
                )

                continue

            timestamp = candle["timestamp"]

            if (
                previous_timestamp is not None
                and str(timestamp) <= str(previous_timestamp)
            ):

                invalid_count += 1

                errors.append(
                    {
                        "index": index,
                        "reason": "TIMESTAMP_NOT_INCREASING",
                    }
                )

                continue

            previous_timestamp = timestamp

            valid_count += 1

        return {
            "valid": invalid_count == 0,
            "reason": (
                "VALID"
                if invalid_count == 0
                else "INVALID_DATA"
            ),
            "total": len(candles),
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "errors": errors,
        }

    def clean_candles(self, candles):

        cleaned = []
        seen = set()

        for candle in candles:

            valid, _ = self.validate_candle(
                candle
            )

            if not valid:
                continue

            timestamp = str(
                candle["timestamp"]
            )

            if timestamp in seen:
                continue

            seen.add(timestamp)

            cleaned.append(candle)

        cleaned.sort(
            key=lambda item: str(
                item["timestamp"]
            )
        )

        return cleaned