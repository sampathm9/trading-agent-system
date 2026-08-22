from orchestrator.session_manager import TradingSessionManager
from workers.decision.exit_agent import ExitAgent
from execution.paper_execution import PaperExecution
from execution.position_manager import PositionManager
from risk.risk_engine import RiskEngine


class TradingOrchestrator:

    def __init__(self):

        self.session = TradingSessionManager()

        self.execution = PaperExecution()

        self.positions = PositionManager()

        self.exit_agent = ExitAgent()

        self.risk = RiskEngine()

        self.daily_pnl = 0

        self.running = False

    def start_pre_market(self):

        result = self.session.start_pre_market()

        print("\n=== PRE-MARKET ===")
        print(result["message"])

        return result

    def start_trading(self):

        result = self.session.start_trading()

        self.running = True

        print("\n=== TRADING SESSION ===")
        print(result["message"])

        return result

    def execute_trade(
        self,
        decision,
        symbol,
        quantity,
        price
    ):

        if not self.session.trading_enabled:

            return {
                "status": "REJECTED",
                "reason": "Trading session is not active"
            }

        risk_result = self.risk.validate(
            decision=decision,
            quantity=quantity,
            daily_pnl=self.daily_pnl
        )

        print(
            "Risk:",
            risk_result["reason"]
        )

        if not risk_result["approved"]:

            return {
                "status": "RISK_REJECTED",
                "reason": risk_result["reason"]
            }

        result = self.execution.execute(
            decision=decision,
            symbol=symbol,
            quantity=quantity,
            price=price
        )

        if result["status"] != "EXECUTED":
            return result

        position = result["position"]

        self.positions.add_position(
            symbol=symbol,
            side=position["side"],
            quantity=position["quantity"],
            entry_price=position["entry_price"]
        )

        print(
            f"TRADE: {position['side']} "
            f"{symbol} @ {position['entry_price']}"
        )

        return result

    def monitor_position(
        self,
        symbol,
        current_price
    ):

        position = self.positions.get_position(symbol)

        if position is None:

            return {
                "status": "NO_POSITION"
            }

        self.positions.update_price(
            symbol,
            current_price
        )

        exit_decision = self.exit_agent.evaluate(
            entry_price=position["entry_price"],
            current_price=current_price,
            side=position["side"]
        )

        if exit_decision["exit"]:

            return self.exit_position(
                symbol,
                current_price,
                exit_decision["reason"]
            )

        return {
            "status": "HOLD",
            "position": self.positions.get_position(symbol)
        }

    def exit_position(
        self,
        symbol,
        price,
        reason="Manual exit"
    ):

        result = self.execution.exit_position(
            symbol,
            price
        )

        if result["status"] != "CLOSED":
            return result

        position = self.positions.close_position(
            symbol,
            price
        )

        self.daily_pnl += position["realized_pnl"]

        print(
            f"EXIT: {symbol} @ {price} | "
            f"Reason: {reason} | "
            f"P&L: {position['realized_pnl']}"
        )

        return {
            "status": "CLOSED",
            "reason": reason,
            "position": position
        }

    def force_close_all(self):

        print("\n=== FORCE CLOSE ===")

        open_positions = self.positions.get_open_positions()

        results = []

        for position in open_positions:

            symbol = position["symbol"]
            current_price = position["current_price"]

            result = self.execution.exit_position(
                symbol,
                current_price
            )

            if result["status"] == "CLOSED":

                closed = self.positions.close_position(
                    symbol,
                    current_price
                )

                self.daily_pnl += closed["realized_pnl"]

                results.append(closed)

                print(
                    f"FORCED EXIT: {symbol} "
                    f"@ {current_price} | "
                    f"P&L: {closed['realized_pnl']}"
                )

        self.session.force_close()

        self.running = False

        return results

    def post_market(self):

        result = self.session.start_post_market()

        print("\n=== POST-MARKET ===")
        print(result["message"])

        print(
            "Realized P&L:",
            self.daily_pnl
        )

        return result

    def sleep(self):

        result = self.session.sleep()

        print("\n=== SLEEP ===")
        print(result["message"])

        return result