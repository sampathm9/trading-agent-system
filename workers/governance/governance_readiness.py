from typing import Any, Dict


class GovernanceReadiness:

    def evaluate(
        self,
        checks: Dict[str, bool],
        minimum_score: float = 0.90,
    ) -> Dict[str, Any]:

        total = len(checks)

        passed = sum(
            1
            for value in checks.values()
            if bool(value)
        )

        score = (
            passed / total
            if total
            else 0.0
        )

        ready = (
            score >= float(minimum_score)
            and all(bool(v) for v in checks.values())
        )

        classification = (
            "GOVERNANCE_READY"
            if ready
            else "GOVERNANCE_NOT_READY"
        )

        return {
            "ready": ready,
            "score": score,
            "classification": classification,
            "passed_checks": passed,
            "total_checks": total,
            "checks": checks,
        }
