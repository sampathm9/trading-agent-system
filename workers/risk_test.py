from risk.guardian import RiskGuardian


def main():

    print("=" * 60)
    print("RISK GUARDIAN TEST")
    print("=" * 60)

    risk = RiskGuardian(
        max_daily_loss=1000,
        max_position_size=1
    )

    print()
    print("TEST 1 - Normal trade")
    print("-" * 60)

    result = risk.approve(
        quantity=1,
        current_daily_loss=0
    )

    print("Approved:", result)

    print()
    print("TEST 2 - Maximum allowed position")
    print("-" * 60)

    result = risk.approve(
        quantity=1,
        current_daily_loss=500
    )

    print("Approved:", result)

    print()
    print("TEST 3 - Position too large")
    print("-" * 60)

    result = risk.approve(
        quantity=2,
        current_daily_loss=0
    )

    print("Approved:", result)

    print()
    print("TEST 4 - Daily loss limit reached")
    print("-" * 60)

    result = risk.approve(
        quantity=1,
        current_daily_loss=1000
    )

    print("Approved:", result)

    print()
    print("TEST 5 - Daily loss exceeded")
    print("-" * 60)

    result = risk.approve(
        quantity=1,
        current_daily_loss=1200
    )

    print("Approved:", result)

    print()
    print("=" * 60)
    print("RISK GUARDIAN TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()