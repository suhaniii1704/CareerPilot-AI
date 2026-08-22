import sqlite3
import json
from datetime import datetime


DB_NAME = "careerpilot.db"


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_connection():
    return sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )


# =====================================================
# INITIALIZE DATABASE
# =====================================================

def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    # -------------------------------------------------
    # USERS TABLE
    # -------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TEXT
    )
    """)

    # -------------------------------------------------
    # RESUME ANALYSES TABLE
    # -------------------------------------------------

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

    # -------------------------------------------------
    # INTERVIEW HISTORY TABLE
    # -------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        target_role TEXT,
        interview_json TEXT,
        final_report TEXT,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # -------------------------------------------------
    # JOB MATCH HISTORY TABLE
    # -------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job_matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        target_role TEXT,
        job_description TEXT,
        match_score INTEGER,
        result TEXT,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # -------------------------------------------------
    # CAREER ROADMAP HISTORY TABLE
    # -------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roadmaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        target_role TEXT,
        current_level TEXT,
        duration TEXT,
        roadmap_result TEXT,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()


# =====================================================
# USER FUNCTIONS
# =====================================================

def create_user(name, email, password):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users (
                name,
                email,
                password,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                email,
                password,
                datetime.now().isoformat()
            )
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


# =====================================================
# RESUME ANALYSIS FUNCTIONS
# =====================================================

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
        SELECT
            id,
            target_role,
            ats_score,
            created_at
        FROM analyses
        WHERE user_id=?
        ORDER BY id DESC
        """,
        (user_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_analysis_by_id(user_id, analysis_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            target_role,
            ats_score,
            resume_json,
            created_at
        FROM analyses
        WHERE id=? AND user_id=?
        """,
        (analysis_id, user_id)
    )

    row = cursor.fetchone()

    conn.close()

    return row


def delete_analysis(user_id, analysis_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM analyses
        WHERE id=? AND user_id=?
        """,
        (analysis_id, user_id)
    )

    conn.commit()
    conn.close()


# =====================================================
# INTERVIEW HISTORY FUNCTIONS
# =====================================================

def save_interview(
    user_id,
    target_role,
    interview_history,
    final_report
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO interviews (
            user_id,
            target_role,
            interview_json,
            final_report,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            user_id,
            target_role,
            json.dumps(interview_history),
            final_report,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_user_interviews(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            target_role,
            created_at
        FROM interviews
        WHERE user_id=?
        ORDER BY id DESC
        """,
        (user_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_interview_by_id(user_id, interview_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            target_role,
            interview_json,
            final_report,
            created_at
        FROM interviews
        WHERE id=? AND user_id=?
        """,
        (interview_id, user_id)
    )

    row = cursor.fetchone()

    conn.close()

    return row


def delete_interview(user_id, interview_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM interviews
        WHERE id=? AND user_id=?
        """,
        (interview_id, user_id)
    )

    conn.commit()
    conn.close()


# =====================================================
# JOB MATCH HISTORY FUNCTIONS
# =====================================================

def save_job_match(
    user_id,
    target_role,
    job_description,
    match_score,
    result
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO job_matches (
            user_id,
            target_role,
            job_description,
            match_score,
            result,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            target_role,
            job_description,
            int(match_score),
            result,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_user_job_matches(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            target_role,
            match_score,
            created_at
        FROM job_matches
        WHERE user_id=?
        ORDER BY id DESC
        """,
        (user_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_job_match_by_id(user_id, match_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            target_role,
            job_description,
            match_score,
            result,
            created_at
        FROM job_matches
        WHERE id=? AND user_id=?
        """,
        (match_id, user_id)
    )

    row = cursor.fetchone()

    conn.close()

    return row


def delete_job_match(user_id, match_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM job_matches
        WHERE id=? AND user_id=?
        """,
        (match_id, user_id)
    )

    conn.commit()
    conn.close()


# =====================================================
# CAREER ROADMAP HISTORY FUNCTIONS
# =====================================================

def save_roadmap(
    user_id,
    target_role,
    current_level,
    duration,
    roadmap_result
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO roadmaps (
            user_id,
            target_role,
            current_level,
            duration,
            roadmap_result,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            target_role,
            current_level,
            duration,
            roadmap_result,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_user_roadmaps(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            target_role,
            current_level,
            duration,
            created_at
        FROM roadmaps
        WHERE user_id=?
        ORDER BY id DESC
        """,
        (user_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_roadmap_by_id(user_id, roadmap_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            target_role,
            current_level,
            duration,
            roadmap_result,
            created_at
        FROM roadmaps
        WHERE id=? AND user_id=?
        """,
        (roadmap_id, user_id)
    )

    row = cursor.fetchone()

    conn.close()

    return row


def delete_roadmap(user_id, roadmap_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM roadmaps
        WHERE id=? AND user_id=?
        """,
        (roadmap_id, user_id)
    )

    conn.commit()
    conn.close()