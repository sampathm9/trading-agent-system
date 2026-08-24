from typing import Dict


class DeploymentReadinessEvaluator:

    def evaluate(
        self,
        checks: Dict,
    ) -> Dict:

        results = {
            key: bool(value)
            for key, value in checks.items()
        }

        passed = sum(
            1
            for value in results.values()
            if value
        )

        total = len(results)

        score = (
            passed / total
            if total
            else 0.0
        )

        ready = (
            total > 0
            and passed == total
        )

        classification = (
            "PAPER_DEPLOYMENT_READY"
            if ready
            else "NOT_READY"
        )

        return {
            "ready": ready,
            "score": round(score, 6),
            "classification": classification,
            "checks": results,
            "passed": passed,
            "total": total,
        }
