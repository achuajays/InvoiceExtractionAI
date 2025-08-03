from pydantic import BaseModel
from typing import List, Optional

# Temporary model for AI extraction (without vat_amount)
class InvoiceLineExtracted(BaseModel):
    product: str
    quantity: str
    unit_price: str
    taxes: str

# Final model with calculated vat_amount
class InvoiceLine(BaseModel):
    product: str
    quantity: str
    unit_price: str
    taxes: str
    vat_amount: str  # VAT amount (calculated using quantity × unit_price × 15%)

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
