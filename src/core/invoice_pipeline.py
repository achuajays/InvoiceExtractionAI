import logging
import os
from typing import Dict, List, Optional

from dotenv import load_dotenv

from pdf_converter import PDFConverter
from src.core.image_preprocessor import ImagePreprocessor
from src.core.invoice_extractorgemini import InvoiceExtractorGEMINI
from src.core.invoice_extractoropenai import InvoiceExtractorOPENAI
from src.core.invoice_postprocessor import InvoicePostProcessor
from src.models.models import InvoiceData, MultipleInvoicesResponse

load_dotenv()  # Load environment variables from .env file


print("SERVICE:", os.getenv("SERVICE"))


class InvoicePipeline:
    def __init__(self, output_folder: str = "temp_images"):
        self.pdf_converter = PDFConverter(output_folder)
        self.preprocessor = ImagePreprocessor()
        self.extractor_openai = InvoiceExtractorOPENAI()
        self.extractor_gemini = InvoiceExtractorGEMINI()
        self.output_folder = output_folder
        self.service = os.getenv("SERVICE")

    def process(self, pdf_path: str, preprocess=True) -> Optional[InvoiceData]:
        """
        Process a PDF and extract invoice data from all pages.
        Returns a single InvoiceData object with combined data from all pages.
        """
        combined_data = None
        filename = os.path.basename(pdf_path)

        image_paths = self.pdf_converter.convert(pdf_path)

        for img in image_paths:
            try:
                if preprocess:
                    img = self.preprocessor.preprocess(img)
                if self.service == "openai":
                    extracted_data = self.extractor_openai.extract(img)
                else:
                    extracted_data = self.extractor_gemini.extract(img)

                if extracted_data:
                    # Post-process to add VAT calculations
                    data = InvoicePostProcessor.add_vat_calculations(extracted_data)

                    if data:
                        if not combined_data:
                            combined_data = data  # Initialize with the first page data
                            combined_data.filename = filename
                        else:
                            # Combine subsequent page data (merge invoice lines)
                            combined_data.invoice_lines.extend(data.invoice_lines)
            except Exception as e:
                logging.error(f"Error processing image {img}: {str(e)}")

        if not combined_data:
            raise ValueError("Failed to extract any data from the PDF.")

        return combined_data

    def process_multiple(
        self, pdf_paths: List[str], preprocess=True
    ) -> MultipleInvoicesResponse:
        """
        Process multiple PDF files and extract invoice data from each.
        Returns a MultipleInvoicesResponse with all processed invoices.
        """
        invoices = []
        successful_extractions = 0
        failed_extractions = 0

        for pdf_path in pdf_paths:
            try:
                invoice_data = self.process(pdf_path, preprocess)
                if invoice_data:
                    invoices.append(invoice_data)
                    successful_extractions += 1
                else:
                    failed_extractions += 1
                    logging.warning(f"Failed to extract data from {pdf_path}")
            except Exception as e:
                failed_extractions += 1
                logging.error(f"Error processing {pdf_path}: {str(e)}")

        return MultipleInvoicesResponse(
            invoices=invoices,
            total_processed=len(pdf_paths),
            successful_extractions=successful_extractions,
            failed_extractions=failed_extractions,
        )
