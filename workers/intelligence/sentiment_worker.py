import re

class SentimentWorker:

    POSITIVE_WORDS = {'bullish','positive','strong','growth','upside','buy','support','surge','rally'}
    NEGATIVE_WORDS = {'bearish','negative','weak','downside','sell','resistance','fall','crash','decline'}

    def analyze(self, text):
        words = re.findall(r'[a-zA-Z]+', text.lower())

        positive = sum(1 for word in words if word in self.POSITIVE_WORDS)
        negative = sum(1 for word in words if word in self.NEGATIVE_WORDS)
        total = positive + negative

        if total == 0:
            score = 0.0
        else:
            score = (positive - negative) / total

        if score > 0.2:
            sentiment = 'POSITIVE'
        elif score < -0.2:
            sentiment = 'NEGATIVE'
        else:
            sentiment = 'NEUTRAL'

        return {
            'sentiment': sentiment,
            'score': score,
            'positive_count': positive,
            'negative_count': negative
        }
