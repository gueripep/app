import sqlite3

# Set up SQLite DB (if you don't have one)
conn = sqlite3.connect('data.db')
c = conn.cursor()

# Create table for storing file info
c.execute('''
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    content TEXT,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Function to insert a new file
def insert_file(filename, content, last_modified):
    print("Inserting file into DB")
    print(f"filename: {filename}")
    c.execute('''
    INSERT INTO files (filename, content, last_modified)
    VALUES (?, ?, ?)
    ''', (filename, content, last_modified))
    conn.commit()
    return  {
        "id": c.lastrowid,
        "filename": filename,
        "content": content,
        "last_modified": last_modified
    }

# Function to get all files
def get_all_files_from_db():
    c.execute('SELECT * FROM files')
    return c.fetchall()

def get_file_by_id(file_id):
    c.execute('SELECT * FROM files WHERE id = ?', (file_id,))
    return c.fetchone()

def update_file(file_id, filename, content, last_modified):
    c.execute('''
    UPDATE files
    SET filename = ?, content = ?, last_modified = ?
    WHERE id = ?
    ''', (filename, content, last_modified, file_id))
    conn.commit()

def get_file_db_info_by_name(filename):
    c.execute('SELECT * FROM files WHERE filename = ?', (filename,))
    return c.fetchone()

def delete_file(file_id):
    c.execute('DELETE FROM files WHERE id = ?', (file_id,))
    conn.commit()