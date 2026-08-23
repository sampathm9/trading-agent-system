from execution.paper_broker import PaperBroker


def main():

    print("=" * 60)
    print("POSITION AND P&L TEST")
    print("=" * 60)

    broker = PaperBroker()

    # BUY at 144
    broker.place_order(
        symbol="NIFTY",
        side="BUY",
        quantity=1,
        price=144
    )

    print()
    print("CURRENT POSITION")
    print(broker.get_position("NIFTY"))

    # Price moves to 150
    current_price = 150

    pnl = broker.calculate_unrealized_pnl(
        symbol="NIFTY",
        current_price=current_price
    )

    print()
    print(f"Current price: {current_price}")
    print(f"Unrealized P&L: {pnl}")

    # SELL at 150
    broker.place_order(
        symbol="NIFTY",
        side="SELL",
        quantity=1,
        price=150
    )

    print()
    print("POSITION AFTER SELL")
    print(broker.get_position("NIFTY"))

    print()
    print("=" * 60)
    print("POSITION AND P&L TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()