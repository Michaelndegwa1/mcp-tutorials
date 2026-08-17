"""Common constants and helper utilities for NGO jobs crawlers."""

from typing import Any, Dict

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9"
}
HTTP_TIMEOUT = 2.5


def classify_work_type(title: str, location: str, description: str) -> Dict[str, str]:
    """Determine Work Arrangement (Remote/Hybrid/Onsite) and Eligibility (International/National Only)."""
    text = f"{title} {location} {description}".lower()
    
    # 1. Work Arrangement Classification
    if any(kw in text for kw in ["remote", "home-based", "home based", "work from home", "virtual"]):
        work_arrangement = "Remote"
    elif "hybrid" in text:
        work_arrangement = "Hybrid"
    else:
        work_arrangement = "Onsite"
        
    # 2. Eligibility Classification
    national_keywords = [
        "national officer", "national professional", "no-a", "no-b", "no-c", "no-d",
        "npsa", "national consultant", "national staff", "local recruitment",
        "citizens of", "nationals only", "resident of"
    ]
    if any(kw in text for kw in national_keywords):
        eligibility = "National Only"
    else:
        eligibility = "International"
        
    # 3. Category Classification
    if any(kw in text for kw in ["developer", "software", "full-stack", "backend", "frontend", "python", "react", "fastapi", "django", "engineer"]):
        category = "Software Engineering"
    elif any(kw in text for kw in ["data analyst", "data scientist", "data specialist", "analytics", "statistics", "data engineer", "bi"]):
        category = "Data & Analytics"
    elif any(kw in text for kw in ["ict", "information technology", "information management", "systems", "database"]):
        category = "IT & Infrastructure"
    elif any(kw in text for kw in ["ai", "machine learning", "llm", "annotation"]):
        category = "AI & Machine Learning"
    else:
        category = "General"
        
    return {
        "work_arrangement": work_arrangement,
        "eligibility": eligibility,
        "category": category
    }
