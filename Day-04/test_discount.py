import unittest
from decimal import Decimal

from discount import apply_discount, order_summary


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

    def test_rejects_negative_quantity(self) -> None:
        items = [{"name": "Item", "unit_price": Decimal("10.00"), "quantity": -1}]

        with self.assertRaises(ValueError):
            apply_discount(items, Decimal("10"))

    def test_rejects_negative_unit_price(self) -> None:
        items = [{"name": "Item", "unit_price": Decimal("-10.00"), "quantity": 1}]

        with self.assertRaises(ValueError):
            apply_discount(items, Decimal("10"))

    def test_rejects_empty_items(self) -> None:
        with self.assertRaises(ValueError):
            apply_discount([], Decimal("10"))

    def test_rounds_each_item_before_total(self) -> None:
        items = [
            {"name": "Item A", "unit_price": Decimal("0.005"), "quantity": 1},
            {"name": "Item B", "unit_price": Decimal("0.005"), "quantity": 1},
        ]

        self.assertEqual(apply_discount(items, Decimal("0")), Decimal("0.02"))



class OrderSummaryTests(unittest.TestCase):
    def test_totals_a_single_item(self) -> None:
        items = [{"name": "Notebook", "unit_price": Decimal("12.50"), "quantity": 2}]

        self.assertEqual(order_summary(items), Decimal("25.00"))

    def test_totals_multiple_items(self) -> None:
        items = [
            {"name": "Notebook", "unit_price": Decimal("12.50"), "quantity": 2},
            {"name": "Pen", "unit_price": Decimal("1.25"), "quantity": 3},
        ]

        self.assertEqual(order_summary(items), Decimal("28.75"))

    def test_ignores_items_with_zero_quantity(self) -> None:
        items = [
            {"name": "Notebook", "unit_price": Decimal("12.50"), "quantity": 2},
            {"name": "Pen", "unit_price": Decimal("1.25"), "quantity": 0},
        ]

        self.assertEqual(order_summary(items), Decimal("25.00"))

    def test_rejects_negative_quantity(self) -> None:
        items = [{"name": "Notebook", "unit_price": Decimal("12.50"), "quantity": -1}]

        with self.assertRaises(ValueError):
            order_summary(items)

    def test_totals_decimal_prices(self) -> None:
        items = [
            {"name": "Cable", "unit_price": Decimal("19.99"), "quantity": 3},
            {"name": "Adapter", "unit_price": Decimal("4.05"), "quantity": 2},
        ]

        result = order_summary(items)

        self.assertEqual(result, Decimal("68.07"))
        self.assertEqual(result.as_tuple().exponent, -2)

    def test_empty_order_totals_zero(self) -> None:
        result = order_summary([])

        self.assertEqual(result, Decimal("0.00"))
        self.assertEqual(result.as_tuple().exponent, -2)


if __name__ == "__main__":
    unittest.main()
