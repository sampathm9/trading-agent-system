from typing import Dict


class ReleaseReadiness:

    def evaluate(self, result: Dict) -> Dict:

        score = float(result.get("score", 0.0))
        ready = bool(result.get("ready", False))

        return {
            "ready": ready,
            "score": score,
            "classification": (
                "FINAL_RELEASE_CERTIFIED"
                if ready and score >= 1.0
                else "RELEASE_NOT_CERTIFIED"
            ),
        }
