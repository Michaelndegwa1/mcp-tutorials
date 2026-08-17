"""Global NGO Directory Lookup Engine (USA, EU, UK, Middle East, Global)."""

import json
import os
from typing import Any, Dict, List, Optional

DIRECTORY_FILE = os.path.join(os.path.dirname(__file__), "ngo_directory.json")


def load_ngo_directory() -> List[Dict[str, Any]]:
    """Load curated directory of international NGOs."""
    if not os.path.exists(DIRECTORY_FILE):
        return []
    with open(DIRECTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def search_ngo_directory(
    region: Optional[str] = None,
    focus_area: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Search and filter directory of international NGOs across USA, EU, UK, Middle East, and Global UN."""
    directory = load_ngo_directory()
    results = []
    
    reg_filter = region.upper().strip() if region else None
    focus_filter = focus_area.lower().strip() if focus_area else None
    query_filter = search_query.lower().strip() if search_query else None
    
    for ngo in directory:
        # 1. Region Filter (USA, EU, UK, Middle East, Global)
        if reg_filter:
            ngo_reg = ngo.get("region", "").upper()
            if reg_filter not in ngo_reg and ngo_reg not in reg_filter:
                continue
                
        # 2. Focus Area Filter
        if focus_filter:
            ngo_focus = ngo.get("focus_area", "").lower()
            if focus_filter not in ngo_focus:
                continue
                
        # 3. Query Text Search
        if query_filter:
            combined = f"{ngo.get('name')} {ngo.get('country_hq')} {ngo.get('focus_area')} {ngo.get('description')}".lower()
            if not any(q in combined for q in query_filter.split()):
                continue
                
        results.append(ngo)
        if len(results) >= limit:
            break
            
    return results


def get_ngo_stats() -> Dict[str, Any]:
    """Get region count summary of NGO directory."""
    directory = load_ngo_directory()
    counts: Dict[str, int] = {}
    for ngo in directory:
        reg = ngo.get("region", "Other")
        counts[reg] = counts.get(reg, 0) + 1
        
    return {
        "total_ngos": len(directory),
        "region_counts": counts
    }
