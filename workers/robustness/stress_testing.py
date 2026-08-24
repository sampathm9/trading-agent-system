from typing import Dict, Iterable, List, Optional

from config.phase18_config import (
    PNL_DEGRADATION_LEVELS,
    SLIPPAGE_LEVELS,
)


class Phase18StressTester:

    # --------------------------------------------------------
    # PNL EXTRACTION
    # --------------------------------------------------------

    def extract_pnls(
        self,
        trades: Optional[Iterable[Dict]],
    ) -> List[float]:

        pnls = []

        if not trades:
            return pnls

        for trade in trades:

            if not isinstance(trade, dict):
                continue

            value = None

            for key in (
                "realized_pnl",
                "pnl",
                "profit",
                "profit_loss",
            ):

                if key in trade:
                    value = trade[key]
                    break

            if value is None:
                continue

            try:
                pnls.append(float(value))
            except (
                TypeError,
                ValueError,
            ):
                continue

        return pnls

    # --------------------------------------------------------
    # SLIPPAGE
    # --------------------------------------------------------

    def apply_slippage(
        self,
        pnl: float,
        slippage: float,
    ) -> float:

        return pnl * (
            1.0 - float(slippage)
        )

    # --------------------------------------------------------
    # DEGRADATION
    # --------------------------------------------------------

    def apply_degradation(
        self,
        pnl: float,
        degradation: float,
    ) -> float:

        return pnl * (
            1.0 - float(degradation)
        )

    # --------------------------------------------------------
    # RUN
    # --------------------------------------------------------

    def run(
        self,
        trades: Optional[Iterable[Dict]],
    ) -> Dict:

        pnls = self.extract_pnls(
            trades
        )

        scenarios = []

        for slippage in SLIPPAGE_LEVELS:

            for degradation in PNL_DEGRADATION_LEVELS:

                stressed_pnl = 0.0

                for pnl in pnls:

                    value = self.apply_slippage(
                        pnl,
                        slippage,
                    )

                    value = self.apply_degradation(
                        value,
                        degradation,
                    )

                    stressed_pnl += value

                scenarios.append(
                    {
                        "slippage": float(
                            slippage
                        ),
                        "pnl_degradation": float(
                            degradation
                        ),
                        "stressed_pnl": round(
                            stressed_pnl,
                            6,
                        ),
                        "profitable": (
                            stressed_pnl > 0
                        ),
                    }
                )

        profitable = sum(
            1
            for scenario in scenarios
            if scenario["profitable"]
        )

        scenario_count = len(
            scenarios
        )

        positive_rate = (
            profitable / scenario_count
            if scenario_count
            else 0.0
        )

        return {
            "trade_count": len(pnls),
            "scenario_count": scenario_count,
            "profitable_scenarios": profitable,
            "positive_scenario_rate": round(
                positive_rate,
                6,
            ),
            "scenarios": scenarios,
        }
