import cv2
import os
import logging

class ImagePreprocessor:
    def preprocess(self, image_path: str) -> str:
        try:
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            if gray.shape[1] > gray.shape[0]:
                gray = cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE)

            denoised = cv2.fastNlMeansDenoising(gray, h=10)
            clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            final = cv2.adaptiveThreshold(enhanced, 255,
                                          cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 25, 11)
            output_path = image_path.replace('.png', '_processed.png')
            cv2.imwrite(output_path, final)
            return output_path
        except Exception as e:
            logging.error(f"Preprocessing failed: {e}")
            return image_path
