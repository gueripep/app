import textract # type: ignore
import os

SUPPORTED_EXTENSIONS = [
    ".csv", ".doc", ".docx", ".eml", ".epub", ".gif", ".jpg", ".jpeg", ".json",
    ".html", ".htm", ".mp3", ".msg", ".odt", ".ogg", ".pdf", ".png", ".pptx",
    ".ps", ".rtf", ".tiff", ".tif", ".txt", ".wav", ".xlsx", ".xls"
]

def fetch_all_filenames() -> list:
    files = []
    for root, _, filenames in os.walk("pdfs"):
        for filename in filenames:
            if any(filename.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                files.append(os.path.join(root, filename))
    return files

def extract_text_from_all_pdfs() -> list:
    """Extract text from all PDFs in the pdfs directory."""
    pdf_files = fetch_all_filenames()
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
    full_text = textract.process(filename).decode('utf-8')

    document = {
        "filename": filename,
        "content": full_text,
        "last_modified": os.path.getmtime(filename),
    }
    return document