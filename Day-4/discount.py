from decimal import Decimal, ROUND_HALF_UP
from typing import TypedDict


class Item(TypedDict):
    name: str
    unit_price: Decimal
    quantity: int


def apply_discount(items: list[Item], discount_percent: Decimal) -> Decimal:
    """Return the discounted invoice total rounded to two decimal places."""
    if discount_percent < Decimal("0") or discount_percent > Decimal("100"):
        raise ValueError("discount_percent must be between 0 and 100")

    subtotal = sum(
        (item["unit_price"] * item["quantity"] for item in items),
        Decimal("0"),
    )
    discounted_total = subtotal * (Decimal("1") - discount_percent / Decimal("100"))
    return discounted_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
