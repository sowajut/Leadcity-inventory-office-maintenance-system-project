import sqlite3
import os

DB_PATH = os.path.join("database", "database.db")  # same as your Flask app

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE maintenance ADD COLUMN date_reported TEXT")
    print("✅ Column 'date_reported' added to maintenance table.")
except sqlite3.OperationalError as e:
    print("⚠️", e)

conn.commit()
conn.close()
