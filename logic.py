import sqlite3

# Save user issue to the requests table in the database, including username
def save_request(user_id, message, department, username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            department TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            username TEXT
        )
    """)
    cursor.execute("INSERT INTO requests (user_id, message, department, username) VALUES (?, ?, ?, ?)", 
                   (user_id, message, department, username))
    conn.commit()
    conn.close()