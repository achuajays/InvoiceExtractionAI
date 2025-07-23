from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.core.invoice_pipeline import InvoicePipeline
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

# Response models
class ItemResponse(BaseModel):
    name: str
    name_translated: str
    quantity: str
    cost: str

class InvoiceResponse(BaseModel):
    party_name: str
    party_name_translated: str
    date: str
    invoice_no: str
    seller_vat_no: str
    client_vat_no: str
    amount: str
    vendor_addr: str
    vendor_addr_translated: str
    items: List[ItemResponse]
    detected_language: str

@app.post("/extract", response_model=InvoiceResponse)
async def extract_invoice(pdf: UploadFile = File(...)):
    """
    Extract invoice data from an uploaded PDF file.
    Processes all pages and returns a single combined result.
    
    - **pdf**: PDF file to process
    
    Returns extracted invoice data as a single JSON object.
    """
    if not pdf.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
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
        
        # Convert to response format
        response = InvoiceResponse(
            party_name=invoice_data.party_name,
            party_name_translated=invoice_data.party_name_translated,
            date=invoice_data.date,
            invoice_no=invoice_data.invoice_no,
            seller_vat_no=invoice_data.seller_vat_no,
            client_vat_no=invoice_data.client_vat_no,
            amount=invoice_data.amount,
            vendor_addr=invoice_data.vendor_addr,
            vendor_addr_translated=invoice_data.vendor_addr_translated,
            items=[ItemResponse(
                name=item.name,
                name_translated=item.name_translated,
                quantity=item.quantity,
                cost=item.cost
            ) for item in invoice_data.items],
            detected_language=invoice_data.detected_language
        )
        
        return response

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.get("/")
async def read_root():
    return {
        "message": "Welcome to the Invoice Extraction API!",
        "endpoints": {
            "POST /extract": "Upload a PDF file to extract invoice data",
            "GET /docs": "Interactive API documentation",
            "GET /redoc": "Alternative API documentation"
        }
    }

@app.get("/health")
async def health_check():
    """Check if the API is running."""
    return {"status": "healthy"}
