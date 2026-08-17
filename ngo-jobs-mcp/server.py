"""FastMCP Server for NGO Jobs Crawler, 1000+ NGO Directory & Resume Matcher."""

import os
import sys
import argparse
import logging

# Suppress verbose MCP internal low-level server logs on stderr
logging.getLogger("mcp").setLevel(logging.WARNING)
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.WARNING)

# Ensure current directory is in sys.path
sys.path.insert(0, os.path.dirname(__file__))

from mcp.server.fastmcp import FastMCP
from crawlers import crawl_all_sources
from matcher import match_jobs
from mailer import send_job_digest_email
from storage import save_application as db_save_application, list_applications as db_list_applications
from ngo_directory import search_ngo_directory, get_ngo_stats

mcp = FastMCP(
    "NGO Jobs Crawler & 1000+ NGO Directory MCP",
    instructions="MCP Server for searching 1,000+ international NGOs (USA, EU, UK, Middle East, Global), crawling direct official career portals, resume profile matching, and application tracking."
)


@mcp.tool()
def list_ngos(region: str | None = None, focus_area: str | None = None, search_query: str | None = None, limit: int = 30) -> str:
    """Browse and filter the curated directory of 1,000+ international NGOs across USA, EU, UK, Middle East, and Global UN.
    
    Args:
        region: Optional region filter ('USA', 'EU', 'UK', 'Middle East', 'Global')
        focus_area: Optional thematic filter (e.g., 'Humanitarian', 'Health', 'Tech', 'Education', 'Rights')
        search_query: Search keywords for organization name or headquarters location
        limit: Max number of NGOs to return (default: 30)
    """
    results = search_ngo_directory(region=region, focus_area=focus_area, search_query=search_query, limit=limit)
    stats = get_ngo_stats()
    
    if not results:
        return f"No NGOs found matching query filters. Total directory count: {stats['total_ngos']} NGOs across regions: {stats['region_counts']}."
        
    lines = [f"🌍 NGO Directory Results ({len(results)} shown out of {stats['total_ngos']} total registered):\n"]
    for ngo in results:
        lines.append(f"• {ngo['name']} [{ngo['region']}] - HQ: {ngo['country_hq']}")
        lines.append(f"  Focus: {ngo['focus_area']}")
        lines.append(f"  Official Careers Portal: {ngo['careers_url']}")
        lines.append(f"  Overview: {ngo['description']}\n")
        
    return "\n".join(lines)


@mcp.tool()
def search_jobs(query: str = "", sources: list[str] | None = None, limit: int = 15) -> str:
    """Crawl official NGO career portals & job boards (ReliefWeb, UN Jobs, Impactpool, UNICEF, ICRC, WFP, IRC).
    
    Args:
        query: Search keywords (e.g., 'Software', 'Data Analyst', 'Python', 'Information Management')
        sources: Optional list of sources: ['reliefweb', 'unjobs', 'impactpool', 'unicef', 'icrc', 'wfp', 'irc', 'direct_ngos'] (default: all)
        limit: Number of jobs to fetch per source (default: 15)
    """
    res = crawl_all_sources(query=query, sources=sources, limit_per_source=limit)
    if res.get("status") == "success":
        return f"Successfully crawled NGO career sites for '{query}'. Fetched: {res['total_fetched']}, Saved/Updated: {res['total_saved_or_updated']} jobs."
    return f"Error crawling job boards: {res.get('error')}"


@mcp.tool()
def match_to_resume(top_n: int = 20, include_applied: bool = False, min_score: int = 30) -> str:
    """Score and rank cached NGO jobs against Michael Ndegwa's resume profile (Software Engineering, AI/ML, Data Analytics).
    
    Categorizes jobs by work arrangement (Remote / Hybrid / Onsite) and eligibility (International / National Only).
    
    Args:
        top_n: Number of top ranked jobs to return (default: 20)
        include_applied: Whether to include jobs already marked as applied/rejected (default: False)
        min_score: Minimum relevance score cutoff out of 100 (default: 30)
    """
    matches = match_jobs(top_n=top_n, include_applied=include_applied, min_score=min_score)
    if not matches:
        return "No relevant job matches found meeting the score threshold. Try running 'search_jobs' to crawl fresh NGO listings!"
        
    lines = [f"🎯 Top {len(matches)} NGO Job Matches (Ranked against Michael Ndegwa's Resume):\n"]
    
    for idx, j in enumerate(matches, 1):
        work_tag = f"[{j['work_arrangement'].upper()}]"
        elig_tag = f"[{j['eligibility'].upper()}]" if j['eligibility'] == "National Only" else "[INTERNATIONAL]"
        reg_tag = f"[{j.get('region', 'GLOBAL').upper()}]"
        
        lines.append(f"{idx}. [ID #{j['job_id']}] {j['title']} - {j['organization']}")
        lines.append(f"   Location: {j['location']} | Work Type: {work_tag} {elig_tag} {reg_tag} | Source: {j['source']}")
        lines.append(f"   Score: {j['total_score']}/100 | Fit Note: {j['fit_note']}")
        lines.append(f"   Link: {j['url']}\n")
        
    return "\n".join(lines)


@mcp.tool()
def email_job_matches(to_email: str | None = None, top_n: int = 15) -> str:
    """Send an HTML/Text email digest of top ranked NGO job matches via Gmail SMTP.
    
    Args:
        to_email: Target recipient email address (defaults to DEFAULT_RECIPIENT_EMAIL or GMAIL_USER in .env)
        top_n: Number of top ranked job matches to include in the email (default: 15)
    """
    matches = match_jobs(top_n=top_n)
    if not matches:
        return "No job matches found to email. Please run 'search_jobs' first!"
        
    res = send_job_digest_email(to_email=to_email, matched_jobs=matches)
    if res.get("status") == "success":
        return f"Email digest sent successfully to {res['recipient']} ({res['matched_count']} jobs included)."
    return f"Error sending email: {res.get('error')}"


@mcp.tool()
def save_application(job_id: int, status: str, notes: str = "") -> str:
    """Log or update application status for a specific job ID.
    
    Args:
        job_id: The job ID from search/match results
        status: Application status ('applied', 'interviewing', 'offer', 'rejected', 'saved', 'skipped')
        notes: Optional personal notes or application status comments
    """
    res = db_save_application(job_id=job_id, status=status, notes=notes)
    if res.get("status") == "success":
        return f"Updated Job #{job_id} ('{res['title']}') status to '{res['application_status']}'. Notes: '{notes}'"
    return f"Error updating application: {res.get('error')}"


@mcp.tool()
def list_applications(status: str | None = None) -> str:
    """List tracked job applications and their statuses.
    
    Args:
        status: Optional status filter ('applied', 'interviewing', 'offer', 'rejected', 'saved', 'skipped')
    """
    apps = db_list_applications(status_filter=status)
    if not apps:
        filter_msg = f" with status '{status}'" if status else ""
        return f"No tracked applications found{filter_msg}."
        
    lines = [f"📋 Tracked Job Applications ({len(apps)} entries):\n"]
    for a in apps:
        work_tag = f"[{a.get('work_arrangement', 'Onsite').upper()}]"
        lines.append(f"• [Job #{a['job_id']}] {a['title']} - {a['organization']}")
        lines.append(f"  Status: {a['status'].upper()} | Location: {a['location']} {work_tag} | Updated: {a['updated_at']}")
        if a.get("notes"):
            lines.append(f"  Notes: {a['notes']}")
        lines.append(f"  Link: {a['url']}\n")
        
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="NGO Jobs & Directory MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport mode: 'stdio' for Desktop or 'sse' for Web (default: stdio)"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host for SSE server")
    parser.add_argument("--port", type=int, default=8001, help="Port for SSE server (default: 8001)")
    args = parser.parse_args()

    if args.transport == "sse":
        print(f"Starting FastMCP NGO Jobs Server in SSE mode on http://{args.host}:{args.port}/sse ...")
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
