from fastapi import FastAPI # type: ignore
from pydantic import BaseModel # type: ignore
from meilisearch import Client # type: ignore
from extractor import extract_data_from_pdf, extract_text_from_all_pdfs
from indexer import create_index, index_pdf_text
from typing import Union
from db import get_all_files, insert_file, get_file_by_name, update_file
import sqlite3


app = FastAPI()

# Meilisearch client
client = Client('http://meilisearch:7700', "masterKey")
index_name = "pdfs"

class SearchRequest(BaseModel):
    query: str

# Create index on app startup
@app.on_event("startup")
async def startup():
    create_index(client, index_name)
    update_all_indexes()

def update_all_indexes():
    """Update all indexes with the latest PDFs."""
    pdfs_contents = extract_text_from_all_pdfs()
    for pdf in pdfs_contents:
        existing_file = get_file_by_name(pdf["filename"])
        # update the file if there is a more recent version
        if existing_file:
            if existing_file[3] != pdf["last_modified"]:
                pdf_id = existing_file[0]
                update_file(pdf_id, pdf["filename"], pdf["content"], pdf["last_modified"])
                index_pdf_text(client, index_name, pdf_id, pdf["content"], pdf["filename"])
            else:
                # skip the file if it is already indexed
                print(f"File {pdf['filename']} is already indexed.")
        else:
            # insert the file if it doesn't exist
            document = insert_file(pdf["filename"], pdf["content"], pdf["last_modified"])
            index_pdf_text(client, index_name, document["id"], pdf["content"], pdf["filename"])
    

@app.post("/search")
async def search(request: SearchRequest):
    """Search PDFs with a query."""
    index = client.index(index_name)
    results = index.search(request.query)
    return results

@app.post("/index_pdf")
async def index_pdf(filename: str):
    """Index a PDF into Meilisearch."""
    document = extract_data_from_pdf(f"pdfs/{filename}")
    documentId = insert_file(filename, document["content"], document["last_modified"])
    index_pdf_text(client, index_name, documentId, document["content"])
    return {"status": "success", "message": f"PDF {documentId} indexed"}


#db
def get_conn():
    return sqlite3.connect("data.db")

@app.get("/files")
def list_files():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files")
    return cursor.fetchall()