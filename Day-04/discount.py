from decimal import Decimal, ROUND_HALF_UP
from typing import TypedDict


class Item(TypedDict):
    name: str
    unit_price: Decimal
    quantity: int


def apply_discount(items: list[Item], discount_percent: Decimal) -> Decimal:
    """Return the discounted invoice total using per-item half-up rounding."""
    if discount_percent < Decimal("0") or discount_percent > Decimal("100"):
        raise ValueError("discount_percent must be between 0 and 100")

    if not items:
        raise ValueError("items cannot be empty")

    for item in items:
        if not isinstance(item["unit_price"], Decimal):
            raise TypeError("item unit_price must be a Decimal")
        if item["unit_price"] < Decimal("0"):
            raise ValueError("item unit_price cannot be negative")
        if not isinstance(item["quantity"], int) or isinstance(item["quantity"], bool):
            raise TypeError("item quantity must be an integer")
        if item["quantity"] < 0:
            raise ValueError("item quantity cannot be negative")

    discount_multiplier = Decimal("1") - discount_percent / Decimal("100")
    discounted_total = sum(
        (
            (item["unit_price"] * item["quantity"] * discount_multiplier).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            for item in items
        ),
        Decimal("0"),
    )
    return discounted_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def order_summary(items: list[Item]) -> Decimal:
    """Return the invoice total for an order, rounding each line half-up.

    Lines with a quantity of 0 contribute nothing, and an empty order totals 0.00.
    """
    if not items:
        return Decimal("0.00")

    return apply_discount(items, Decimal("0"))
