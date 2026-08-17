"""Crawlers for NGO job boards (ReliefWeb API, UN Jobs, Devex, Idealist)."""

import json
import logging
import re
import requests
from bs4 import BeautifulSoup
from typing import Any, Dict, List, Optional
from storage import save_job, DEFAULT_DB_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crawlers")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


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


def crawl_reliefweb(query: str = "", limit: int = 25) -> List[Dict[str, Any]]:
    """Crawl jobs using the official ReliefWeb REST API targeting ICT and Data categories."""
    url = "https://api.reliefweb.int/v1/jobs?appname=ngo-jobs-mcp&preset=latest"
    
    # Use queries tailored for software engineering, data analysis, and ICT
    search_queries = [query] if query else ["software", "developer", "data analyst", "python", "ict", "information management"]
    
    results = []
    seen_urls = set()
    
    for q in search_queries:
        payload = {
            "limit": min(limit, 30),
            "fields": {
                "include": ["title", "body-html", "body", "source", "country", "date", "url"]
            }
        }
        if q:
            payload["query"] = {"value": q}
            
        try:
            response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                continue
            data = response.json()
            
            for item in data.get("data", []):
                fields = item.get("fields", {})
                job_url = fields.get("url", f"https://reliefweb.int/job/{item.get('id')}")
                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)
                
                title = fields.get("title", "Untitled Job")
                orgs = fields.get("source", [])
                org_name = orgs[0].get("name", "NGO / ReliefWeb") if orgs else "ReliefWeb Partner"
                
                countries = fields.get("country", [])
                location = ", ".join([c.get("name", "") for c in countries]) if countries else "International / Unspecified"
                
                body = fields.get("body", "") or fields.get("body-html", "")
                snippet = BeautifulSoup(body, "html.parser").get_text(strip=True)[:500] if body else ""
                date_info = fields.get("date", {}).get("created", "")
                
                meta = classify_work_type(title, location, snippet)
                
                results.append({
                    "title": title,
                    "organization": org_name,
                    "location": location,
                    "url": job_url,
                    "source": "ReliefWeb",
                    "description": snippet,
                    "posted_date": date_info[:10] if date_info else "",
                    "work_arrangement": meta["work_arrangement"],
                    "eligibility": meta["eligibility"],
                    "category": meta["category"]
                })
        except Exception as err:
            logger.error(f"Error querying ReliefWeb API for '{q}': {err}")
            
    return results[:limit]


def crawl_unjobs(query: str = "", limit: int = 25) -> List[Dict[str, Any]]:
    """Crawl UN Jobs across tech and data themes."""
    search_paths = [
        f"/search/{query.replace(' ', '+')}" if query else "/themes/information-technology",
        "/themes/data-analysis",
        "/search/software",
        "/search/developer"
    ]
    
    results = []
    seen_urls = set()
    
    for path in search_paths:
        url = f"https://unjobs.org{path}"
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            job_cards = soup.select(".job, .j-title, article, .job-item")
            
            for card in job_cards:
                a_tag = card.find("a")
                if not a_tag or not a_tag.get("href"):
                    continue
                href = a_tag.get("href", "")
                job_url = href if href.startswith("http") else f"https://unjobs.org{href}"
                if job_url in seen_urls:
                    continue
                seen_urls.add(job_url)
                
                title = a_tag.get_text(strip=True)
                org_tag = card.select_one(".org, .organization, .org-name")
                org_name = org_tag.get_text(strip=True) if org_tag else "UN System / UNJobs"
                
                loc_tag = card.select_one(".location, .duty-station")
                location = loc_tag.get_text(strip=True) if loc_tag else "Global / UN Field"
                
                snippet = f"UN Job opening for {title} - {org_name} located in {location}."
                meta = classify_work_type(title, location, snippet)
                
                results.append({
                    "title": title or "UN Technical Opening",
                    "organization": org_name,
                    "location": location,
                    "url": job_url,
                    "source": "UN Jobs",
                    "description": snippet,
                    "posted_date": "",
                    "work_arrangement": meta["work_arrangement"],
                    "eligibility": meta["eligibility"],
                    "category": meta["category"]
                })
                if len(results) >= limit:
                    break
        except Exception as err:
            logger.error(f"Error crawling UN Jobs path '{path}': {err}")
            
    return results[:limit]


def crawl_devex(query: str = "", limit: int = 15) -> List[Dict[str, Any]]:
    """Crawl Devex international development jobs."""
    search_terms = [query] if query else ["software", "data", "technology"]
    results = []
    seen_urls = set()
    
    for term in search_terms:
        url = f"https://www.devex.com/jobs/search?q={term.replace(' ', '%20')}"
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            job_links = soup.find_all("a", href=True)
            for link in job_links:
                href = link["href"]
                if "/jobs/" in href and not href.endswith("/search"):
                    title = link.get_text(strip=True)
                    if len(title) > 5:
                        full_url = href if href.startswith("http") else f"https://www.devex.com{href}"
                        if full_url in seen_urls:
                            continue
                        seen_urls.add(full_url)
                        
                        snippet = f"Devex Global Development Job: {title}"
                        meta = classify_work_type(title, "Global / Remote", snippet)
                        
                        results.append({
                            "title": title,
                            "organization": "Devex Partner Organization",
                            "location": "Global / Remote",
                            "url": full_url,
                            "source": "Devex",
                            "description": snippet,
                            "posted_date": "",
                            "work_arrangement": meta["work_arrangement"],
                            "eligibility": meta["eligibility"],
                            "category": meta["category"]
                        })
                        if len(results) >= limit:
                            break
        except Exception as err:
            logger.error(f"Error crawling Devex for '{term}': {err}")
            
    return results[:limit]


def crawl_idealist(query: str = "", limit: int = 15) -> List[Dict[str, Any]]:
    """Crawl Idealist non-profit job search results."""
    search_terms = [query] if query else ["software", "data analyst", "technology"]
    results = []
    seen_urls = set()
    
    for term in search_terms:
        url = f"https://www.idealist.org/en/jobs?q={term.replace(' ', '+')}"
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            links = soup.find_all("a", href=True)
            for link in links:
                href = link["href"]
                if "/en/job/" in href:
                    title = link.get_text(strip=True)
                    if len(title) > 3:
                        full_url = href if href.startswith("http") else f"https://www.idealist.org{href}"
                        if full_url in seen_urls:
                            continue
                        seen_urls.add(full_url)
                        
                        snippet = f"Idealist Nonprofit Opening: {title}"
                        meta = classify_work_type(title, "Remote / Worldwide", snippet)
                        
                        results.append({
                            "title": title,
                            "organization": "Nonprofit / Idealist",
                            "location": "Remote / Worldwide",
                            "url": full_url,
                            "source": "Idealist",
                            "description": snippet,
                            "posted_date": "",
                            "work_arrangement": meta["work_arrangement"],
                            "eligibility": meta["eligibility"],
                            "category": meta["category"]
                        })
                        if len(results) >= limit:
                            break
        except Exception as err:
            logger.error(f"Error crawling Idealist for '{term}': {err}")
            
    return results[:limit]


def crawl_all_sources(
    query: str = "",
    sources: Optional[List[str]] = None,
    limit_per_source: int = 25,
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """Crawl requested sources and store results into SQLite database."""
    if not sources:
        sources = ["reliefweb", "unjobs", "devex", "idealist"]
        
    normalized_sources = [s.lower().strip() for s in sources]
    all_jobs: List[Dict[str, Any]] = []
    
    if "reliefweb" in normalized_sources:
        rw_jobs = crawl_reliefweb(query, limit=limit_per_source)
        all_jobs.extend(rw_jobs)
        
    if "unjobs" in normalized_sources:
        un_jobs = crawl_unjobs(query, limit=limit_per_source)
        all_jobs.extend(un_jobs)
        
    if "devex" in normalized_sources:
        dx_jobs = crawl_devex(query, limit=limit_per_source)
        all_jobs.extend(dx_jobs)
        
    if "idealist" in normalized_sources:
        id_jobs = crawl_idealist(query, limit=limit_per_source)
        all_jobs.extend(id_jobs)
        
    saved_count = 0
    for job in all_jobs:
        res = save_job(job, db_path)
        if res.get("status") == "saved":
            saved_count += 1
            
    return {
        "status": "success",
        "query": query,
        "sources_crawled": sources,
        "total_fetched": len(all_jobs),
        "total_saved_or_updated": saved_count,
        "db_path": db_path
    }
