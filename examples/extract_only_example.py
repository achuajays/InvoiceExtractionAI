#!/usr/bin/env python3
"""
Simple invoice extraction script that only extracts and prints data.
No storage functionality - just pure extraction and display.
"""

from invoice_pipeline import InvoicePipeline
import sys


def extract_and_print(pdf_path: str, preprocess: bool = True):
    """
    Extract invoice data from a PDF and print it to console.

    Args:
        pdf_path: Path to the PDF file
        preprocess: Whether to apply image preprocessing (default: True)
    """
    print(f"\n🔍 Processing: {pdf_path}")
    print("=" * 60)

    pipeline = InvoicePipeline()
    extracted_data = pipeline.process(pdf_path, preprocess=preprocess)

    total_pages = sum(1 for k in extracted_data.keys() if isinstance(k, int))
    successful = sum(
        1 for k, v in extracted_data.items() if isinstance(k, int) and v is not None
    )

    print(f"\n📊 Summary:")
    print(f"  - Total pages: {total_pages}")
    print(f"  - Successful extractions: {successful}")
    print(f"  - Failed extractions: {total_pages - successful}")

    for page_num, invoice_data in extracted_data.items():
        if isinstance(page_num, int):  # Skip error summary
            print(f"\n{'='*60}")
            print(f"📄 PAGE {page_num}")
            print(f"{'='*60}")

            if invoice_data:
                print(f"\n🏢 VENDOR INFORMATION:")
                print(f"  Party Name: {invoice_data.party_name}")
                print(f"  Translated: {invoice_data.party_name_translated}")
                print(f"  Address: {invoice_data.vendor_addr}")
                print(f"  Address (Translated): {invoice_data.vendor_addr_translated}")

                print(f"\n📋 INVOICE DETAILS:")
                print(f"  Invoice No: {invoice_data.invoice_no}")
                print(f"  Date: {invoice_data.date}")
                print(f"  Seller VAT No: {invoice_data.seller_vat_no}")
                print(f"  Client VAT No: {invoice_data.client_vat_no}")
                print(f"  Total Amount: {invoice_data.amount}")
                print(f"  Language: {invoice_data.detected_language}")

                if invoice_data.items:
                    print(f"\n🛒 ITEMS ({len(invoice_data.items)}):")
                    print(
                        f"  {'No.':<5} {'Item Name':<30} {'Translated':<30} {'Cost':<15}"
                    )
                    print(f"  {'-'*5} {'-'*30} {'-'*30} {'-'*15}")
                    for i, item in enumerate(invoice_data.items, 1):
                        print(
                            f"  {i:<5} {item.name[:30]:<30} {item.name_translated[:30]:<30} {item.cost:<15}"
                        )
                else:
                    print("\n  ℹ️ No items found in this invoice")
            else:
                print("  ❌ Failed to extract data from this page")

    if "errors" in extracted_data and extracted_data["errors"]:
        print(f"\n⚠️ ERRORS:")
        for error in extracted_data["errors"]:
            print(f"  - {error}")


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python extract_only_example.py <pdf_path> [--no-preprocess]")
        print("\nExample:")
        print("  python extract_only_example.py invoice.pdf")
        print("  python extract_only_example.py invoice.pdf --no-preprocess")
        sys.exit(1)

    pdf_path = sys.argv[1]
    preprocess = "--no-preprocess" not in sys.argv

    try:
        extract_and_print(pdf_path, preprocess)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
