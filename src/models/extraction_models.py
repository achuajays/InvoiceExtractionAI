from pydantic import BaseModel
from typing import List, Optional


class InvoiceLineExtracted(BaseModel):
    """Temporary model for AI extraction (without vat_amount)"""
    product: str
    quantity: str
    unit_price: str
    gross_price: str
    taxes: str


class InvoiceDataExtracted(BaseModel):
    """Temporary model for AI extraction (without vat_amount in invoice lines)"""
    partner: str
    vat_number: str
    cr_number: str
    street: str
    street2: str
    country: str
    email: str
    city: str
    mobile: str
    invoice_type: str
    invoice_bill_date: str
    reference: str
    invoice_lines: List[InvoiceLineExtracted]
    detected_language: str
    filename: Optional[str] = None
