"""Resume matching and job ranking engine tailored to Michael Ndegwa's profile."""

import json
import os
import re
from typing import Any, Dict, List, Optional
from storage import get_jobs, DEFAULT_DB_PATH

DEFAULT_PROFILE_PATH = os.path.join(os.path.dirname(__file__), "resume_profile.json")


def load_resume_profile(profile_path: str = DEFAULT_PROFILE_PATH) -> Dict[str, Any]:
    """Load candidate resume profile JSON."""
    if not os.path.exists(profile_path):
        return {
            "name": "Michael Ndegwa",
            "target_titles": ["Software Engineer", "Full-Stack Developer", "Backend Developer", "Data Analyst", "AI Evaluator", "ICT Specialist"],
            "core_skills": ["python", "django", "fastapi", "react", "typescript", "node.js", "flutter", "ai evaluation", "mcp", "data analysis", "sql"],
            "preferred_locations": ["Nairobi", "Kenya", "Remote", "Worldwide", "Global"],
            "allow_remote": True,
            "min_fit_score": 30
        }
    with open(profile_path, "r", encoding="utf-8") as f:
        return json.load(f)


def score_job(job: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate match score (0 to 100) and generate a fit explanation."""
    title = job.get("title", "").lower()
    description = job.get("description", "").lower()
    location = job.get("location", "").lower()
    combined_text = f"{title} {description} {location}"
    
    target_titles = [t.lower() for t in profile.get("target_titles", [])]
    core_skills = [s.lower() for s in profile.get("core_skills", [])]
    preferred_locs = [l.lower() for l in profile.get("preferred_locations", [])]
    
    # 1. Title Match Score (0 - 45 points)
    title_score = 0
    matched_title = ""
    for t_title in target_titles:
        if t_title in title:
            title_score = 45
            matched_title = t_title
            break
        # Partial word match
        words = [w for w in t_title.split() if len(w) > 3]
        if any(w in title for w in words):
            title_score = max(title_score, 25)
            matched_title = t_title
            
    # 2. Skill Match Score (0 - 40 points)
    matched_skills = []
    for skill in core_skills:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, combined_text):
            matched_skills.append(skill)
            
    skill_score = min(40, len(matched_skills) * 10)
    
    # Negative penalty for completely unrelated non-tech roles (Finance, Logistics, Security, Nurse, Driver)
    irrelevant_keywords = ["finance manager", "payroll", "security officer", "logistics admin", "nurse", "driver", "procurement officer"]
    if any(ik in title for ik in irrelevant_keywords) and not matched_skills:
        title_score = 0
        skill_score = 0
        
    # 3. Location & Remote Score (0 - 15 points)
    location_score = 0
    work_arrangement = job.get("work_arrangement", "Onsite")
    eligibility = job.get("eligibility", "International")
    
    if work_arrangement == "Remote" or any(kw in location or kw in title for kw in ["remote", "worldwide", "global"]):
        location_score = 15
    elif any(loc in location for loc in preferred_locs):
        location_score = 15
    elif "unspecified" in location or "international" in location:
        location_score = 10
        
    total_score = title_score + skill_score + location_score
    
    # Generate 1-line fit summary note
    reasons = []
    if matched_title:
        reasons.append(f"Target Title: '{matched_title.title()}'")
    if matched_skills:
        reasons.append(f"Skills: {', '.join(matched_skills[:4])}")
    if work_arrangement == "Remote":
        reasons.append("Remote position")
    elif location_score > 0:
        reasons.append(f"Location: {job.get('location')}")
    if eligibility == "National Only":
        reasons.append("⚠️ National/Local Candidates Only")
        
    fit_note = " | ".join(reasons) if reasons else "General non-profit match"
    
    return {
        "job_id": job.get("id"),
        "title": job.get("title"),
        "organization": job.get("organization"),
        "location": job.get("location"),
        "url": job.get("url"),
        "source": job.get("source"),
        "work_arrangement": work_arrangement,
        "eligibility": eligibility,
        "category": job.get("category", "General"),
        "total_score": total_score,
        "title_score": title_score,
        "skill_score": skill_score,
        "location_score": location_score,
        "matched_skills": matched_skills,
        "fit_note": fit_note,
        "application_status": job.get("application_status")
    }


def match_jobs(
    top_n: int = 20,
    profile_path: str = DEFAULT_PROFILE_PATH,
    db_path: str = DEFAULT_DB_PATH,
    include_applied: bool = False,
    min_score: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Rank cached jobs in database against candidate resume profile."""
    profile = load_resume_profile(profile_path)
    score_cutoff = min_score if min_score is not None else profile.get("min_fit_score", 30)
    jobs = get_jobs(limit=500, db_path=db_path)
    
    scored_jobs = []
    for j in jobs:
        # Skip if candidate already applied/rejected unless requested
        app_status = j.get("application_status")
        if not include_applied and app_status in ("applied", "rejected", "skipped"):
            continue
            
        scored = score_job(j, profile)
        if scored["total_score"] >= score_cutoff:
            scored_jobs.append(scored)
            
    # Sort by total score descending
    scored_jobs.sort(key=lambda x: x["total_score"], reverse=True)
    return scored_jobs[:top_n]
