import os

import cv2
from pdf2image import convert_from_path


def pdf_to_png(pdf_path, output_folder):
    """
    Converts each page of the PDF at pdf_path to a PNG image and saves them in output_folder.
    Returns a list of output PNG file paths.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    images = convert_from_path(pdf_path)
    output_files = []
    for i, image in enumerate(images):
        output_file = os.path.join(output_folder, f"page_{i+1}.png")
        image.save(output_file, "PNG")
        output_files.append(output_file)
    return output_files


def preprocess_for_vision_model(img_path):
    import cv2

    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Rotate if landscape
    if gray.shape[1] > gray.shape[0]:
        gray = cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    # Enhance contrast gently
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    # Binarization (optional, only if background is uneven)
    final = cv2.adaptiveThreshold(
        enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 25, 11
    )

    return final


images = pdf_to_png(r"C:\Users\adars\Invoice AI\ali.pdf", "image.png")
print(images)

new_image = preprocess_for_vision_model(images[0])
cv2.imwrite("new_image.png", new_image)


import base64
from typing import List

from google import genai
from pydantic import BaseModel


# Define schema for items
class Item(BaseModel):
    name: str
    name_translated: str  # Added translation field
    cost: str


# Define full invoice schema
class InvoiceData(BaseModel):
    party_name: str
    party_name_translated: str  # Added translation field
    date: str
    invoice_no: str
    vat_no: str
    amount: str
    vendor_addr: str
    vendor_addr_translated: str  # Added translation field
    items: List[Item]
    detected_language: str  # Added to track source language


def extract_invoice_gemini(image_path: str) -> InvoiceData:
    # Read image and encode as base64
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    # Initialize Gemini client (make sure genai.configure has already been called)
    client = genai.Client(
        api_key="",
    )

    # Enhanced prompt with translation instructions
    prompt = """
You are a document data extraction expert with multilingual capabilities. Extract and return the following fields in structured JSON format:

EXTRACTION REQUIREMENTS:
- party_name: Company/vendor name (original text)
- party_name_translated: English translation if original is not in English
- date: Invoice date (maintain original format)
- invoice_no: Invoice/document number
- vat_no: VAT registration number
- amount: Total amount with VAT (include currency symbol)
- vendor_addr: Complete vendor address (original text)
- vendor_addr_translated: English translation if original is not in English
- items: List of all products/services, each item should have:
    - name: Item description (original text)
    - name_translated: English translation if original is not in English
    - cost: Individual item cost (include currency if available)
- detected_language: Primary language detected in the document (e.g., "Arabic", "English", "Mixed")

TRANSLATION RULES:
1. If text is already in English, set the translated field to the same value
2. For Arabic text, provide accurate English translations
3. Preserve technical terms, product codes, and proper nouns appropriately
4. For mixed language documents, translate non-English portions only
5. If translation is uncertain, provide the best approximation

IMPORTANT: 
- Do not skip any values - if a field is not found, use "NOT_FOUND"
- For items without individual costs, use "INCLUDED" or "NOT_SPECIFIED"
- Return only valid JSON format
- Ensure all required fields are present
"""

    # Gemini Vision API call
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            {"text": prompt},
            {
                "inline_data": {
                    "mime_type": "image/png",  # or "image/jpeg"
                    "data": image_data,
                }
            },
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": InvoiceData,
        },
    )

    # Optional: print raw text output
    print("Raw response:")
    print(response.text)

    # Return structured data
    return response.parsed


# Alternative function for handling different image types
def extract_invoice_gemini_auto_mime(image_path: str) -> InvoiceData:
    """
    Enhanced version that automatically detects image mime type
    """
    import mimetypes

    # Detect mime type
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None or not mime_type.startswith("image/"):
        mime_type = "image/jpeg"  # default fallback

    # Read image and encode as base64
    with open(image_path, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")

    # Initialize Gemini client
    client = genai.Client(
        api_key="",
    )

    # Enhanced prompt with translation instructions
    prompt = """
You are a document data extraction expert with multilingual capabilities. Extract and return the following fields in structured JSON format:

EXTRACTION REQUIREMENTS:
- party_name: Company/vendor name (original text)
- party_name_translated: English translation if original is not in English
- date: Invoice date (maintain original format)
- invoice_no: Invoice/document number
- vat_no: VAT registration number
- amount: Total amount with VAT (include currency symbol)
- vendor_addr: Complete vendor address (original text)
- vendor_addr_translated: English translation if original is not in English
- items: List of all products/services, each item should have:
    - name: Item description (original text)
    - name_translated: English translation if original is not in English
    - cost: Individual item cost (include currency if available)
- detected_language: Primary language detected in the document (e.g., "Arabic", "English", "Mixed")

TRANSLATION RULES:
1. If text is already in English, set the translated field to the same value
2. For Arabic text, provide accurate English translations
3. Preserve technical terms, product codes, and proper nouns appropriately
4. For mixed language documents, translate non-English portions only
5. If translation is uncertain, provide the best approximation

IMPORTANT: 
- Do not skip any values - if a field is not found, use "NOT_FOUND"
- For items without individual costs, use "INCLUDED" or "NOT_SPECIFIED"
- Return only valid JSON format
- Ensure all required fields are present
"""

    # Gemini Vision API call with auto-detected mime type
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            {"text": prompt},
            {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": image_data,
                }
            },
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": InvoiceData,
        },
    )

    # Print results with translation info
    print("Raw response:")
    print(response.text)

    parsed_data = response.parsed
    print(f"\nDetected Language: {parsed_data.detected_language}")
    print(
        f"Party Name: {parsed_data.party_name} -> {parsed_data.party_name_translated}"
    )

    return parsed_data


# Example usage

result = extract_invoice_gemini_auto_mime(images[0])
print(f"\nExtracted Data:")
print(f"Company: {result.party_name} ({result.party_name_translated})")
print(f"Date: {result.date}")
print(f"Invoice No: {result.invoice_no}")
print(f"VAT No: {result.vat_no}")
print(f"Amount: {result.amount}")
print(f"Address: {result.vendor_addr}")
print(f"Address (EN): {result.vendor_addr_translated}")
print(f"\nItems:")

for item in result.items:
    try:
        print(f"  - {item.name} ({item.name_translated}): {item.cost}")
    except Exception as e:
        print(f"Error: {e}")


data = extract_invoice_gemini(images[0])
print(data.party_name)
print(data.date)
print(data.invoice_no)
print(data.vat_no)
print(data.amount)
print(data.vendor_addr)
print(data.items)
