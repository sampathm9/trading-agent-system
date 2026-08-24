from typing import Any, Dict


class SessionAuthorizer:

    def __init__(self, allowed_sessions=None):

        self.allowed_sessions = set(
            allowed_sessions or [
                "PAPER",
                "SHADOW",
                "CANARY",
            ]
        )

    def authorize(
        self,
        session: str,
        live_trading_enabled: bool,
    ) -> Dict[str, Any]:

        session_name = str(session).upper()

        if session_name == "LIVE":

            return {
                "authorized": False,
                "session": session_name,
                "reason": (
                    "LIVE session is blocked by Phase 29 "
                    "governance safety policy."
                ),
            }

        if session_name not in self.allowed_sessions:

            return {
                "authorized": False,
                "session": session_name,
                "reason": "Session is not approved.",
            }

        if live_trading_enabled:

            return {
                "authorized": False,
                "session": session_name,
                "reason": (
                    "Live trading flag must remain disabled "
                    "during Phase 29 certification."
                ),
            }

        return {
            "authorized": True,
            "session": session_name,
            "reason": "Approved non-live session.",
        }
