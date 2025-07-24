from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
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

    try:
        # Save all uploaded files to temporary locations
        for pdf in pdfs:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                shutil.copyfileobj(pdf.file, tmp_file)
                temp_paths.append(tmp_file.name)

        # Initialize the extraction pipeline
        pipeline = InvoicePipeline()

        # Process all PDFs
        result = pipeline.process_multiple(temp_paths, preprocess=True)

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


@app.get("/")
async def read_root():
    return {
        "message": "Welcome to the Invoice Extraction API!",
        "endpoints": {
            "POST /extract": "Upload a single PDF file to extract invoice data",
            "POST /extract-multiple": "Upload multiple PDF files to extract invoice data from all",
            "GET /docs": "Interactive API documentation",
            "GET /redoc": "Alternative API documentation",
            "GET /health": "Health check endpoint"
        },
        "extracted_fields": [
            "partner", "vat_number", "cr_number", "street", "street2",
            "country", "email", "city", "mobile", "invoice_type",
            "invoice_bill_date", "reference", "invoice_lines", "detected_language"
        ]
    }


@app.get("/health")
async def health_check():
    """Check if the API is running."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
