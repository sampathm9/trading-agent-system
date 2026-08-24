import json
from pathlib import Path


def load_phase23_report():

    path = Path(
        "reports/phase23/"
        "phase23_shadow_observation_report.json"
    )

    if not path.exists():
        return None

    try:
        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        return None


def load_phase24_report():

    path = Path(
        "reports/phase24/"
        "phase24_live_activation_readiness_report.json"
    )

    if not path.exists():
        return None

    try:
        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    except Exception:
        return None
