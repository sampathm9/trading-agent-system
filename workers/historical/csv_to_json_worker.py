import csv
import json
from datetime import datetime
from pathlib import Path


class CSVToJSONWorker:

    REQUIRED_COLUMNS = {
        "open",
        "high",
        "low",
        "close"
    }

    COLUMN_ALIASES = {
        "Open": "open",
        "OPEN": "open",
        "High": "high",
        "HIGH": "high",
        "Low": "low",
        "LOW": "low",
        "Close": "close",
        "CLOSE": "close",
        "Volume": "volume",
        "VOLUME": "volume",
        "Date": "date",
        "DATE": "date",
        "Datetime": "datetime",
        "Datetime": "datetime",
        "Timestamp": "timestamp",
        "TIMESTAMP": "timestamp",
    }

    def normalize_columns(self, fieldnames):

        normalized = {}

        for field in fieldnames or []:

            clean = field.strip()

            if clean in self.COLUMN_ALIASES:
                normalized[clean] = self.COLUMN_ALIASES[clean]
            else:
                normalized[clean] = clean.lower()

        return normalized

    def _parse_number(self, value, field_name):

        if value is None:
            raise ValueError(
                f"Missing value for {field_name}"
            )

        value = str(value).strip()

        if value == "":
            raise ValueError(
                f"Empty value for {field_name}"
            )

        return float(value)

    def _parse_timestamp(self, row):

        timestamp = (
            row.get("timestamp")
            or row.get("datetime")
            or row.get("date")
        )

        if not timestamp:
            return None

        timestamp = timestamp.strip()

        # Preserve the original timestamp if it cannot
        # be parsed into a known format.
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%d-%m-%Y %H:%M:%S",
            "%d-%m-%Y %H:%M",
            "%Y-%m-%d",
            "%d-%m-%Y",
        ]

        for fmt in formats:

            try:
                return datetime.strptime(
                    timestamp,
                    fmt
                ).isoformat()
            except ValueError:
                continue

        return timestamp

    def convert_rows(self, rows):

        candles = []

        for index, row in enumerate(rows):

            open_price = self._parse_number(
                row.get("open"),
                "open"
            )

            high_price = self._parse_number(
                row.get("high"),
                "high"
            )

            low_price = self._parse_number(
                row.get("low"),
                "low"
            )

            close_price = self._parse_number(
                row.get("close"),
                "close"
            )

            if high_price < max(
                open_price,
                close_price
            ):
                raise ValueError(
                    f"Invalid candle {index}: "
                    f"high is below open/close"
                )

            if low_price > min(
                open_price,
                close_price
            ):
                raise ValueError(
                    f"Invalid candle {index}: "
                    f"low is above open/close"
                )

            candle = {
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price
            }

            volume = row.get("volume")

            if volume not in (None, ""):
                candle["volume"] = float(volume)

            timestamp = self._parse_timestamp(row)

            if timestamp:
                candle["timestamp"] = timestamp

            candles.append(candle)

        return candles

    def convert(
        self,
        input_file,
        output_file,
        symbol=None
    ):

        input_path = Path(input_file)
        output_path = Path(output_file)

        if not input_path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {input_path}"
            )

        with input_path.open(
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            if not reader.fieldnames:
                raise ValueError(
                    "CSV has no header"
                )

            normalized = self.normalize_columns(
                reader.fieldnames
            )

            rows = []

            for row in reader:

                normalized_row = {}

                for original, value in row.items():

                    if original is None:
                        continue

                    key = normalized.get(
                        original.strip(),
                        original.strip().lower()
                    )

                    normalized_row[key] = value

                rows.append(normalized_row)

        if not rows:
            raise ValueError(
                "CSV contains no data rows"
            )

        missing = (
            self.REQUIRED_COLUMNS
            - set(rows[0].keys())
        )

        if missing:
            raise ValueError(
                "Missing required columns: "
                + ", ".join(sorted(missing))
            )

        candles = self.convert_rows(rows)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        payload = {
            "symbol": symbol,
            "source": str(input_path),
            "candle_count": len(candles),
            "candles": candles
        }

        with output_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                payload,
                file,
                indent=2
            )

        return payload