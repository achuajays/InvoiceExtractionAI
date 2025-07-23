import os
import pandas as pd
import json
import logging
from models import InvoiceData
from datetime import datetime

class InvoiceStorage:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.columns = [
            'extraction_date', 'party_name', 'party_name_translated', 'date',
            'invoice_no', 'vat_no', 'amount', 'vendor_addr',
            'vendor_addr_translated', 'items', 'detected_language', 'items_count'
        ]

    def _create_empty_file(self):
        df = pd.DataFrame(columns=self.columns)
        df.to_excel(self.file_path, index=False, engine='openpyxl')

    def load(self) -> pd.DataFrame:
        if not os.path.exists(self.file_path):
            self._create_empty_file()
        df = pd.read_excel(self.file_path, engine='openpyxl')
        return df

    def save(self, invoice: InvoiceData) -> bool:
        df = self.load()
        if invoice.invoice_no in df['invoice_no'].values:
            return False

        items_json = json.dumps([i.dict() for i in invoice.items], ensure_ascii=False)
        new_row = {
            'extraction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'party_name': invoice.party_name,
            'party_name_translated': invoice.party_name_translated,
            'date': invoice.date,
            'invoice_no': invoice.invoice_no,
            'vat_no': invoice.vat_no,
            'amount': invoice.amount,
            'vendor_addr': invoice.vendor_addr,
            'vendor_addr_translated': invoice.vendor_addr_translated,
            'items': items_json,
            'detected_language': invoice.detected_language,
            'items_count': len(invoice.items)
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_excel(self.file_path, index=False, engine='openpyxl')
        return True
