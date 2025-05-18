import sqlite3

DB_PATH = "database.db" 

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# Create inventory table
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    department TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    condition TEXT NOT NULL,
    location TEXT NOT NULL
)
""")

# Create maintenance table
cursor.execute("""
CREATE TABLE IF NOT EXISTS maintenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    department TEXT NOT NULL,
    issue TEXT NOT NULL,
    status TEXT NOT NULL
)
""")

conn.commit()
conn.close()
print("✅ New database created successfully.")
