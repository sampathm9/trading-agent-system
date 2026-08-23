from datetime import datetime


class Phase3DataValidator:

    REQUIRED_FIELDS = {
        "open",
        "high",
        "low",
        "close"
    }

    def validate_candle(
        self,
        candle,
        index=0
    ):

        if not isinstance(candle, dict):

            raise ValueError(
                f"Candle {index} is not a dictionary"
            )

        missing = (
            self.REQUIRED_FIELDS
            - set(candle.keys())
        )

        if missing:

            raise ValueError(
                f"Candle {index} missing fields: "
                + ", ".join(
                    sorted(missing)
                )
            )

        try:

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

        except (
            TypeError,
            ValueError
        ) as exc:

            raise ValueError(
                f"Candle {index} contains "
                f"non-numeric OHLC data"
            ) from exc

        if min(
            open_price,
            high_price,
            low_price,
            close_price
        ) <= 0:

            raise ValueError(
                f"Candle {index} contains "
                f"non-positive price"
            )

        if high_price < max(
            open_price,
            close_price
        ):

            raise ValueError(
                f"Candle {index}: invalid high"
            )

        if low_price > min(
            open_price,
            close_price
        ):

            raise ValueError(
                f"Candle {index}: invalid low"
            )

        return True

    def validate_timestamp(
        self,
        candle,
        index=0
    ):

        timestamp = (
            candle.get("timestamp")
            or candle.get("datetime")
            or candle.get("date")
        )

        if timestamp is None:

            return True

        if isinstance(
            timestamp,
            datetime
        ):

            return True

        if not isinstance(
            timestamp,
            str
        ):

            raise ValueError(
                f"Candle {index}: invalid timestamp"
            )

        if not timestamp.strip():

            raise ValueError(
                f"Candle {index}: empty timestamp"
            )

        return True

    def validate(
        self,
        candles
    ):

        if not isinstance(
            candles,
            list
        ):

            raise ValueError(
                "Historical data must be a list"
            )

        if not candles:

            raise ValueError(
                "Historical data is empty"
            )

        previous_timestamp = None

        for index, candle in enumerate(
            candles
        ):

            self.validate_candle(
                candle,
                index
            )

            self.validate_timestamp(
                candle,
                index
            )

            timestamp = (
                candle.get("timestamp")
                or candle.get("datetime")
                or candle.get("date")
            )

            if timestamp:

                timestamp_string = str(
                    timestamp
                )

                if (
                    previous_timestamp
                    and timestamp_string
                    < previous_timestamp
                ):

                    raise ValueError(
                        "Historical data is not "
                        "chronologically ordered"
                    )

                previous_timestamp = (
                    timestamp_string
                )

        return {
            "valid": True,
            "candle_count": len(candles)
        }