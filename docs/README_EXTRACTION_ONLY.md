# Invoice Extraction AI - Extraction Only Mode

This version of the Invoice Extraction AI focuses purely on extracting and displaying invoice data without any storage functionality.

## Features

- Extract invoice data from PDF files
- Support for multi-page PDFs
- Automatic language detection and translation
- Image preprocessing for better OCR results
- Detailed console output with formatted display

## Removed Features

- Excel file storage
- Database functionality
- Duplicate checking
- Data persistence

## Usage

### Basic Usage

```bash
python main.py
```

This will process the PDF file specified in `main.py` (default: "ali.pdf") and print the extracted data to the console.

### Command Line Example

```bash
python extract_only_example.py invoice.pdf
```

### Without Preprocessing

```bash
python extract_only_example.py invoice.pdf --no-preprocess
```

## Output Format

The extraction results are displayed in a structured format:

```
📋 INVOICE EXTRACTION RESULTS
============================================================

📄 Page 1:
----------------------------------------
Party Name: [Vendor Name]
Party Name (Translated): [Translated Name]
Date: [Invoice Date]
Invoice No: [Invoice Number]
VAT No: [VAT Number]
Total Amount: [Total Amount]
Vendor Address: [Address]
Vendor Address (Translated): [Translated Address]
Detected Language: [Language]

Items (X):
  1. [Item Name] ([Translated Name]) - [Cost]
  2. [Item Name] ([Translated Name]) - [Cost]
  ...
```

## Code Structure

- `main.py` - Simple extraction script for the default PDF
- `extract_only_example.py` - Command-line extraction tool
- `invoice_pipeline.py` - Core pipeline without storage functionality
- `invoice_extractor.py` - Gemini AI extraction logic
- `image_preprocessor.py` - Image preprocessing utilities
- `pdf_converter.py` - PDF to image conversion
- `models.py` - Data models for invoice structure

## Note

The `invoice_storage.py` file is no longer used in this extraction-only version. All storage-related functionality has been removed to focus purely on data extraction and display.
