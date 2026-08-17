"""Crawlers for NGO job boards & official NGO career sites (ReliefWeb, UN Jobs, Impactpool, UNICEF, ICRC, WFP, IRC)."""

import json
import logging
import re
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional
from storage import save_job, DEFAULT_DB_PATH
from utils import HEADERS, HTTP_TIMEOUT, classify_work_type
from direct_ngo_crawlers import (
    crawl_unicef_direct,
    crawl_icrc_direct,
    crawl_wfp_direct,
    crawl_irc_direct,
)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("crawlers")


def crawl_reliefweb(query: str = "", limit: int = 15) -> List[Dict[str, Any]]:
    """Crawl live jobs from official ReliefWeb RSS feed."""
    rss_url = "https://reliefweb.int/jobs/rss.xml"
    results = []
    seen_urls = set()
    
    try:
        response = requests.get(rss_url, headers=HEADERS, timeout=HTTP_TIMEOUT)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            for item in root.findall(".//item"):
                title_elem = item.find("title")
                link_elem = item.find("link")
                desc_elem = item.find("description")
                date_elem = item.find("pubDate")
                
                title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Untitled"
                job_url = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
                
                if not job_url or job_url in seen_urls:
                    continue
                seen_urls.add(job_url)
                
                desc_raw = desc_elem.text if desc_elem is not None and desc_elem.text else ""
                snippet = BeautifulSoup(desc_raw, "html.parser").get_text(strip=True)[:500] if desc_raw else title
                
                if query and not any(kw.lower() in f"{title} {snippet}".lower() for kw in query.split()):
                    continue
                    
                meta = classify_work_type(title, "International / Field", snippet)
                
                results.append({
                    "title": title,
                    "organization": "ReliefWeb Partner NGO",
                    "location": "International / Unspecified",
                    "url": job_url,
                    "source": "ReliefWeb",
                    "description": snippet,
                    "posted_date": date_elem.text[:16] if date_elem is not None and date_elem.text else "",
                    "work_arrangement": meta["work_arrangement"],
                    "eligibility": meta["eligibility"],
                    "category": meta["category"],
                    "region": "Global"
                })
                if len(results) >= limit:
                    break
    except Exception as err:
        logger.error(f"Error parsing ReliefWeb RSS: {err}")
        
    return results[:limit]


def crawl_unjobs(query: str = "", limit: int = 15) -> List[Dict[str, Any]]:
    """Crawl UN Jobs across tech and data themes."""
    search_path = f"/search/{query.replace(' ', '+')}" if query else "/themes/information-technology"
    url = f"https://unjobs.org{search_path}"
    
    results = []
    seen_urls = set()
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=HTTP_TIMEOUT)
        if response.status_code == 200:
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
                    "category": meta["category"],
                    "region": "Global"
                })
                if len(results) >= limit:
                    break
    except Exception as err:
        logger.error(f"Error crawling UN Jobs: {err}")
        
    return results[:limit]


def crawl_impactpool(query: str = "", limit: int = 15) -> List[Dict[str, Any]]:
    """Crawl Impactpool international development & NGO job listings."""
    url = "https://www.impactpool.org/jobs"
    results = []
    seen_urls = set()
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=HTTP_TIMEOUT)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            job_links = soup.find_all("a", href=True)
            
            for link in job_links:
                href = link["href"]
                if "/jobs/" in href and len(href) > 8:
                    title = link.get_text(strip=True)
                    if not title or len(title) < 4 or title.lower() in ("jobs", "view job", "apply"):
                        continue
                    full_url = href if href.startswith("http") else f"https://www.impactpool.org{href}"
                    if full_url in seen_urls:
                        continue
                    seen_urls.add(full_url)
                    
                    snippet = f"Impactpool International NGO position: {title}"
                    if query and not any(kw.lower() in f"{title} {snippet}".lower() for kw in query.split()):
                        continue
                        
                    meta = classify_work_type(title, "Global / Remote", snippet)
                    
                    results.append({
                        "title": title,
                        "organization": "Impactpool Partner NGO",
                        "location": "Global / Remote",
                        "url": full_url,
                        "source": "Impactpool",
                        "description": snippet,
                        "posted_date": "",
                        "work_arrangement": meta["work_arrangement"],
                        "eligibility": meta["eligibility"],
                        "category": meta["category"],
                        "region": "Global"
                    })
                    if len(results) >= limit:
                        break
    except Exception as err:
        logger.error(f"Error crawling Impactpool: {err}")
        
    return results[:limit]


def crawl_all_sources(
    query: str = "",
    sources: Optional[List[str]] = None,
    limit_per_source: int = 15,
    db_path: str = DEFAULT_DB_PATH
) -> Dict[str, Any]:
    """Crawl requested sources concurrently in parallel and store results into SQLite database."""
    if not sources:
        sources = ["reliefweb", "unjobs", "impactpool", "unicef", "icrc", "wfp", "irc"]
        
    normalized_sources = [s.lower().strip() for s in sources]
    all_jobs: List[Dict[str, Any]] = []
    
    crawler_map = {
        "reliefweb": lambda: crawl_reliefweb(query, limit=limit_per_source),
        "unjobs": lambda: crawl_unjobs(query, limit=limit_per_source),
        "impactpool": lambda: crawl_impactpool(query, limit=limit_per_source),
        "unicef": lambda: crawl_unicef_direct(query, limit=limit_per_source),
        "icrc": lambda: crawl_icrc_direct(query, limit=limit_per_source),
        "wfp": lambda: crawl_wfp_direct(query, limit=limit_per_source),
        "irc": lambda: crawl_irc_direct(query, limit=limit_per_source),
        "direct_ngos": lambda: (crawl_unicef_direct(query, limit=limit_per_source) +
                                crawl_icrc_direct(query, limit=limit_per_source) +
                                crawl_wfp_direct(query, limit=limit_per_source) +
                                crawl_irc_direct(query, limit=limit_per_source))
    }
    
    selected_crawlers = [crawler_map[s] for s in normalized_sources if s in crawler_map]
    if not selected_crawlers:
        selected_crawlers = [
            lambda: crawl_reliefweb(query, limit=limit_per_source),
            lambda: crawl_unjobs(query, limit=limit_per_source),
            lambda: crawl_impactpool(query, limit=limit_per_source),
        ]
    
    # Run crawlers concurrently in parallel threads
    with ThreadPoolExecutor(max_workers=len(selected_crawlers) or 1) as executor:
        futures = [executor.submit(fn) for fn in selected_crawlers]
        for future in as_completed(futures):
            try:
                jobs = future.result()
                if jobs:
                    all_jobs.extend(jobs)
            except Exception as err:
                logger.error(f"Error in parallel crawler: {err}")
                
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
