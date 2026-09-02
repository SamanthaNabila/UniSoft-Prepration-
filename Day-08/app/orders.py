from decimal import Decimal, ROUND_HALF_UP
from typing import TypedDict


class OrderItem(TypedDict):
    name: str
    price: Decimal
    quantity: int


def order_summary(items: list[OrderItem]) -> Decimal:
    """Return the invoice total for an order, rounding each line half-up.

    Lines with a quantity of 0 contribute nothing, and an empty order totals 0.00.
    Raises ValueError if any quantity is negative.
    """
    if not items:
        return Decimal("0.00")

    for item in items:
        if not isinstance(item["price"], Decimal):
            raise TypeError("item price must be a Decimal")
        if item["price"] < Decimal("0"):
            raise ValueError("item price cannot be negative")
        if not isinstance(item["quantity"], int) or isinstance(item["quantity"], bool):
            raise TypeError("item quantity must be an integer")
        if item["quantity"] < 0:
            raise ValueError("item quantity cannot be negative")

    total = sum(
        (
            (item["price"] * item["quantity"]).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            for item in items
        ),
        Decimal("0"),
    )
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
