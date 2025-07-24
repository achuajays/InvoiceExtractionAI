from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any
from fastapi.middleware.cors import CORSMiddleware
from src.core.invoice_pipeline import InvoicePipeline
from src.models.models import InvoiceData, InvoiceLine, MultipleInvoicesResponse
from typing import Dict, List, Optional
from pydantic import BaseModel
import shutil
import os
import tempfile

app = FastAPI(
    title="Invoice Extraction API",
    description="Extract invoice data from PDF files using AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/extract", response_model=InvoiceData)
async def extract_invoice(pdf: UploadFile = File(...)):
    """
    Extract invoice data from an uploaded PDF file.
    Processes all pages and returns a single combined result.

    - **pdf**: PDF file to process

    Returns extracted invoice data with new field structure.
    """
    if not pdf.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400, detail="Only PDF files are supported")

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        # Save the uploaded PDF
        shutil.copyfileobj(pdf.file, tmp_file)
        tmp_path = tmp_file.name

    try:
        # Initialize the extraction pipeline
        pipeline = InvoicePipeline()

        # Process the PDF - returns a single InvoiceData object
        invoice_data = pipeline.process(tmp_path, preprocess=True)
        
        # Set the original filename
        invoice_data.filename = pdf.filename

        return invoice_data

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Extraction failed: {str(e)}")
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/extract-multiple", response_model=MultipleInvoicesResponse)
async def extract_multiple_invoices(pdfs: List[UploadFile] = File(...)):
    """
    Extract invoice data from multiple uploaded PDF files.
    Processes each file separately and returns combined results.

    - **pdfs**: List of PDF files to process

    Returns extracted invoice data from all files with processing statistics.
    """
    # Validate all files are PDFs
    for pdf in pdfs:
        if not pdf.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400, detail=f"Only PDF files are supported. Invalid file: {pdf.filename}")

    temp_paths = []
    original_filenames = []

    try:
        # Save all uploaded files to temporary locations
        for pdf in pdfs:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                shutil.copyfileobj(pdf.file, tmp_file)
                temp_paths.append(tmp_file.name)
                original_filenames.append(pdf.filename)

        # Initialize the extraction pipeline
        pipeline = InvoicePipeline()

        # Process all PDFs
        result = pipeline.process_multiple(temp_paths, preprocess=True)
        
        # Set the original filenames for each invoice
        for i, invoice in enumerate(result.invoices):
            if i < len(original_filenames):
                invoice.filename = original_filenames[i]

        return result

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Extraction failed: {str(e)}")
    finally:
        # Clean up all temporary files
        for tmp_path in temp_paths:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)



class CustomExtractionRequest(BaseModel):
    fields: Dict[str, str]  # field_name: description
    custom_fields: Optional[Dict[str, str]] = {}  # Additional fields not in standard schema

@app.post("/custom-extract")
async def custom_extract_with_body(
    pdf: UploadFile = File(...), 
    fields: str = None
):
    """
    Customizable invoice extraction based on specified fields.
    
    - **pdf**: PDF file to extract data from
    - **fields**: JSON string of fields to extract
    
    Example fields: '{"partner": "Company name", "vat_number": "VAT registration number"}'
    
    Returns extracted data based on custom specifications.
    """
    if not pdf.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Parse the fields parameter
    if not fields:
        raise HTTPException(status_code=400, detail="Fields parameter is required")
    
    try:
        import json
        requested_fields = json.loads(fields)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format for fields parameter")
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        # Save the uploaded PDF
        shutil.copyfileobj(pdf.file, tmp_file)
        tmp_path = tmp_file.name

    try:
        # Initialize custom extraction pipeline
        from src.core.custom_extractor import CustomInvoiceExtractor
        extractor = CustomInvoiceExtractor()
        
        # Extract data based on custom fields
        custom_data = extractor.extract_custom_fields(tmp_path, requested_fields)
        
        return {
            "filename": pdf.filename,
            "extracted_data": custom_data,
            "requested_fields": list(requested_fields.keys())
        }

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Custom extraction failed: {str(e)}")
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/predefined-extract")
async def predefined_extract(
    pdf: UploadFile = File(...), 
    field_set: str = "basic"
):
    """
    Extract predefined sets of fields from invoice.
    
    - **pdf**: PDF file to extract data from
    - **field_set**: Type of field set ("basic", "detailed", "accounting")
    
    Available field sets:
    - basic: partner, invoice_bill_date, reference, total_amount
    - detailed: basic + vat_number, address, contact info
    - accounting: detailed + cr_number, invoice_type, invoice_lines, tax_amount
    
    Returns extracted data for the selected field set.
    """
    if not pdf.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        # Save the uploaded PDF
        shutil.copyfileobj(pdf.file, tmp_file)
        tmp_path = tmp_file.name

    try:
        # Initialize custom extraction pipeline
        from src.core.custom_extractor import CustomInvoiceExtractor
        extractor = CustomInvoiceExtractor()
        
        # Extract data based on predefined field set
        extracted_data = extractor.extract_predefined_fields(tmp_path, field_set)
        
        return {
            "filename": pdf.filename,
            "field_set": field_set,
            "extracted_data": extracted_data
        }

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Predefined extraction failed: {str(e)}")
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.get("/")
async def read_root():
    return {
        "message": "Welcome to the Invoice Extraction API!",
        "endpoints": {
            "POST /extract": "Upload a single PDF file to extract all standard invoice data",
            "POST /extract-multiple": "Upload multiple PDF files to extract invoice data from all",
            "POST /custom-extract": "Upload PDF and specify custom fields to extract (JSON format)",
            "POST /predefined-extract": "Upload PDF and use predefined field sets (basic/detailed/accounting)",
            "GET /available-fields": "Get list of all available fields for extraction",
            "GET /docs": "Interactive API documentation",
            "GET /redoc": "Alternative API documentation",
            "GET /health": "Health check endpoint"
        },
        "standard_fields": [
            "partner", "vat_number", "cr_number", "street", "street2",
            "country", "email", "city", "mobile", "invoice_type",
            "invoice_bill_date", "reference", "invoice_lines", "detected_language"
        ],
        "predefined_field_sets": {
            "basic": ["partner", "invoice_bill_date", "reference", "total_amount"],
            "detailed": ["partner", "vat_number", "invoice_bill_date", "reference", "street", "city", "country", "email", "mobile"],
            "accounting": ["partner", "vat_number", "cr_number", "invoice_type", "invoice_bill_date", "reference", "invoice_lines", "total_amount", "tax_amount"]
        }
    }


@app.get("/available-fields")
async def get_available_fields():
    """Get all available fields that can be extracted from invoices."""
    return {
        "standard_fields": {
            "partner": "Company or client name",
            "vat_number": "VAT registration number",
            "cr_number": "Commercial registration number",
            "street": "Primary address line",
            "street2": "Secondary address line",
            "country": "Country name",
            "email": "Email address",
            "city": "City name",
            "mobile": "Phone/mobile number",
            "invoice_type": "Type of invoice",
            "invoice_bill_date": "Invoice date (DD/MM/YYYY)",
            "reference": "Invoice number or reference",
            "invoice_lines": "Array of line items",
            "detected_language": "Detected language",
            "total_amount": "Total invoice amount",
            "tax_amount": "Total tax amount",
            "subtotal": "Subtotal before taxes",
            "discount": "Discount amount",
            "due_date": "Payment due date",
            "payment_terms": "Payment terms",
            "currency": "Invoice currency",
            "po_number": "Purchase order number",
            "description": "Invoice description or notes"
        },
        "custom_examples": {
            "company_info": {
                "partner": "Company name",
                "street": "Address",
                "city": "City",
                "country": "Country"
            },
            "financial_summary": {
                "total_amount": "Total amount",
                "tax_amount": "Tax amount",
                "subtotal": "Subtotal",
                "currency": "Currency"
            },
            "invoice_details": {
                "reference": "Invoice number",
                "invoice_bill_date": "Invoice date",
                "due_date": "Due date",
                "payment_terms": "Payment terms"
            }
        }
    }

@app.get("/health")
async def health_check():
    """Check if the API is running."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
