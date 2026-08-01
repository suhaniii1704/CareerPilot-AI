import fitz
from docx import Document
from pathlib import Path


def extract_text(file_path):

    extension=Path(file_path).suffix.lower()

    if extension==".pdf":
        document=fitz.open(file_path)
        text=""

        for page in document:
            text+=page.get_text()

        document.close()
        return text

    elif extension == ".docx":
        document = Document(file_path)
        text = ""

        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"

        return text

    else:
        raise ValueError("Unsupported File Format")