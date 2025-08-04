import logging
from typing import Optional

from src.models.extraction_models import InvoiceDataExtracted, InvoiceLineExtracted
from src.models.models import InvoiceData, InvoiceLine
from src.utils.vat_calculator import VATCalculator


class InvoicePostProcessor:
    """Post-processes extracted invoice data to add VAT calculations."""

    @staticmethod
    def add_vat_calculations(extracted_data: InvoiceDataExtracted) -> InvoiceData:
        """
        Convert extracted invoice data to final format with calculated VAT amounts.

        Args:
            extracted_data: Invoice data from AI extraction (without vat_amount)

        Returns:
            InvoiceData with calculated VAT amounts for each line item
        """
        if not extracted_data:
            return None

        try:
            # Process each invoice line and add VAT calculation
            processed_lines = []

            for line in extracted_data.invoice_lines:
                # Calculate VAT amount using quantity × unit_price × 15%
                vat_amount = VATCalculator.calculate_vat_amount(
                    line.quantity, line.unit_price
                )

                # Create new InvoiceLine with calculated VAT
                processed_line = InvoiceLine(
                    product=line.product,
                    quantity=line.quantity,
                    unit_price=line.unit_price,
                    taxes=line.taxes,
                    vat_amount=vat_amount,
                )
                processed_lines.append(processed_line)

            # Create final InvoiceData with calculated VAT amounts
            final_data = InvoiceData(
                partner=extracted_data.partner,
                vat_number=extracted_data.vat_number,
                cr_number=extracted_data.cr_number,
                street=extracted_data.street,
                street2=extracted_data.street2,
                country=extracted_data.country,
                email=extracted_data.email,
                city=extracted_data.city,
                mobile=extracted_data.mobile,
                invoice_type=extracted_data.invoice_type,
                invoice_bill_date=extracted_data.invoice_bill_date,
                reference=extracted_data.reference,
                invoice_lines=processed_lines,
                detected_language=extracted_data.detected_language,
                filename=extracted_data.filename,
            )

            return final_data

        except Exception as e:
            logging.error(f"Post-processing failed: {e}")
            return None

    @staticmethod
    def calculate_total_vat(invoice_data: InvoiceData) -> str:
        """
        Calculate total VAT amount for all line items.

        Args:
            invoice_data: Processed invoice data with VAT amounts

        Returns:
            Total VAT amount as string
        """
        try:
            total_vat = 0.0

            for line in invoice_data.invoice_lines:
                if line.vat_amount and line.vat_amount.strip():
                    vat_value = VATCalculator.clean_numeric_value(line.vat_amount)
                    if vat_value:
                        total_vat += float(vat_value)

            return str(round(total_vat, 2))

        except Exception as e:
            logging.error(f"Total VAT calculation failed: {e}")
            return "0.00"

    @staticmethod
    def calculate_subtotal(invoice_data: InvoiceData) -> str:
        """
        Calculate subtotal (before VAT) for all line items.

        Args:
            invoice_data: Processed invoice data

        Returns:
            Subtotal amount as string
        """
        try:
            subtotal = 0.0

            for line in invoice_data.invoice_lines:
                qty = VATCalculator.clean_numeric_value(line.quantity)
                price = VATCalculator.clean_numeric_value(line.unit_price)

                if qty and price:
                    line_subtotal = float(qty) * float(price)
                    subtotal += line_subtotal

            return str(round(subtotal, 2))

        except Exception as e:
            logging.error(f"Subtotal calculation failed: {e}")
            return "0.00"

    @staticmethod
    def calculate_total_amount(invoice_data: InvoiceData) -> str:
        """
        Calculate total amount (subtotal + VAT) for all line items.

        Args:
            invoice_data: Processed invoice data

        Returns:
            Total amount as string
        """
        try:
            subtotal_str = InvoicePostProcessor.calculate_subtotal(invoice_data)
            total_vat_str = InvoicePostProcessor.calculate_total_vat(invoice_data)

            subtotal = float(subtotal_str) if subtotal_str else 0.0
            total_vat = float(total_vat_str) if total_vat_str else 0.0

            total_amount = subtotal + total_vat

            return str(round(total_amount, 2))

        except Exception as e:
            logging.error(f"Total amount calculation failed: {e}")
            return "0.00"
