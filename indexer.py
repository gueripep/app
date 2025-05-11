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
    index = client.index(index_name)
    index.add_documents([document])
    
def delete_document(client: Client, index_name: str, document_id: str):
    """Delete a document from the index."""
    index = client.index(index_name)
    index.delete_document(document_id)