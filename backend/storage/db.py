import sqlite3
from datetime import datetime, timezone
from domain.enums import CaseStatus

DB_PATH = "storage/medical.db"


def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def normalize_symptoms(symptoms: str) -> str:
    return ",".join(
        sorted(s.strip().lower() for s in symptoms.split(",") if s.strip())
    )

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # -------- medical_cases --------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            symptoms TEXT NOT NULL,
            status TEXT NOT NULL,
            predicted_disease TEXT,
            confidence REAL,
            decision TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # -------- feedback --------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id INTEGER NOT NULL,
            prediction_id INTEGER,
            accepted INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# -------------------------------------------------
# CASES
# -------------------------------------------------

def insert_case(age: int, gender: str, symptoms: str):
    normalized_symptoms = normalize_symptoms(symptoms)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO medical_cases (
            age, gender, symptoms, status, created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        age,
        gender,
        normalized_symptoms,
        CaseStatus.QUEUED.name,
        datetime.now(timezone.utc).isoformat()
    ))

    case_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return case_id


def fetch_next_queued_case():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            age,
            gender,
            symptoms,
            status
        FROM medical_cases
        WHERE status = ?
        ORDER BY id
        LIMIT 1
    """, (CaseStatus.QUEUED.name,))

    row = cursor.fetchone()

    if row:
        cursor.execute("""
            UPDATE medical_cases
            SET status = ?
            WHERE id = ?
        """, (CaseStatus.PROCESSING.name, row[0]))
        conn.commit()

    conn.close()
    return row


def update_case_status(
    case_id: int,
    disease: str,
    confidence: float,
    decision: str
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE medical_cases
        SET
            status = ?,
            predicted_disease = ?,
            confidence = ?,
            decision = ?
        WHERE id = ?
    """, (
        CaseStatus.DIAGNOSED.name,
        disease,
        confidence,
        decision,
        case_id
    ))

    conn.commit()
    conn.close()


def get_case_by_id(case_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            age,
            gender,
            symptoms,
            status,
            predicted_disease,
            confidence,
            decision
        FROM medical_cases
        WHERE id = ?
    """, (case_id,))

    row = cursor.fetchone()
    conn.close()
    return row


# -------------------------------------------------
# FEEDBACK
# -------------------------------------------------

def insert_feedback(case_id: int, prediction_id: int, accepted: bool):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feedback (
            case_id, prediction_id, accepted, created_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        case_id,
        prediction_id,
        int(accepted),
        datetime.now(timezone.utc).isoformat()
    ))

    conn.commit()
    conn.close()


def count_feedback():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            SUM(CASE WHEN accepted = 1 THEN 1 ELSE 0 END),
            SUM(CASE WHEN accepted = 0 THEN 1 ELSE 0 END)
        FROM feedback
    """)

    row = cursor.fetchone()
    conn.close()

    accepted = row[0] or 0
    rejected = row[1] or 0
    return accepted, rejected


def feedback_stats_for_symptoms(symptoms: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            SUM(CASE WHEN accepted = 1 THEN 1 ELSE 0 END),
            SUM(CASE WHEN accepted = 0 THEN 1 ELSE 0 END)
        FROM feedback f
        JOIN medical_cases c ON c.id = f.case_id
        WHERE LOWER(c.symptoms) = LOWER(?)
    """, (symptoms,))  

    row = cursor.fetchone()
    conn.close()

    accepted = row[0] or 0
    rejected = row[1] or 0
    return accepted, rejected


