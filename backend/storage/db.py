import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
from domain.enums import CaseStatus

DB_PATH = Path(__file__).resolve().parent / "medical.db"


def get_connection():
    return sqlite3.connect(str(DB_PATH), check_same_thread=False)


def normalize_symptoms(symptoms: str) -> str:
    parts = [s.strip().lower() for s in symptoms.split(",") if s.strip()]
    parts = sorted(set(parts))
    return ", ".join(parts)


def _ensure_column(cursor, table: str, column: str, col_def: str):
    cursor.execute(f"PRAGMA table_info({table})")
    cols = {row[1] for row in cursor.fetchall()}
    if column not in cols:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            symptoms TEXT NOT NULL,
            status TEXT NOT NULL,
            predicted_disease TEXT,
            predictions_json TEXT,
            confidence REAL,
            decision TEXT,
            created_at TEXT NOT NULL
        )
    """)

    _ensure_column(cursor, "medical_cases", "predicted_disease", "TEXT")
    _ensure_column(cursor, "medical_cases", "predictions_json", "TEXT")
    _ensure_column(cursor, "medical_cases", "confidence", "REAL")
    _ensure_column(cursor, "medical_cases", "decision", "TEXT")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id INTEGER NOT NULL,
        disease TEXT NOT NULL,
        symptoms TEXT NOT NULL,
        accepted INTEGER NOT NULL,
        created_at TEXT NOT NULL
    )
    """)

    _ensure_column(cursor, "feedback", "disease", "TEXT")

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
        INSERT INTO medical_cases (age, gender, symptoms, status, created_at)
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
        SELECT id, age, gender, symptoms, status
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
    decision: str,
    predictions=None
):
    conn = get_connection()
    cursor = conn.cursor()

    predictions_json = json.dumps(predictions, ensure_ascii=False) if predictions is not None else None

    cursor.execute("""
        UPDATE medical_cases
        SET
            status = ?,
            predicted_disease = ?,
            confidence = ?,
            decision = ?,
            predictions_json = ?
        WHERE id = ?
    """, (
        CaseStatus.DIAGNOSED.name,
        disease,
        confidence,
        decision,
        predictions_json,
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
            decision,
            predictions_json
        FROM medical_cases
        WHERE id = ?
    """, (case_id,))

    row = cursor.fetchone()
    conn.close()
    return row


# -------------------------------------------------
# FEEDBACK
# -------------------------------------------------

def insert_feedback(case_id: int, disease: str, accepted: bool):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT symptoms FROM medical_cases WHERE id = ?", (case_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError("Case not found")

    normalized_symptoms = normalize_symptoms(row[0])

    cursor.execute("""
        INSERT INTO feedback (case_id, disease, symptoms, accepted, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        case_id,
        disease.strip(),
        normalized_symptoms,
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
            SUM(CASE WHEN f.accepted = 1 THEN 1 ELSE 0 END),
            SUM(CASE WHEN f.accepted = 0 THEN 1 ELSE 0 END)
        FROM feedback f
        JOIN medical_cases c ON c.id = f.case_id
        WHERE LOWER(c.symptoms) = LOWER(?)
    """, (symptoms,))

    row = cursor.fetchone()
    conn.close()

    accepted = row[0] or 0
    rejected = row[1] or 0
    return accepted, rejected


def feedback_stats_for_symptoms_and_disease(symptoms: str, disease: str):
    conn = get_connection()
    cursor = conn.cursor()

    normalized_symptoms = normalize_symptoms(symptoms)

    cursor.execute("""
        SELECT
            SUM(CASE WHEN accepted = 1 THEN 1 ELSE 0 END),
            SUM(CASE WHEN accepted = 0 THEN 1 ELSE 0 END)
        FROM feedback
        WHERE symptoms = ?
          AND LOWER(disease) = LOWER(?)
    """, (normalized_symptoms, disease))

    row = cursor.fetchone()
    conn.close()

    accepted = row[0] or 0
    rejected = row[1] or 0
    return accepted, rejected

