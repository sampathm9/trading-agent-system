from typing import Dict, Iterable, List, Optional

from workers.trading.session_manager import (
    SessionManager,
    TradingSession,
)

from workers.trading.safety_gateway import (
    SafetyGateway,
)

from workers.integration import (
    IntelligentTradingWorker,
)


class TradingController:

    def __init__(
        self,
        intelligent_worker: IntelligentTradingWorker,
        session_manager: Optional[SessionManager] = None,
        safety_gateway: Optional[SafetyGateway] = None,
    ):

        self.intelligence = intelligent_worker

        self.session = (
            session_manager
            or SessionManager()
        )

        self.safety = (
            safety_gateway
            or SafetyGateway()
        )

        self.cycle_count = 0
        self.history: List[Dict] = []

    # ---------------------------------------------------------
    # SESSION
    # ---------------------------------------------------------

    def set_session(self, session):

        self.session.set_session(session)

        if (
            self.session.get_session()
            == TradingSession.MARKET_OPEN
        ):
            self.safety.reset()

    def current_session(self):

        return self.session.get_session().value

    # ---------------------------------------------------------
    # MARKET CYCLE
    # ---------------------------------------------------------

    def process_market(
        self,
        candles: List[Dict],
        symbol: str,
        quantity: int,
        price: float,
        news: Optional[Iterable[Dict | str]] = None,
    ) -> Dict:

        self.cycle_count += 1

        session = self.session.get_session()

        # -----------------------------------------------------
        # SESSION SAFETY
        # -----------------------------------------------------

        if not self.session.can_trade():

            result = {
                "cycle": self.cycle_count,
                "session": session.value,
                "status": "BLOCKED",
                "reason": (
                    "Trading session does not permit orders"
                ),
                "execution": None,
            }

            self.history.append(result)

            return result

        # -----------------------------------------------------
        # PHASE 13 INTELLIGENCE
        # -----------------------------------------------------
        #
        # IMPORTANT:
        # Do NOT call intelligence.run_cycle().
        #
        # run_cycle() performs execution itself.
        #
        # Phase 14 must control execution so that exactly
        # one order can be generated.
        # -----------------------------------------------------

        intelligence = (
            self.intelligence.analyze_market(
                candles,
                news,
            )
        )

        strategy = (
            self.intelligence.create_strategy_signal(
                intelligence
            )
        )

        risk = (
            self.intelligence.validate_risk(
                strategy,
                quantity,
            )
        )

        # -----------------------------------------------------
        # SAFETY GATEWAY
        # -----------------------------------------------------

        safety = self.safety.validate(
            action=strategy["action"],
            quantity=quantity,
            can_trade=True,
        )

        if not safety["approved"]:

            result = {
                "cycle": self.cycle_count,
                "session": session.value,
                "status": "BLOCKED",
                "reason": safety["reason"],
                "intelligence": intelligence,
                "strategy": strategy,
                "risk": risk,
                "safety": safety,
                "execution": None,
            }

            self.history.append(result)

            return result

        # -----------------------------------------------------
        # RISK
        # -----------------------------------------------------

        if not risk["approved"]:

            result = {
                "cycle": self.cycle_count,
                "session": session.value,
                "status": "RISK_REJECTED",
                "reason": risk["reason"],
                "intelligence": intelligence,
                "strategy": strategy,
                "risk": risk,
                "safety": safety,
                "execution": None,
            }

            self.history.append(result)

            return result

        # -----------------------------------------------------
        # SINGLE EXECUTION
        # -----------------------------------------------------

        execution = (
            self.intelligence.execute_signal(
                symbol=symbol,
                quantity=quantity,
                price=price,
                strategy_result=strategy,
            )
        )

        if execution is not None:
            self.safety.record_trade()

        result = {
            "cycle": self.cycle_count,
            "session": session.value,
            "status": "EXECUTED",
            "intelligence": intelligence,
            "strategy": strategy,
            "risk": risk,
            "safety": safety,
            "execution": execution,
        }

        self.history.append(result)

        return result

    # ---------------------------------------------------------
    # EOD
    # ---------------------------------------------------------

    def end_of_day(
        self,
        prices: Dict[str, float],
    ):

        self.set_session(
            TradingSession.EOD
        )

        return self.intelligence.close_all(
            prices
        )

    # ---------------------------------------------------------
    # CLOSE SESSION
    # ---------------------------------------------------------

    def close_session(self):

        self.set_session(
            TradingSession.CLOSED
        )

    # ---------------------------------------------------------
    # POSITIONS
    # ---------------------------------------------------------

    def positions(self):

        return self.intelligence.positions()

    # ---------------------------------------------------------
    # HISTORY
    # ---------------------------------------------------------

    def history_report(self):

        return self.history
