from fastapi import FastAPI # type: ignore
from pydantic import BaseModel # type: ignore
from meilisearch import Client # type: ignore
from extractor import extract_data_from_pdf, fetch_all_filenames
from indexer import create_index, index_pdf_text, delete_document
from typing import Union
from db import insert_file, get_file_db_info_by_name, update_file, get_all_files_from_db, delete_file
from fastapi.middleware.cors import CORSMiddleware # type: ignore
import sqlite3
import os
from fastapi.responses import FileResponse # type: ignore


app = FastAPI()

origins = [
    "http://127.0.0.1:5500",
    "null" 
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Meilisearch client
client = Client('http://meilisearch:7700', "masterKey")
index_name = "pdfs"

class SearchRequest(BaseModel):
    query: str

# Create index on app startup
@app.on_event("startup")
def startup():
    create_index(client, index_name)
    delete_document_and_db_entry_for_deleted_files()
    update_all_indexes()
    
def delete_document_and_db_entry_for_deleted_files():
    """Delete indexes for files that have been deleted."""
    db_files = get_all_files_from_db()
    pdfs_filenames = fetch_all_filenames()
    
    # Find files that are in the database but not in the filesystem
    for file in db_files:
        file_name = file[1]
        print(f"File name: {file_name}")
        if file_name not in pdfs_filenames:
            file_id = file[0]
            print(f"Deleting {file_name} from database and index.")
            print(f"File ID: {file_id}")
            delete_document(client, index_name, file_id)
            delete_file(file_id)
            print(f"Deleted {file_name} document and from database.")

def update_all_indexes():
    """Update all indexes with the latest PDFs."""
    pdfs_filenames = fetch_all_filenames()
    for pdf_name in pdfs_filenames:
        file_db_info = get_file_db_info_by_name(pdf_name)
        # update the file if there is a more recent version
        if file_db_info:
            file_last_modified = os.path.getmtime(pdf_name)
            if file_db_info[3] != file_last_modified:
                pdf = extract_data_from_pdf(pdf_name)
                pdf_id = file_db_info[0]
                update_file(pdf_id, pdf_name, pdf["content"], pdf["last_modified"])
                index_pdf_text(client, index_name, pdf_id, pdf["content"], pdf_name)
            else:
                # skip the file if it is already indexed
                print(f"File {pdf_name} is already indexed.")
        else:
            # insert the file if it doesn't exist
            pdf = extract_data_from_pdf(pdf_name)
            document = insert_file(pdf_name, pdf["content"], pdf["last_modified"])
            index_pdf_text(client, index_name, document["id"], pdf["content"], pdf_name)
    

@app.post("/search")
async def search(request: SearchRequest):
    """Search PDFs with a query."""
    index = client.index(index_name)
    results = index.search(request.query, {
        "attributesToHighlight": ["*"]
    })
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


# Endpoint to serve a PDF
@app.get("/pdfs/{pdf_filename}")
async def get_pdf(pdf_filename: str):
    pdf_path = os.path.join('pdfs', pdf_filename)

    # Check if the file exists
    if not os.path.exists(pdf_path):
        return {"error": "PDF not found"}

    if pdf_filename.endswith('.pdf'):
        return FileResponse(pdf_path, media_type='application/pdf')
    else:
        return FileResponse(
            pdf_path,
            media_type='application/octet-stream',
            headers={"Content-Disposition": f"attachment; filename={pdf_filename}"}
        )
