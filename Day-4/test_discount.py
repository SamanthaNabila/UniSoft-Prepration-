import unittest
from decimal import Decimal

from discount import apply_discount


class ApplyDiscountTests(unittest.TestCase):
    def test_applies_discount_to_multiple_items(self) -> None:
        items = [
            {"name": "Notebook", "unit_price": Decimal("12.50"), "quantity": 2},
            {"name": "Pen", "unit_price": Decimal("1.25"), "quantity": 3},
        ]

        self.assertEqual(apply_discount(items, Decimal("10")), Decimal("25.88"))

    def test_rounds_to_two_places_using_half_up(self) -> None:
        items = [{"name": "Service", "unit_price": Decimal("10.005"), "quantity": 1}]

        result = apply_discount(items, Decimal("0"))

        self.assertEqual(result, Decimal("10.01"))
        self.assertEqual(result.as_tuple().exponent, -2)

    def test_accepts_boundary_discounts(self) -> None:
        items = [{"name": "Item", "unit_price": Decimal("25.00"), "quantity": 2}]

        self.assertEqual(apply_discount(items, Decimal("0")), Decimal("50.00"))
        self.assertEqual(apply_discount(items, Decimal("100")), Decimal("0.00"))

    def test_rejects_discount_below_zero(self) -> None:
        with self.assertRaises(ValueError):
            apply_discount([], Decimal("-0.01"))

    def test_rejects_discount_above_one_hundred(self) -> None:
        with self.assertRaises(ValueError):
            apply_discount([], Decimal("100.01"))




if __name__ == "__main__":
    unittest.main()
