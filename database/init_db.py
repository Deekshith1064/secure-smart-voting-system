import sqlite3
import os

# Get database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database.db")


def initialize_database():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    print("Creating tables...")

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        voter_id TEXT UNIQUE NOT NULL,
        has_voted INTEGER DEFAULT 0,
        role TEXT DEFAULT 'voter'
    )
    """)

    # CANDIDATES TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_name TEXT NOT NULL,
        vote_count INTEGER DEFAULT 0
    )
    """)

    # VOTES TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        candidate_id INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(candidate_id) REFERENCES candidates(id)
    )
    """)

    # ELECTION STATUS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS election_status (
        id INTEGER PRIMARY KEY,
        status INTEGER DEFAULT 0
    )
    """)

    # Ensure one default row exists
    cursor.execute("""
    INSERT OR IGNORE INTO election_status (id, status)
    VALUES (1, 0)
    """)

    # INSERT DEFAULT ADMIN USER
    cursor.execute("""
    INSERT OR IGNORE INTO users (username, password, voter_id, role)
    VALUES ('admin', 'admin123', 'ADMIN001', 'admin')
    """)

    connection.commit()
    connection.close()

    print("Database initialized successfully!")


if __name__ == "__main__":
    initialize_database()