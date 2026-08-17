"""SQLite Storage Manager for NGO Jobs & Applications."""

import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

DEFAULT_DB_PATH = os.getenv("DB_PATH", "ngo_jobs.db")


def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Establish connection to SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initialize database tables for jobs and application tracking."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Table for storing crawled job listings with work arrangement & eligibility columns
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            organization TEXT NOT NULL,
            location TEXT DEFAULT 'Unspecified',
            source TEXT NOT NULL,
            description TEXT DEFAULT '',
            posted_date TEXT DEFAULT '',
            work_arrangement TEXT DEFAULT 'Onsite',
            eligibility TEXT DEFAULT 'International',
            category TEXT DEFAULT 'General',
            crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Table for tracking application status per job
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER UNIQUE NOT NULL,
            status TEXT NOT NULL,
            notes TEXT DEFAULT '',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
        );
        """)
        
        conn.commit()


def save_job(job_data: Dict[str, Any], db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Insert job into SQLite storage if unique by URL, otherwise ignore duplicate."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO jobs (url, title, organization, location, source, description, posted_date, work_arrangement, eligibility, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                title = excluded.title,
                organization = excluded.organization,
                location = excluded.location,
                description = excluded.description,
                posted_date = excluded.posted_date,
                work_arrangement = excluded.work_arrangement,
                eligibility = excluded.eligibility,
                category = excluded.category;
            """, (
                job_data.get("url", "").strip(),
                job_data.get("title", "Untitled").strip(),
                job_data.get("organization", "Unknown").strip(),
                job_data.get("location", "Unspecified").strip(),
                job_data.get("source", "Unknown").strip(),
                job_data.get("description", "").strip(),
                job_data.get("posted_date", "").strip(),
                job_data.get("work_arrangement", "Onsite").strip(),
                job_data.get("eligibility", "International").strip(),
                job_data.get("category", "General").strip(),
            ))
            conn.commit()
            
            # Fetch inserted/updated job ID
            cursor.execute("SELECT id FROM jobs WHERE url = ?", (job_data.get("url", "").strip(),))
            row = cursor.fetchone()
            job_id = row["id"] if row else None
            
            return {"status": "saved", "job_id": job_id, "url": job_data.get("url")}
        except Exception as err:
            return {"status": "error", "error": str(err)}


def get_jobs(limit: int = 200, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Retrieve crawled jobs from database."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT j.id, j.url, j.title, j.organization, j.location, j.source, j.description, j.posted_date,
               j.work_arrangement, j.eligibility, j.category, j.crawled_at,
               a.status AS application_status, a.notes AS application_notes
        FROM jobs j
        LEFT JOIN applications a ON j.id = a.job_id
        ORDER BY j.id DESC
        LIMIT ?;
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def save_application(
    job_id: int, status: str, notes: str = "", db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """Save or update application status for a job ID."""
    init_db(db_path)
    valid_statuses = {"applied", "interviewing", "offer", "rejected", "saved", "skipped"}
    st = status.lower().strip()
    if st not in valid_statuses:
        return {"status": "error", "error": f"Invalid status: '{status}'. Must be one of {valid_statuses}"}
        
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, organization FROM jobs WHERE id = ?", (job_id,))
        job = cursor.fetchone()
        if not job:
            return {"status": "error", "error": f"Job ID {job_id} not found in database"}
            
        cursor.execute("""
        INSERT INTO applications (job_id, status, notes, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(job_id) DO UPDATE SET
            status = excluded.status,
            notes = excluded.notes,
            updated_at = CURRENT_TIMESTAMP;
        """, (job_id, st, notes))
        conn.commit()
        
        return {
            "status": "success",
            "job_id": job_id,
            "title": job["title"],
            "organization": job["organization"],
            "application_status": st,
            "notes": notes
        }


def list_applications(
    status_filter: Optional[str] = None, db_path: str = DEFAULT_DB_PATH
) -> List[Dict[str, Any]]:
    """List tracked job applications."""
    init_db(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        if status_filter:
            cursor.execute("""
            SELECT a.id AS application_id, a.job_id, j.title, j.organization, j.location, j.url, j.source,
                   j.work_arrangement, j.eligibility, a.status, a.notes, a.updated_at
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            WHERE LOWER(a.status) = LOWER(?)
            ORDER BY a.updated_at DESC;
            """, (status_filter,))
        else:
            cursor.execute("""
            SELECT a.id AS application_id, a.job_id, j.title, j.organization, j.location, j.url, j.source,
                   j.work_arrangement, j.eligibility, a.status, a.notes, a.updated_at
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            ORDER BY a.updated_at DESC;
            """)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
