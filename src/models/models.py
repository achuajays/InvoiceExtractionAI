from typing import List, Optional

from pydantic import BaseModel


# Temporary model for AI extraction (without vat_amount)
class InvoiceLineExtracted(BaseModel):
    product: Optional[str] = ""
    quantity: Optional[str] = "1"
    unit_price: Optional[str] = "0"
    taxes: Optional[str] = "0"
    gross_price: Optional[str] = "0"


# Final model with calculated vat_amount
class InvoiceLine(BaseModel):
    product: Optional[str] = ""
    quantity: Optional[str] = "1"
    unit_price: Optional[str] = "0"
    taxes: Optional[str] = "0"
    gross_price: Optional[str] = "0"
    vat_amount: Optional[str] = "0"


class InvoiceData(BaseModel):
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
    invoice_lines: List[InvoiceLine]
    detected_language: str
    filename: Optional[str] = None


class MultipleInvoicesResponse(BaseModel):
    invoices: List[InvoiceData]
    total_processed: int
    successful_extractions: int
    failed_extractions: int
