"""Automated unit tests for NGO Jobs MCP module."""

import os
import tempfile
import pytest
from storage import init_db, save_job, get_jobs, save_application, list_applications
from crawlers import crawl_reliefweb
from matcher import load_resume_profile, score_job, match_jobs


@pytest.fixture
def test_db():
    """Create a temporary test database file for each test."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_ngo_jobs.db")
    init_db(db_path)
    yield db_path
    # Cleanup after test closes handles
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)
    except Exception:
        pass


def test_storage_operations(test_db):
    job_sample = {
        "title": "Program Officer - Emergency Response",
        "organization": "Red Cross",
        "location": "Geneva",
        "source": "ReliefWeb",
        "url": "https://reliefweb.int/job/12345",
        "description": "Managing emergency response and proposal writing for humanitarian aid.",
        "posted_date": "2026-08-17"
    }
    
    res = save_job(job_sample, db_path=test_db)
    assert res["status"] == "saved"
    assert res["job_id"] is not None

    jobs = get_jobs(db_path=test_db)
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Program Officer - Emergency Response"

    # Application tracking test
    app_res = save_application(res["job_id"], "applied", notes="Submitted via portal", db_path=test_db)
    assert app_res["status"] == "success"

    apps = list_applications(db_path=test_db)
    assert len(apps) == 1
    assert apps[0]["status"] == "applied"


def test_reliefweb_crawler():
    results = crawl_reliefweb(query="humanitarian", limit=3)
    assert isinstance(results, list)
    if results:
        assert "title" in results[0]
        assert "url" in results[0]
        assert "source" in results[0]


def test_matcher_scoring():
    profile = {
        "target_titles": ["Program Officer"],
        "core_skills": ["emergency response", "proposal writing"],
        "preferred_locations": ["Geneva", "Remote"],
        "allow_remote": True
    }
    job = {
        "id": 1,
        "title": "Program Officer - Emergency Response",
        "organization": "Red Cross",
        "location": "Geneva",
        "url": "https://reliefweb.int/job/12345",
        "description": "Managing emergency response and proposal writing.",
        "source": "ReliefWeb"
    }
    
    scored = score_job(job, profile)
    assert scored["total_score"] > 60
    assert "Program Officer" in scored["fit_note"] or "Emergency Response" in scored["fit_note"]
