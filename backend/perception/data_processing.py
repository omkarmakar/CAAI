import fitz  # PyMuPDF
from PIL import Image
from typing import Dict
import os

class DocumentProcessor:
    """
    Extracts text and structured data from various document types without OCR.
    """

    def __init__(self):
        """
        Initializes the DocumentProcessor.
        """
        pass  # No OCR setup required

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extracts text from a PDF file using PyMuPDF.

        Args:
            pdf_path (str): The path to the PDF file.

        Returns:
            str: The extracted text from the PDF.
        """
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def extract_metadata_from_image(self, image_path: str) -> str:
        """
        Extracts basic metadata from an image file without OCR.

        Args:
            image_path (str): The path to the image file.

        Returns:
            str: Metadata summary string.
        """
        with Image.open(image_path) as img:
            format = img.format
            size = img.size  # (width, height)
            mode = img.mode
        return f"Image metadata - Format: {format}, Size: {size}, Mode: {mode}"

    def process_document(self, file_path: str) -> Dict:
        """
        Processes a document (PDF or image) to extract text or metadata.

        Args:
            file_path (str): The path to the document file.

        Returns:
            Dict: A dictionary containing the extracted text/metadata and file type.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            text = self.extract_text_from_pdf(file_path)
            file_type = "PDF"
        elif ext in ['.png', '.jpg', '.jpeg', '.tiff']:
            text = self.extract_metadata_from_image(file_path)
            file_type = "Image"
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        return {"file_path": file_path, "file_type": file_type, "content": text}
