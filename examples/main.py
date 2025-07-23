import os
import json
from invoice_pipeline import InvoicePipeline

def main():
    pdf_path = "ali.pdf"  # path to your invoice PDF
    
    try:
        pipeline = InvoicePipeline()
        invoice_data = pipeline.process(pdf_path, preprocess=True)

        print("\n" + "="*60)
        print("📋 INVOICE EXTRACTION RESULTS")
        print("="*60)
        
        print(f"\nParty Name: {invoice_data.party_name}")
        print(f"Party Name (Translated): {invoice_data.party_name_translated}")
        print(f"Date: {invoice_data.date}")
        print(f"Invoice No: {invoice_data.invoice_no}")
        print(f"Seller VAT No: {invoice_data.seller_vat_no}")
        print(f"Client VAT No: {invoice_data.client_vat_no}")
        print(f"Total Amount: {invoice_data.amount}")
        print(f"Vendor Address: {invoice_data.vendor_addr}")
        print(f"Vendor Address (Translated): {invoice_data.vendor_addr_translated}")
        print(f"Detected Language: {invoice_data.detected_language}")
        
        if invoice_data.items:
            print(f"\nItems ({len(invoice_data.items)}):")
            print(f"  {'No.':<5} {'Name':<30} {'Translated':<30} {'Qty':<8} {'Cost':<15}")
            print(f"  {'-'*5} {'-'*30} {'-'*30} {'-'*8} {'-'*15}")
            for i, item in enumerate(invoice_data.items, 1):
                print(f"  {i:<5} {item.name[:30]:<30} {item.name_translated[:30]:<30} {item.quantity:<8} {item.cost:<15}")
        
        print("\n" + "="*60)
        print("JSON OUTPUT:")
        print("="*60)
        # Convert to JSON and print
        json_output = {
            "party_name": invoice_data.party_name,
            "party_name_translated": invoice_data.party_name_translated,
            "date": invoice_data.date,
            "invoice_no": invoice_data.invoice_no,
            "seller_vat_no": invoice_data.seller_vat_no,
            "client_vat_no": invoice_data.client_vat_no,
            "amount": invoice_data.amount,
            "vendor_addr": invoice_data.vendor_addr,
            "vendor_addr_translated": invoice_data.vendor_addr_translated,
            "detected_language": invoice_data.detected_language,
            "items": [
                {
                    "name": item.name,
                    "name_translated": item.name_translated,
                    "quantity": item.quantity,
                    "cost": item.cost
                } for item in invoice_data.items
            ]
        }
        print(json.dumps(json_output, indent=2, ensure_ascii=False))
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
