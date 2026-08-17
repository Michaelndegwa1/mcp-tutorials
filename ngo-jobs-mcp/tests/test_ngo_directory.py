"""Automated tests for 1,000+ Global NGO Directory lookup engine."""

import pytest
from ngo_directory import search_ngo_directory, get_ngo_stats


def test_ngo_directory_stats():
    stats = get_ngo_stats()
    assert stats["total_ngos"] >= 25
    assert "USA" in stats["region_counts"]
    assert "EU" in stats["region_counts"]
    assert "UK" in stats["region_counts"]
    assert "Middle East" in stats["region_counts"]
    assert "Global" in stats["region_counts"]


def test_ngo_directory_region_filters():
    usa_ngos = search_ngo_directory(region="USA")
    assert len(usa_ngos) > 0
    assert any("IRC" in ngo["name"] or "Rescue" in ngo["name"] for ngo in usa_ngos)

    me_ngos = search_ngo_directory(region="Middle East")
    assert len(me_ngos) > 0
    assert any("Qatar" in ngo["name"] or "KSrelief" in ngo["name"] or "Taawon" in ngo["name"] for ngo in me_ngos)

    uk_ngos = search_ngo_directory(region="UK")
    assert len(uk_ngos) > 0
    assert any("Oxfam" in ngo["name"] or "Save the Children" in ngo["name"] for ngo in uk_ngos)


def test_ngo_directory_query_search():
    res = search_ngo_directory(search_query="Red Cross")
    assert len(res) > 0
    assert any("ICRC" in ngo["name"] or "Red Cross" in ngo["name"] for ngo in res)
