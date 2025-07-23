# Invoice Extraction FastAPI Application

This is a FastAPI-based web service for extracting invoice data from PDF files using Google's Gemini AI.

## Features

- **RESTful API** for invoice data extraction
- **Multi-page PDF support** - Process PDFs with multiple invoices
- **Automatic language detection and translation**
- **Image preprocessing** for better OCR results
- **Interactive API documentation** (Swagger UI & ReDoc)
- **CORS enabled** for cross-origin requests
- **Simple HTML test interface** included

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Google Gemini API key in `invoice_extractor.py`:
```python
self.client = genai.Client(api_key="YOUR_API_KEY_HERE")
```

## Running the Server

### Option 1: Using the startup script
```bash
python run_server.py
```

With auto-reload for development:
```bash
python run_server.py --reload
```

### Option 2: Using uvicorn directly
```bash
uvicorn app_fastapi:app --reload
```

## API Endpoints

### `POST /extract`
Extract invoice data from a PDF file.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: PDF file upload

**Response:**
```json
{
  "pages": {
    "1": {
      "party_name": "Vendor Name",
      "party_name_translated": "Translated Name",
      "date": "2024-01-15",
      "invoice_no": "INV-001",
      "vat_no": "123456789",
      "amount": "1,500.00",
      "vendor_addr": "123 Main St",
      "vendor_addr_translated": "123 Main St",
      "items": [
        {
          "name": "Product 1",
          "name_translated": "Product 1",
          "cost": "500.00"
        }
      ],
      "detected_language": "English"
    }
  },
  "total_pages": 1,
  "successful_extractions": 1,
  "errors": []
}
```

### `GET /`
Welcome endpoint with API information.

### `GET /health`
Health check endpoint.

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing the API

### Using the HTML Interface
Open `test_frontend.html` in your web browser to use the simple upload interface.

### Using cURL
```bash
curl -X POST "http://localhost:8000/extract" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "pdf=@invoice.pdf"
```

### Using Python
```python
import requests

with open('invoice.pdf', 'rb') as f:
    files = {'pdf': f}
    response = requests.post('http://localhost:8000/extract', files=files)
    print(response.json())
```

## Project Structure

```
InvoiceExtractionAI/
├── app_fastapi.py          # FastAPI application
├── run_server.py           # Server startup script
├── invoice_pipeline.py     # Core extraction pipeline
├── invoice_extractor.py    # Gemini AI integration
├── image_preprocessor.py   # Image preprocessing
├── pdf_converter.py        # PDF to image conversion
├── models.py              # Pydantic data models
├── requirements.txt       # Python dependencies
├── test_frontend.html     # Simple web interface
└── README_FASTAPI.md      # This file
```

## Configuration

### Environment Variables (Optional)
You can set these environment variables:

- `GEMINI_API_KEY`: Your Google Gemini API key
- `PORT`: Server port (default: 8000)
- `HOST`: Server host (default: 0.0.0.0)

### CORS Settings
CORS is currently configured to allow all origins (`*`). For production, update the `allow_origins` in `app_fastapi.py` to specify your frontend domain.

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Successful extraction
- `400`: Bad request (e.g., non-PDF file)
- `500`: Server error during extraction

Error responses include detailed messages in the response body.

## Development Tips

1. Use `--reload` flag during development for auto-reloading
2. Check `/docs` for testing individual endpoints
3. Monitor server logs for debugging
4. Temporary files are automatically cleaned up after processing

## Deployment

For production deployment:

1. Use a production ASGI server like Gunicorn:
```bash
gunicorn app_fastapi:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. Set up proper environment variables
3. Configure CORS for your specific frontend domain
4. Use HTTPS with proper SSL certificates
5. Set up monitoring and logging

## Note

This version focuses purely on extraction via API - no data is stored. Each request processes the PDF and returns the extracted data immediately.
