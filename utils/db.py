import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd

# database.db isn't downloaded from anywhere — this app creates it itself.
# This just decides where it lives: a file named database.db at the project root.
DB_PATH = Path(__file__).resolve().parent.parent / "database.db"

HIGH_RISK_LABELS = {"High Risk", "Demented", "Converted"}
LOW_RISK_LABELS = {"Low Risk", "Nondemented"}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    gender TEXT,
    age INTEGER,
    phone TEXT,
    email TEXT,
    address TEXT,
    emergency_contact TEXT,
    registration_date TEXT,
    assessment_type TEXT,
    education_years INTEGER,
    diabetes INTEGER,
    hypertension INTEGER,
    high_cholesterol INTEGER,
    smoking INTEGER,
    ef REAL,
    ps REAL,
    global_cognitive REAL,
    fazekas INTEGER,
    lacune_count INTEGER,
    mmse REAL,
    etiv REAL,
    nwbv REAL,
    asf REAL,
    prediction_label TEXT,
    confidence REAL
)
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    # Creates the "patients" table if it doesn't exist yet; does nothing if it already does.
    conn = get_connection()
    conn.execute(_SCHEMA)
    conn.commit()
    conn.close()


def insert_patient(data: dict) -> int:
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO patients
           (full_name, gender, age, phone, email, address, emergency_contact, registration_date)
           VALUES (:full_name, :gender, :age, :phone, :email, :address, :emergency_contact, :registration_date)""",
        {**data, "registration_date": date.today().isoformat()},
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update_assessment(patient_id: int, assessment_type: str, fields: dict, prediction_label: str, confidence: float) -> None:
    conn = get_connection()
    columns = list(fields.keys()) + ["assessment_type", "prediction_label", "confidence"]
    set_clause = ", ".join(f"{col} = :{col}" for col in columns)
    params = {**fields, "assessment_type": assessment_type, "prediction_label": prediction_label,
              "confidence": confidence, "id": patient_id}
    conn.execute(f"UPDATE patients SET {set_clause} WHERE id = :id", params)
    conn.commit()
    conn.close()


def fetch_all_patients() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM patients", conn)
    conn.close()
    return df


def get_patient(patient_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def search_patients(query: str = "", risk_filter: str = "All") -> pd.DataFrame:
    df = fetch_all_patients()
    if query:
        q = query.strip().lower()
        mask = df["full_name"].str.lower().str.contains(q, na=False) | df["id"].astype(str).str.contains(q)
        df = df[mask]
    if risk_filter == "High Risk":
        df = df[df["prediction_label"].isin(HIGH_RISK_LABELS)]
    elif risk_filter == "Low Risk":
        df = df[df["prediction_label"].isin(LOW_RISK_LABELS)]
    elif risk_filter == "Pending":
        df = df[df["prediction_label"].isna()]
    return df


def delete_patient(patient_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    conn.commit()
    conn.close()


def display_id(patient_id: int) -> str:
    return f"P{patient_id:04d}"
