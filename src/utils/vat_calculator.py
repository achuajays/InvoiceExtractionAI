import re
from decimal import Decimal, InvalidOperation
from typing import Union


class VATCalculator:
    """Utility class for calculating VAT amounts."""

    VAT_RATE = 0.15  # 15% VAT rate

    @staticmethod
    def clean_numeric_value(value: str) -> Union[Decimal, None]:
        """
        Clean and convert a string value to Decimal for calculation.
        Removes currency symbols, commas, and other non-numeric characters.

        Args:
            value: String value to clean and convert

        Returns:
            Decimal value or None if conversion fails
        """
        if not value or value.strip() == "":
            return None

        try:
            # Remove currency symbols, commas, and spaces
            cleaned = re.sub(r"[^\d.-]", "", str(value).strip())

            # Handle empty string after cleaning
            if not cleaned:
                return None

            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return None

    @classmethod
    def calculate_vat_amount(cls, quantity: str, unit_price: str) -> str:
        """
        Calculate VAT amount using the formula: quantity × unit_price × 15%

        Args:
            quantity: Quantity as string
            unit_price: Unit price as string

        Returns:
            Calculated VAT amount as string, or empty string if calculation fails
        """
        try:
            # Clean and convert values
            qty_decimal = cls.clean_numeric_value(quantity)
            price_decimal = cls.clean_numeric_value(unit_price)

            # Check if both values are valid
            if qty_decimal is None or price_decimal is None:
                return ""

            # Calculate VAT: quantity × unit_price × 15%
            vat_amount = qty_decimal * price_decimal * Decimal(cls.VAT_RATE)

            # Round to 2 decimal places and return as string
            return str(round(vat_amount, 2))

        except Exception:
            return ""

    @classmethod
    def calculate_line_total(cls, quantity: str, unit_price: str) -> str:
        """
        Calculate line total including VAT: (quantity × unit_price) + VAT

        Args:
            quantity: Quantity as string
            unit_price: Unit price as string

        Returns:
            Total amount including VAT as string, or empty string if calculation fails
        """
        try:
            # Clean and convert values
            qty_decimal = cls.clean_numeric_value(quantity)
            price_decimal = cls.clean_numeric_value(unit_price)

            if qty_decimal is None or price_decimal is None:
                return ""

            # Calculate subtotal
            subtotal = qty_decimal * price_decimal

            # Calculate VAT
            vat_amount = subtotal * Decimal(cls.VAT_RATE)

            # Calculate total
            total = subtotal + vat_amount

            return str(round(total, 2))

        except Exception:
            return ""
