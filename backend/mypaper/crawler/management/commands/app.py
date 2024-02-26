import fitz
import pathlib
from PyPDF2 import PdfReader
from django.core.management import BaseCommand
import os
import sys
from django.conf import settings


def pymupdf_get_pdf_text(file):
    text = ""
    with fitz.open(file) as doc:
        text=chr(12).join([page.get_text() for page in doc])
    pathlib.Path('./pymupdf.txt').write_bytes(text.encode())


def pypdf2_get_pdf_text(file):
    text = ""
    pdf_reader = PdfReader(file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    pathlib.Path('./pypdf2.txt').write_bytes(text.encode())


class Command(BaseCommand):
    help = (
        "Extract text from pdfs"
    )

    def handle(self, *args, **kwargs):
        pymupdf_get_pdf_text(f"{settings.BASE_DIR.parent}/paperspider/paperspider/downloads/2023/aaai/A. Pavan_8822.pdf")
        pypdf2_get_pdf_text(f"{settings.BASE_DIR.parent}/paperspider/paperspider/downloads/2023/aaai/A. Pavan_8822.pdf")
