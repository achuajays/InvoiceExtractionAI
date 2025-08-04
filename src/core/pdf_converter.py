import logging
import os
from typing import List

from pdf2image import convert_from_path


class PDFConverter:
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)

    def convert(self, pdf_path: str) -> List[str]:
        try:
            images = convert_from_path(pdf_path)
            output_paths = []
            for i, image in enumerate(images):
                path = os.path.join(self.output_folder, f"page_{i+1}.png")
                image.save(path, "PNG")
                output_paths.append(path)
            return output_paths
        except Exception as e:
            logging.error(f"PDF conversion failed: {e}")
            return []
