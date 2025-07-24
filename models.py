from pydantic import BaseModel
from typing import List, Optional

class InvoiceLine(BaseModel):
    product: str
    quantity: str
    unit_price: str
    taxes: str

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
