import csv
import json
from pathlib import Path
from datetime import datetime


class Phase7Report:

    def __init__(self, output_dir="reports/phase7"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    def build_summary(self, session_result, events):
        final_state = session_result.get(
            "final_state",
            {}
        )

        return {
            "status": session_result.get(
                "status",
                "UNKNOWN"
            ),
            "timestamp": datetime.now().isoformat(),
            "entry_status": (
                session_result
                .get("entry", {})
                .get("status", "UNKNOWN")
            ),
            "monitor_events": len(
                session_result.get(
                    "monitor",
                    []
                )
            ),
            "eod_status": (
                session_result
                .get("eod", {})
                .get("status", "NONE")
                if session_result.get("eod")
                else "NONE"
            ),
            "realized_pnl": final_state.get(
                "realized_pnl",
                0.0
            ),
            "daily_loss": final_state.get(
                "daily_loss",
                0.0
            ),
            "trade_count": final_state.get(
                "trade_count",
                0
            ),
            "event_count": len(events),
        }

    def write_json(self, data):
        path = (
            self.output_dir
            / "phase7_session_report.json"
        )

        with path.open(
            "w",
            encoding="utf-8"
        ) as handle:
            json.dump(
                data,
                handle,
                indent=2,
                default=str
            )

        return str(path)

    def write_events_csv(self, events):
        path = (
            self.output_dir
            / "phase7_events.csv"
        )

        fieldnames = [
            "timestamp",
            "event",
            "details",
        ]

        with path.open(
            "w",
            newline="",
            encoding="utf-8"
        ) as handle:

            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames
            )

            writer.writeheader()

            for event in events:
                details = {
                    key: value
                    for key, value in event.items()
                    if key not in {
                        "timestamp",
                        "event"
                    }
                }

                writer.writerow(
                    {
                        "timestamp": event.get(
                            "timestamp"
                        ),
                        "event": event.get(
                            "event"
                        ),
                        "details": json.dumps(
                            details,
                            default=str
                        ),
                    }
                )

        return str(path)

    def generate(
        self,
        session_result,
        events
    ):
        summary = self.build_summary(
            session_result,
            events
        )

        report = {
            "summary": summary,
            "session": session_result,
            "events": events,
        }

        json_path = self.write_json(
            report
        )

        csv_path = self.write_events_csv(
            events
        )

        return {
            "summary": summary,
            "json": json_path,
            "csv": csv_path,
        }
