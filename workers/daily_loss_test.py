from execution.paper_broker import PaperBroker
from risk.guardian import RiskGuardian
from workers.execution.execution_worker import ExecutionWorker


def main():

    print("=" * 60)
    print("DAILY LOSS INTEGRATION TEST")
    print("=" * 60)

    broker = PaperBroker()

    risk = RiskGuardian(
        max_daily_loss=10,
        max_position_size=1
    )

    execution = ExecutionWorker(
        broker=broker,
        risk_guardian=risk
    )

    print()
    print("TRADE 1 - BUY")
    print("-" * 60)

    result = execution.execute(
        decision={"action": "BUY"},
        symbol="NIFTY",
        quantity=1,
        price=100
    )

    print("Execution:", result)
    print("Realized P&L:", broker.get_realized_pnl())

    print()
    print("TRADE 2 - SELL AT LOSS")
    print("-" * 60)

    result = execution.execute(
        decision={"action": "SELL"},
        symbol="NIFTY",
        quantity=1,
        price=89
    )

    print("Execution:", result)
    print("Realized P&L:", broker.get_realized_pnl())

    daily_loss = max(
        0.0,
        -broker.get_realized_pnl()
    )

    print("Daily loss:", daily_loss)

    print()
    print("TRADE 3 - NEW BUY AFTER LOSS")
    print("-" * 60)

    result = execution.execute(
        decision={"action": "BUY"},
        symbol="NIFTY",
        quantity=1,
        price=90,
        daily_loss=daily_loss
    )

    print("Execution:", result)
    print("Realized P&L:", broker.get_realized_pnl())

    print()
    print("=" * 60)
    print("DAILY LOSS INTEGRATION TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()