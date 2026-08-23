from workers.broker.broker_factory import create_broker
from workers.broker.models import (
    OrderRequest,
    OrderSide,
    OrderStatus,
)
from workers.broker.real_broker import RealBroker
from workers.execution.execution_worker import ExecutionWorker


def main():

    print("=" * 60)
    print("PHASE 11 BROKER INTEGRATION TEST")
    print("=" * 60)

    print("\n1. PAPER BROKER")
    print("-" * 60)

    broker = create_broker(paper=True)

    assert broker.is_connected() is True

    execution = ExecutionWorker(broker)

    print("Paper broker connected: PASS")

    print("\n2. BUY ORDER")
    print("-" * 60)

    buy = execution.execute(
        OrderRequest(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=1,
            price=100.0,
            tag="PHASE11_TEST",
        )
    )

    assert buy.status == OrderStatus.FILLED
    assert buy.price == 100.0

    print("BUY order: PASS")

    print("\n3. POSITION")
    print("-" * 60)

    positions = execution.positions()

    assert "NIFTY" in positions
    assert positions["NIFTY"]["quantity"] == 1

    print("Position created: PASS")
    print(positions)

    print("\n4. SELL ORDER")
    print("-" * 60)

    sell = execution.execute(
        OrderRequest(
            symbol="NIFTY",
            side=OrderSide.SELL,
            quantity=1,
            price=110.0,
            tag="PHASE11_TEST",
        )
    )

    assert sell.status == OrderStatus.FILLED
    assert sell.realized_pnl == 10.0

    print("SELL order: PASS")
    print("Realized P&L:", sell.realized_pnl)

    print("\n5. POSITION CLOSED")
    print("-" * 60)

    positions = execution.positions()

    assert "NIFTY" not in positions

    print("Position closed: PASS")

    print("\n6. EOD EXIT")
    print("-" * 60)

    execution.execute(
        OrderRequest(
            symbol="NIFTY",
            side=OrderSide.BUY,
            quantity=1,
            price=120.0,
            tag="EOD_TEST",
        )
    )

    assert "NIFTY" in execution.positions()

    eod_results = execution.close_all(
        {
            "NIFTY": 125.0,
        }
    )

    assert len(eod_results) == 1
    assert eod_results[0].status == OrderStatus.FILLED
    assert eod_results[0].realized_pnl == 5.0

    assert execution.positions() == {}

    print("EOD close: PASS")
    print("EOD P&L:", eod_results[0].realized_pnl)

    print("\n7. INVALID ORDER PROTECTION")
    print("-" * 60)

    invalid = execution.execute(
        OrderRequest(
            symbol="NIFTY",
            side=OrderSide.SELL,
            quantity=1,
            price=100.0,
        )
    )

    assert invalid.status == OrderStatus.REJECTED

    print("Invalid sell protection: PASS")

    print("\n8. REAL BROKER SAFETY")
    print("-" * 60)

    real_broker = RealBroker()

    assert real_broker.is_connected() is False

    try:
        real_broker.place_order(
            OrderRequest(
                symbol="NIFTY",
                side=OrderSide.BUY,
                quantity=1,
                price=100.0,
            )
        )

        raise AssertionError(
            "Real broker unexpectedly accepted an order"
        )

    except RuntimeError as exc:

        assert "disabled" in str(exc).lower()

        print("Real broker execution disabled: PASS")

    print("\n9. FINAL VALIDATION")
    print("-" * 60)

    print("Broker abstraction: PASS")
    print("Paper execution: PASS")
    print("Execution worker: PASS")
    print("Order validation: PASS")
    print("Position tracking: PASS")
    print("P&L calculation: PASS")
    print("EOD close: PASS")
    print("Real broker safety: PASS")

    print("\n" + "=" * 60)
    print("PHASE 11 INTEGRATION TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
