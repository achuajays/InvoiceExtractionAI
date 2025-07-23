import logging
from typing import Dict, Optional
from pdf_converter import PDFConverter
from src.core.image_preprocessor import ImagePreprocessor
from src.core.invoice_extractor import InvoiceExtractor
from models import InvoiceData

class InvoicePipeline:
    def __init__(self, output_folder: str = "temp_images"):
        self.pdf_converter = PDFConverter(output_folder)
        self.preprocessor = ImagePreprocessor()
        self.extractor = InvoiceExtractor()
        self.output_folder = output_folder
    def process(self, pdf_path: str, preprocess=True) -> Optional[InvoiceData]:
        """
        Process a PDF and extract invoice data from all pages.
        Returns a single InvoiceData object with combined data from all pages.
        """
        combined_data = None

        image_paths = self.pdf_converter.convert(pdf_path)
        
        for img in image_paths:
            try:
                if preprocess:
                    img = self.preprocessor.preprocess(img)

                data = self.extractor.extract(img)
                if data:
                    if not combined_data:
                        combined_data = data  # Initialize with the first page data
                    else:
                        # Combine subsequent page data
                        combined_data.items.extend(data.items)
                        combined_data.amount = str(float(combined_data.amount) + float(data.amount))
            except Exception as e:
                logging.error(f"Error processing image {img}: {str(e)}")
        
        if not combined_data:
            raise ValueError("Failed to extract any data from the PDF.")
        
        return combined_data
