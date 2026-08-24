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

    if any(item["quantity"] < 0 for item in items):
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
