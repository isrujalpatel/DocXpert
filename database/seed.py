"""
seed.py — Create the database, run migrations, and insert sample test data.

Usage:
    python database/seed.py
"""

import sqlite3
import os
import uuid
from datetime import datetime, timedelta

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "docxpert.db")
MIGRATIONS_DIR = os.path.join(BASE_DIR, "database", "migrations")


def run_migrations(conn: sqlite3.Connection) -> None:
    """Execute all .sql migration files in order."""
    migration_files = sorted(
        f for f in os.listdir(MIGRATIONS_DIR) if f.endswith(".sql")
    )

    for filename in migration_files:
        filepath = os.path.join(MIGRATIONS_DIR, filename)
        print(f"  ▸ Running migration: {filename}")
        with open(filepath, "r") as f:
            conn.executescript(f.read())

    print(f"  ✓ Applied {len(migration_files)} migration(s)\n")


def seed_data(conn: sqlite3.Connection) -> None:
    """Insert sample documents and processing jobs for development."""
    cursor = conn.cursor()

    # --- Sample documents ---
    sample_docs = [
        {
            "file_id": str(uuid.uuid4()),
            "original_name": "quarterly_report.docx",
            "stored_name": f"{uuid.uuid4().hex}.docx",
            "file_type": "docx",
            "file_size_bytes": 245_760,
            "upload_path": "uploads/",
            "status": "completed",
        },
        {
            "file_id": str(uuid.uuid4()),
            "original_name": "contract_draft.pdf",
            "stored_name": f"{uuid.uuid4().hex}.pdf",
            "file_type": "pdf",
            "file_size_bytes": 1_048_576,
            "upload_path": "uploads/",
            "status": "uploaded",
        },
        {
            "file_id": str(uuid.uuid4()),
            "original_name": "meeting_notes.docx",
            "stored_name": f"{uuid.uuid4().hex}.docx",
            "file_type": "docx",
            "file_size_bytes": 52_430,
            "upload_path": "uploads/",
            "status": "processing",
        },
    ]

    for doc in sample_docs:
        cursor.execute(
            """INSERT INTO documents
               (file_id, original_name, stored_name, file_type, file_size_bytes, upload_path, status)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                doc["file_id"],
                doc["original_name"],
                doc["stored_name"],
                doc["file_type"],
                doc["file_size_bytes"],
                doc["upload_path"],
                doc["status"],
            ),
        )

    print(f"  ▸ Inserted {len(sample_docs)} sample document(s)")

    # --- Sample processing jobs ---
    now = datetime.utcnow()
    sample_jobs = [
        {
            "job_id": str(uuid.uuid4()),
            "document_id": 1,
            "job_type": "spelling",
            "status": "completed",
            "started_at": (now - timedelta(minutes=5)).isoformat(),
            "completed_at": now.isoformat(),
        },
        {
            "job_id": str(uuid.uuid4()),
            "document_id": 1,
            "job_type": "convert",
            "status": "completed",
            "started_at": (now - timedelta(minutes=3)).isoformat(),
            "completed_at": (now - timedelta(minutes=2)).isoformat(),
        },
        {
            "job_id": str(uuid.uuid4()),
            "document_id": 3,
            "job_type": "font_normalize",
            "status": "running",
            "started_at": now.isoformat(),
            "completed_at": None,
        },
    ]

    for job in sample_jobs:
        cursor.execute(
            """INSERT INTO processing_jobs
               (job_id, document_id, job_type, status, started_at, completed_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                job["job_id"],
                job["document_id"],
                job["job_type"],
                job["status"],
                job["started_at"],
                job["completed_at"],
            ),
        )

    print(f"  ▸ Inserted {len(sample_jobs)} sample job(s)")

    # --- Sample spelling suggestions ---
    cursor.execute(
        """INSERT INTO spelling_suggestions
           (job_id, document_id, original_text, suggested_text, context, position, confidence)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (1, 1, "recieve", "receive", "We will recieve the shipment on Monday.", 8, 0.95),
    )
    cursor.execute(
        """INSERT INTO spelling_suggestions
           (job_id, document_id, original_text, suggested_text, context, position, confidence)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (1, 1, "seperately", "separately", "Each item is packaged seperately.", 27, 0.92),
    )

    print("  ▸ Inserted 2 sample spelling suggestion(s)")

    # --- Sample font reports ---
    cursor.execute(
        """INSERT INTO font_reports
           (job_id, document_id, font_name, font_size, occurrences, is_target)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (3, 3, "Times New Roman", 12.0, 45, 1),
    )
    cursor.execute(
        """INSERT INTO font_reports
           (job_id, document_id, font_name, font_size, occurrences, is_target)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (3, 3, "Arial", 11.0, 8, 0),
    )
    cursor.execute(
        """INSERT INTO font_reports
           (job_id, document_id, font_name, font_size, occurrences, is_target)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (3, 3, "Calibri", 10.5, 3, 0),
    )

    print("  ▸ Inserted 3 sample font report(s)")

    conn.commit()
    print("  ✓ Seed data committed\n")


def main():
    print("\n╔══════════════════════════════════════╗")
    print("║   DocXpert — Database Setup & Seed   ║")
    print("╚══════════════════════════════════════╝\n")

    # Ensure database directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    # Remove existing DB for a clean seed
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"  ▸ Removed existing database: {DB_PATH}")

    # Connect & enable foreign keys
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    print(f"  ▸ Created new database: {DB_PATH}\n")

    # Run migrations
    print("── Migrations ──")
    run_migrations(conn)

    # Seed data
    print("── Seed Data ──")
    seed_data(conn)

    conn.close()
    print("✅ Database setup complete!\n")


if __name__ == "__main__":
    main()
