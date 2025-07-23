from pydantic import BaseModel
from typing import List

class Item(BaseModel):
    name: str
    name_translated: str
    quantity: str
    cost: str

class InvoiceData(BaseModel):
    party_name: str
    party_name_translated: str
    date: str
    invoice_no: str
    seller_vat_no: str
    client_vat_no: str
    amount: str
    vendor_addr: str
    vendor_addr_translated: str
    items: List[Item]
    detected_language: str
