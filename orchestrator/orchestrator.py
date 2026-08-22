from backtest.backtest_worker import BacktestWorker
from workers.strategy.strategy_selector import StrategySelector
from workers.intelligence.market_intelligence_worker import MarketIntelligenceWorker
from workers.decision.decision_engine import DecisionEngine
from risk.risk_engine import RiskEngine
from execution.paper_execution import PaperExecution


class TradingOrchestrator:

    def __init__(self):

        self.backtest = BacktestWorker()

        self.strategy_selector = StrategySelector()

        self.intelligence = MarketIntelligenceWorker()

        self.decision_engine = DecisionEngine()

        self.risk_engine = RiskEngine()

        self.execution = PaperExecution()

        self.selected_strategy = None

        self.running = False

    def start_trading(self):

        print("\n=== TRADING SESSION ===")

        self.running = True

        print("Trading session started")

    def stop_trading(self):

        self.running = False

        print("Trading session stopped")

    def prepare_strategy(self, historical_candles):

        print("\n=== BACKTEST ===")

        result = self.backtest.run_momentum_backtest(
            historical_candles
        )

        print("Backtest result:")
        print(result)

        selected = self.strategy_selector.select(
            [result]
        )

        if selected is None:

            print("No strategy passed validation")

            self.selected_strategy = None

            return None

        self.selected_strategy = selected

        print(
            "Selected strategy:",
            selected["name"]
        )

        return selected

    def analyze_market(
        self,
        candles,
        market_text=""
    ):

        print("\n=== MARKET INTELLIGENCE ===")

        analysis = self.intelligence.analyze(
            candles,
            market_text
        )

        print(
            "Market bias:",
            analysis["market_bias"]
        )

        print(
            "Evidence score:",
            analysis["evidence_score"]
        )

        return analysis

    def make_decision(
        self,
        analysis
    ):

        print("\n=== DECISION ===")

        decision = self.decision_engine.decide(
            analysis,
            self.selected_strategy
        )

        print(
            "Action:",
            decision["action"]
        )

        print(
            "Confidence:",
            decision["confidence"]
        )

        return decision

    def execute_trade(
        self,
        decision,
        symbol,
        quantity,
        price
    ):

        print("\n=== RISK CHECK ===")

        risk_result = self.risk_engine.validate(
            decision,
            quantity=quantity,
            daily_pnl=0
        )

        if not risk_result["approved"]:

            print(
                "Risk rejected:",
                risk_result["reason"]
            )

            return {
                "status": "RISK_REJECTED",
                "reason": risk_result["reason"]
            }

        print("Risk: Risk checks passed")

        print("\n=== PAPER EXECUTION ===")

        result = self.execution.execute(
            decision,
            symbol,
            quantity,
            price
        )

        return result

    def run_cycle(
        self,
        historical_candles,
        market_candles,
        symbol="NIFTY",
        quantity=1
    ):

        if not self.running:

            raise RuntimeError(
                "Trading session is not running"
            )

        self.prepare_strategy(
            historical_candles
        )

        if self.selected_strategy is None:

            return {
                "status": "NO_STRATEGY"
            }

        analysis = self.analyze_market(
            market_candles
        )

        decision = self.make_decision(
            analysis
        )

        current_price = float(
            market_candles[-1]["close"]
        )

        execution = self.execute_trade(
            decision,
            symbol,
            quantity,
            current_price
        )

        return {
            "analysis": analysis,
            "decision": decision,
            "execution": execution
        }