from meilisearch import Client # type: ignore

def create_index(client: Client, index_name: str):
    """Create a new index for storing PDFs."""
    client.create_index(index_name, {"primaryKey": "id"})

def index_pdf_text(client: Client, index_name: str, pdf_id: str, pdf_text: str, pdf_filename: str):
    """Index PDF text in Meilisearch."""
    document = {
        "id": pdf_id,
        "filename": pdf_filename,
        "text": pdf_text
    }
    print(f"Le document avec pour id {pdf_id} a comme texte : {pdf_text}")
    index = client.index(index_name)
    print(f"Index {index}")
    index.add_documents([document])