"""Direct Official Career Portal Crawlers for International NGOs in USA, EU, UK, Middle East & Global UN."""

import json
import logging
import requests
from bs4 import BeautifulSoup
from typing import Any, Dict, List, Optional
from utils import HEADERS, HTTP_TIMEOUT, classify_work_type

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("direct_crawlers")


def crawl_unicef_direct(query: str = "", limit: int = 15) -> List[Dict[str, Any]]:
    """Crawl official UNICEF careers portal (jobs.unicef.org)."""
    url = f"https://jobs.unicef.org/en-us/search/?search-keyword={query.replace(' ', '+')}" if query else "https://jobs.unicef.org/en-us/listing/"
    results = []
    seen_urls = set()
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=HTTP_TIMEOUT)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            job_items = soup.select(".job-link, .listing-item, article, a[href*='/job/']")
            
            for item in job_items:
                if item.name == "a":
                    a_tag = item
                else:
                    a_tag = item.find("a")
                    
                if not a_tag or not a_tag.get("href"):
                    continue
                href = a_tag.get("href", "")
                if "/job/" not in href and "/en-us/job/" not in href:
                    continue
                full_url = href if href.startswith("http") else f"https://jobs.unicef.org{href}"
                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)
                
                title = a_tag.get_text(strip=True)
                if not title or len(title) < 4:
                    continue
                    
                snippet = f"UNICEF Official Career Opportunity: {title}"
                meta = classify_work_type(title, "Global / Field", snippet)
                
                results.append({
                    "title": title,
                    "organization": "UNICEF",
                    "location": "Global / UN Field",
                    "url": full_url,
                    "source": "UNICEF Careers (Official)",
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
        logger.error(f"Error crawling UNICEF direct careers: {err}")
        
    return results[:limit]


def crawl_icrc_direct(query: str = "", limit: int = 15) -> List[Dict[str, Any]]:
    """Crawl official ICRC Red Cross careers portal (careers.icrc.org)."""
    url = f"https://careers.icrc.org/search/?q={query.replace(' ', '+')}" if query else "https://careers.icrc.org/search/"
    results = []
    seen_urls = set()
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=HTTP_TIMEOUT)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", href=True)
            
            for link in links:
                href = link["href"]
                if "/job/" in href:
                    title = link.get_text(strip=True)
                    if len(title) > 4:
                        full_url = href if href.startswith("http") else f"https://careers.icrc.org{href}"
                        if full_url in seen_urls:
                            continue
                        seen_urls.add(full_url)
                        
                        snippet = f"ICRC Red Cross Official Vacancy: {title}"
                        meta = classify_work_type(title, "Geneva / Field", snippet)
                        
                        results.append({
                            "title": title,
                            "organization": "ICRC (Red Cross)",
                            "location": "Geneva / Field",
                            "url": full_url,
                            "source": "ICRC Careers (Official)",
                            "description": snippet,
                            "posted_date": "",
                            "work_arrangement": meta["work_arrangement"],
                            "eligibility": meta["eligibility"],
                            "category": meta["category"],
                            "region": "EU"
                        })
                        if len(results) >= limit:
                            break
    except Exception as err:
        logger.error(f"Error crawling ICRC direct careers: {err}")
        
    return results[:limit]


def crawl_wfp_direct(query: str = "", limit: int = 15) -> List[Dict[str, Any]]:
    """Crawl official WFP World Food Programme careers (worldfoodprogramme.careers)."""
    url = f"https://worldfoodprogramme.careers/search/?q={query.replace(' ', '+')}" if query else "https://worldfoodprogramme.careers/search/"
    results = []
    seen_urls = set()
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=HTTP_TIMEOUT)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", href=True)
            
            for link in links:
                href = link["href"]
                if "/job/" in href:
                    title = link.get_text(strip=True)
                    if len(title) > 4:
                        full_url = href if href.startswith("http") else f"https://worldfoodprogramme.careers{href}"
                        if full_url in seen_urls:
                            continue
                        seen_urls.add(full_url)
                        
                        snippet = f"WFP World Food Programme Official Opening: {title}"
                        meta = classify_work_type(title, "Global / Field", snippet)
                        
                        results.append({
                            "title": title,
                            "organization": "WFP (World Food Programme)",
                            "location": "Global / Field",
                            "url": full_url,
                            "source": "WFP Careers (Official)",
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
        logger.error(f"Error crawling WFP direct careers: {err}")
        
    return results[:limit]


def crawl_irc_direct(query: str = "", limit: int = 15) -> List[Dict[str, Any]]:
    """Crawl official IRC International Rescue Committee careers (rescue.org/careers)."""
    url = "https://www.rescue.org/careers"
    results = []
    seen_urls = set()
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=HTTP_TIMEOUT)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a", href=True)
            
            for link in links:
                href = link["href"]
                if "careers" in href or "job" in href:
                    title = link.get_text(strip=True)
                    if len(title) > 5 and title.lower() not in ("careers", "view all jobs"):
                        full_url = href if href.startswith("http") else f"https://www.rescue.org{href}"
                        if full_url in seen_urls:
                            continue
                        seen_urls.add(full_url)
                        
                        snippet = f"International Rescue Committee (IRC) Official Job: {title}"
                        meta = classify_work_type(title, "USA / Global", snippet)
                        
                        results.append({
                            "title": title,
                            "organization": "International Rescue Committee (IRC)",
                            "location": "USA / Global",
                            "url": full_url,
                            "source": "IRC Careers (Official)",
                            "description": snippet,
                            "posted_date": "",
                            "work_arrangement": meta["work_arrangement"],
                            "eligibility": meta["eligibility"],
                            "category": meta["category"],
                            "region": "USA"
                        })
                        if len(results) >= limit:
                            break
    except Exception as err:
        logger.error(f"Error crawling IRC direct careers: {err}")
        
    return results[:limit]
