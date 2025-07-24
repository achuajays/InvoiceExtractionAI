"""
Test script for multiple file processing functionality.
This script demonstrates how to use the new multiple file processing capabilities.
"""

import requests
import json
from pathlib import Path

def test_single_extraction(file_path: str, api_url: str = "http://localhost:8000"):
    """Test single file extraction."""
    print(f"Testing single file extraction for: {file_path}")
    
    url = f"{api_url}/extract"
    
    with open(file_path, 'rb') as f:
        files = {'pdf': (Path(file_path).name, f, 'application/pdf')}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Single extraction successful!")
        print(f"Partner: {result.get('partner', 'N/A')}")
        print(f"VAT Number: {result.get('vat_number', 'N/A')}")
        print(f"Invoice Type: {result.get('invoice_type', 'N/A')}")
        print(f"Invoice Lines: {len(result.get('invoice_lines', []))}")
        print("-" * 50)
    else:
        print(f"❌ Single extraction failed: {response.status_code} - {response.text}")

def test_multiple_extraction(file_paths: list, api_url: str = "http://localhost:8000"):
    """Test multiple file extraction."""
    print(f"Testing multiple file extraction for {len(file_paths)} files")
    
    url = f"{api_url}/extract-multiple"
    
    files = []
    file_handles = []
    
    try:
        # Open all files
        for file_path in file_paths:
            f = open(file_path, 'rb')
            file_handles.append(f)
            files.append(('pdfs', (Path(file_path).name, f, 'application/pdf')))
        
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Multiple extraction successful!")
            print(f"Total processed: {result['total_processed']}")
            print(f"Successful extractions: {result['successful_extractions']}")
            print(f"Failed extractions: {result['failed_extractions']}")
            
            print("\nExtracted invoices:")
            for i, invoice in enumerate(result['invoices'], 1):
                print(f"  Invoice {i} ({invoice.get('filename', 'Unknown')}):")
                print(f"    Partner: {invoice.get('partner', 'N/A')}")
                print(f"    VAT Number: {invoice.get('vat_number', 'N/A')}")
                print(f"    Invoice Type: {invoice.get('invoice_type', 'N/A')}")
                print(f"    Invoice Lines: {len(invoice.get('invoice_lines', []))}")
            print("-" * 50)
        else:
            print(f"❌ Multiple extraction failed: {response.status_code} - {response.text}")
    
    finally:
        # Close all file handles
        for f in file_handles:
            f.close()

def main():
    """Main test function."""
    print("🚀 Starting Invoice Extraction API Tests")
    print("=" * 60)
    
    # Test API health first
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API is healthy and running")
        else:
            print("❌ API health check failed")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure it's running on http://localhost:8000")
        return
    
    print("\n📋 Available endpoints:")
    response = requests.get("http://localhost:8000/")
    if response.status_code == 200:
        info = response.json()
        for endpoint, description in info['endpoints'].items():
            print(f"  {endpoint}: {description}")
        
        print(f"\n📊 Extracted fields: {', '.join(info['extracted_fields'])}")
    
    # Example usage - you would replace these with actual PDF file paths
    sample_files = [
        # "path/to/invoice1.pdf",
        # "path/to/invoice2.pdf",
        # "path/to/invoice3.pdf"
    ]
    
    print("\n" + "=" * 60)
    print("📝 To test with actual files:")
    print("1. Replace the sample_files list with paths to your PDF files")
    print("2. Uncomment the test function calls below")
    print("3. Run this script again")
    
    # Uncomment these lines when you have actual PDF files to test
    # if sample_files:
    #     if len(sample_files) >= 1:
    #         test_single_extraction(sample_files[0])
    #     
    #     if len(sample_files) >= 2:
    #         test_multiple_extraction(sample_files)
    # else:
    #     print("\n⚠️  No sample files provided for testing")

if __name__ == "__main__":
    main()
