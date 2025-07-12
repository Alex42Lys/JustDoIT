import sqlite3

db_path = "/home/starman/os/JustDoIT/Kairat/app.db"
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("Tables:", cursor.fetchall())
    
    # Check Area table structure
    cursor.execute("PRAGMA table_info(Area);")
    print("Area table columns:", cursor.fetchall())
    
    conn.close()
    print("Database access successful!")
except Exception as e:
    print(f"Error accessing database: {e}")