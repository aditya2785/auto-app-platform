import os
import sqlite3
from database.db_utils import init_db, get_connection

def test_init_db():
    """
    Tests that the database is initialized correctly.
    """
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'tasks.db')
    if os.path.exists(db_path):
        os.remove(db_path)

    init_db()

    assert os.path.exists(db_path)

    conn = get_connection()
    cur = conn.cursor()

    # Check if 'tasks' table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
    assert cur.fetchone() is not None, "Table 'tasks' does not exist"

    # Check if 'repos' table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='repos'")
    assert cur.fetchone() is not None, "Table 'repos' does not exist"

    # Check if 'results' table exists
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='results'")
    assert cur.fetchone() is not None, "Table 'results' does not exist"

    conn.close()
    os.remove(db_path)