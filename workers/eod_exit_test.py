from execution.paper_broker import PaperBroker


def main():

    print("=" * 60)
    print("EOD POSITION EXIT TEST")
    print("=" * 60)

    broker = PaperBroker()

    print()
    print("OPEN POSITION")
    print("-" * 60)

    broker.place_order(
        symbol="NIFTY",
        side="BUY",
        quantity=1,
        price=100
    )

    print("Position:", broker.get_position("NIFTY"))
    print("Realized P&L:", broker.get_realized_pnl())

    print()
    print("EOD CLOSE")
    print("-" * 60)

    broker.close_all_positions(
        current_prices={
            "NIFTY": 110
        }
    )

    print("Position after EOD:", broker.get_position("NIFTY"))
    print("Realized P&L:", broker.get_realized_pnl())

    print()
    print("=" * 60)
    print("EOD POSITION EXIT TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()