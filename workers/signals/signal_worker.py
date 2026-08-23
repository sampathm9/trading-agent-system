from datetime import datetime


class SignalWorker:

    def __init__(
        self,
        minimum_confidence=0.60
    ):

        self.minimum_confidence = float(
            minimum_confidence
        )

        self.last_signal = None
        self.signal_history = []

    def generate(
        self,
        trend_result
    ):

        if not trend_result:

            return self._create_signal(
                action="HOLD",
                confidence=0.0,
                reason="NO_TREND_DATA",
                trend="NEUTRAL",
            )

        trend = trend_result.get(
            "trend",
            "NEUTRAL"
        )

        confidence = float(
            trend_result.get(
                "confidence",
                0.0
            )
        )

        if trend == "BULLISH":

            if confidence >= self.minimum_confidence:

                action = "BUY"
                reason = "BULLISH_TREND"

            else:

                action = "HOLD"
                reason = "LOW_CONFIDENCE"

        elif trend == "BEARISH":

            if confidence >= self.minimum_confidence:

                action = "SELL"
                reason = "BEARISH_TREND"

            else:

                action = "HOLD"
                reason = "LOW_CONFIDENCE"

        else:

            action = "HOLD"
            reason = "NEUTRAL_TREND"

        signal = self._create_signal(
            action=action,
            confidence=confidence,
            reason=reason,
            trend=trend,
        )

        return signal

    def _create_signal(
        self,
        action,
        confidence,
        reason,
        trend,
    ):

        signal = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "trend": trend,
            "confidence": round(
                confidence,
                4
            ),
            "reason": reason,
        }

        self.last_signal = signal

        self.signal_history.append(
            signal
        )

        return signal

    def get_last_signal(self):

        return self.last_signal

    def get_signal_history(self):

        return list(
            self.signal_history
        )

    def clear_history(self):

        self.signal_history.clear()
        self.last_signal = None