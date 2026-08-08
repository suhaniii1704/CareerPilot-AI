import sqlite3
import json
from datetime import datetime



DB_NAME = "careerpilot.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TEXT
    )
    """)

    # Resume analyses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        target_role TEXT,
        ats_score INTEGER,
        resume_json TEXT,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()

def create_user(name, email, password):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (name, email, password, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, password, datetime.now().isoformat())
        )

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()

def authenticate_user(email, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, email
        FROM users
        WHERE email=? AND password=?
        """,
        (email, password)
    )

    user = cursor.fetchone()
    conn.close()

    return user

def save_analysis(user_id, target_role, resume_data):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO analyses (
            user_id,
            target_role,
            ats_score,
            resume_json,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            target_role,
            resume_data.get("ats_score", 0),
            json.dumps(resume_data),
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()

def get_user_analyses(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT target_role, ats_score, created_at
        FROM analyses
        WHERE user_id=?
        ORDER BY id DESC
        """,
        (user_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    return rows