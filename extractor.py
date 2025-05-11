import pdfplumber # type: ignore
import os

def fetch_all_files() -> list:
    """Fetch all files from pdfs directory recursively."""
    files = []
    for root, _, filenames in os.walk("pdfs"):
        for filename in filenames:
            if filename.endswith(".pdf"):
                files.append(os.path.join(root, filename))
    return files

def extract_text_from_all_pdfs() -> list:
    """Extract text from all PDFs in the pdfs directory."""
    pdf_files = fetch_all_files()
    extracted_texts = []
    for pdf_file in pdf_files:
        try:
            text = extract_data_from_pdf(pdf_file)["content"]
            document = {
                "filename": pdf_file,
                "content": text,
                "last_modified": os.path.getmtime(pdf_file),
            }
            extracted_texts.append(document)
        except Exception as e:
            print(f"Error extracting text from {pdf_file}: {e}")
    return extracted_texts


def extract_data_from_pdf(filename: str) -> str:    
    with pdfplumber.open(filename) as pdf:
        full_text = ''
        for page in pdf.pages:
            full_text += page.extract_text()  # Add text from each page
    document = {
        "filename": filename,
        "content": full_text,
        "last_modified": os.path.getmtime(filename),
    }
    return document