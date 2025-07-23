import logging
from typing import List
from pdf_converter import PDFConverter
from image_preprocessor import ImagePreprocessor
from invoice_extractor import InvoiceExtractor
from invoice_storage import InvoiceStorage

class InvoicePipeline:
    def __init__(self, excel_path: str = "invoices_database.xlsx", output_folder: str = "temp_images"):
        self.pdf_converter = PDFConverter(output_folder)
        self.preprocessor = ImagePreprocessor()
        self.extractor = InvoiceExtractor()
        self.storage = InvoiceStorage(excel_path)
        self.output_folder = output_folder

    def process(self, pdf_path: str, preprocess=True) -> dict:
        result = {
            'processed_pages': 0,
            'successful_extractions': 0,
            'saved_to_excel': 0,
            'duplicates': 0,
            'errors': []
        }

        image_paths = self.pdf_converter.convert(pdf_path)
        result['processed_pages'] = len(image_paths)

        for i, img in enumerate(image_paths):
            try:
                if preprocess:
                    img = self.preprocessor.preprocess(img)

                data = self.extractor.extract(img)
                if data:
                    result['successful_extractions'] += 1
                    if self.storage.save(data):
                        result['saved_to_excel'] += 1
                    else:
                        result['duplicates'] += 1
                else:
                    result['errors'].append(f"Page {i+1}: No data extracted")
            except Exception as e:
                result['errors'].append(f"Page {i+1}: {str(e)}")

        return result
