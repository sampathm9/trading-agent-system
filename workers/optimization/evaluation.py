from typing import Dict, List


class Phase16Evaluator:

    # ---------------------------------------------------------
    # SCORE
    # ---------------------------------------------------------

    def score(
        self,
        metrics: Dict,
    ) -> float:

        pnl = float(
            metrics.get(
                "realized_pnl",
                0.0,
            )
        )

        win_rate = float(
            metrics.get(
                "win_rate",
                0.0,
            )
        )

        drawdown = float(
            metrics.get(
                "max_drawdown",
                0.0,
            )
        )

        trades = int(
            metrics.get(
                "total_trades",
                0,
            )
        )

        # -----------------------------------------------------
        # Phase 16 ranking score
        #
        # Reward:
        #   positive P&L
        #   high win rate
        #   sufficient trading activity
        #
        # Penalize:
        #   drawdown
        # -----------------------------------------------------

        score = (
            pnl
            + (win_rate * 100.0)
            + min(trades, 10) * 2.0
            - abs(drawdown)
        )

        return round(
            score,
            6,
        )

    # ---------------------------------------------------------
    # EVALUATE
    # ---------------------------------------------------------

    def evaluate(
        self,
        configuration: Dict,
        result: Dict,
    ) -> Dict:

        metrics = result.get(
            "metrics",
            {},
        )

        ranking_score = self.score(
            metrics
        )

        return {
            "configuration": configuration,
            "metrics": metrics,
            "ranking_score": ranking_score,
            "trades": result.get(
                "trades",
                [],
            ),
        }

    # ---------------------------------------------------------
    # RANK
    # ---------------------------------------------------------

    def rank(
        self,
        evaluations: List[Dict],
    ) -> List[Dict]:

        return sorted(
            evaluations,
            key=lambda item: float(
                item["ranking_score"]
            ),
            reverse=True,
        )
