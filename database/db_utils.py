import sqlite3
import os

DB_FILE = "tasks.db"

def get_db_path():
    """Returns the absolute path to the database file."""
    return os.path.abspath(DB_FILE)

def get_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def execute(query, params=()):
    """Executes a query and returns the last inserted row id."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def fetchall(query, params=()):
    """Fetches all rows from a query."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if conn:
            conn.close()

def fetchone(query, params=()):
    """Fetches one row from a query."""
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        row = cur.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def main():
    """Initializes the database and creates the tasks table."""
    conn = None
    try:
        conn = get_connection()
        conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            task TEXT,
            round INTEGER,
            nonce TEXT,
            brief TEXT,
            attachments TEXT,
            checks TEXT,
            evaluation_url TEXT,
            endpoint TEXT,
            statuscode INTEGER,
            secret TEXT,
            repo_url TEXT,
            commit_sha TEXT,
            pages_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        print("Database initialized and tasks table created.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
