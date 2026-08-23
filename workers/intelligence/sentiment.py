from typing import Iterable, Dict, List


class SentimentAnalyzer:

    POSITIVE_WORDS = {
        "bullish",
        "growth",
        "strong",
        "positive",
        "surge",
        "rally",
        "gain",
        "gains",
        "profit",
        "profits",
        "optimistic",
        "up",
        "higher",
        "beat",
        "beats",
        "record",
        "recovery",
    }

    NEGATIVE_WORDS = {
        "bearish",
        "weak",
        "negative",
        "fall",
        "falls",
        "drop",
        "drops",
        "loss",
        "losses",
        "risk",
        "crisis",
        "fear",
        "decline",
        "lower",
        "downgrade",
        "miss",
        "misses",
        "recession",
    }

    def analyze(
        self,
        news: Iterable[Dict | str] | None = None,
    ) -> Dict:

        items: List[str] = []

        if news:
            for item in news:

                if isinstance(item, str):
                    items.append(item)
                else:
                    items.append(
                        str(
                            item.get(
                                "title",
                                item.get("text", ""),
                            )
                        )
                    )

        if not items:
            return {
                "score": 0.0,
                "label": "NEUTRAL",
                "articles": 0,
                "positive_hits": 0,
                "negative_hits": 0,
            }

        positive_hits = 0
        negative_hits = 0

        for text in items:

            words = {
                word.strip(
                    ".,!?;:()[]{}\"'"
                ).lower()
                for word in text.split()
            }

            positive_hits += len(
                words & self.POSITIVE_WORDS
            )

            negative_hits += len(
                words & self.NEGATIVE_WORDS
            )

        total_hits = positive_hits + negative_hits

        if total_hits == 0:
            score = 0.0
        else:
            score = (
                positive_hits - negative_hits
            ) / total_hits

        if score > 0.20:
            label = "POSITIVE"
        elif score < -0.20:
            label = "NEGATIVE"
        else:
            label = "NEUTRAL"

        return {
            "score": score,
            "label": label,
            "articles": len(items),
            "positive_hits": positive_hits,
            "negative_hits": negative_hits,
        }
