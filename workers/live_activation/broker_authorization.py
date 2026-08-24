from typing import Dict


class BrokerAuthorizationChecker:

    def check(
        self,
        broker,
        require_real_broker: bool = False,
    ) -> Dict:

        broker_type = type(
            broker
        ).__name__

        is_paper = (
            "paper" in broker_type.lower()
        )

        if require_real_broker:

            return {
                "authorized": not is_paper,
                "broker_type": broker_type,
                "paper_broker": is_paper,
                "reason": (
                    "Real broker required"
                    if is_paper
                    else "Broker accepted"
                ),
            }

        return {
            "authorized": True,
            "broker_type": broker_type,
            "paper_broker": is_paper,
            "reason": (
                "Paper broker accepted"
                if is_paper
                else "Broker accepted"
            ),
        }
