"""
GovTrack API Integration Service
Provides legislative intelligence: bill prognosis, vote records, and legislator profiles.
Uses the govtrack Python library.
"""
import requests
import logging

logger = logging.getLogger(__name__)


class GovTrackService:
    """Client for the GovTrack.us API — legislative data, votes, and member profiles."""

    BASE_URL = "https://www.govtrack.us/api/v2"

    # ── Bills ────────────────────────────────────────────────────────────
    @classmethod
    def search_bills(cls, query: str, congress: int = 119, limit: int = 10) -> list:
        """Search GovTrack bills by keyword."""
        try:
            resp = requests.get(
                f"{cls.BASE_URL}/bill",
                params={"q": query, "congress": congress, "limit": limit},
                timeout=10,
            )
            if resp.status_code == 200:
                return resp.json().get("objects", [])
        except Exception as e:
            logger.warning(f"GovTrack bill search failed: {e}")
        return []

    @classmethod
    def fetch_bill_by_id(cls, bill_id: int) -> dict:
        """Fetch a single bill by its GovTrack numeric ID."""
        try:
            resp = requests.get(f"{cls.BASE_URL}/bill/{bill_id}", timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            logger.warning(f"GovTrack fetch bill {bill_id} failed: {e}")
        return {}

    # ── Votes ────────────────────────────────────────────────────────────
    @classmethod
    def fetch_recent_votes(cls, congress: int = 119, limit: int = 10) -> list:
        """Fetch recent roll-call votes from the current Congress."""
        try:
            resp = requests.get(
                f"{cls.BASE_URL}/vote",
                params={
                    "congress": congress,
                    "limit": limit,
                    "sort": "-created",
                },
                timeout=10,
            )
            if resp.status_code == 200:
                return resp.json().get("objects", [])
        except Exception as e:
            logger.warning(f"GovTrack vote fetch failed: {e}")
        return []

    @classmethod
    def fetch_vote_detail(cls, vote_id: int) -> dict:
        """Fetch detailed breakdown for a single vote."""
        try:
            resp = requests.get(f"{cls.BASE_URL}/vote/{vote_id}", timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            logger.warning(f"GovTrack vote detail {vote_id} failed: {e}")
        return {}

    # ── Legislators ──────────────────────────────────────────────────────
    @classmethod
    def search_legislators(cls, name: str = None, state: str = None, limit: int = 10) -> list:
        """Search current legislators by name or state."""
        params = {"limit": limit, "current": True}
        if name:
            params["lastname"] = name
        if state:
            params["state"] = state
        try:
            resp = requests.get(f"{cls.BASE_URL}/person", params=params, timeout=10)
            if resp.status_code == 200:
                return resp.json().get("objects", [])
        except Exception as e:
            logger.warning(f"GovTrack legislator search failed: {e}")
        return []

    @classmethod
    def fetch_legislator(cls, person_id: int) -> dict:
        """Fetch a single legislator's profile."""
        try:
            resp = requests.get(f"{cls.BASE_URL}/person/{person_id}", timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            logger.warning(f"GovTrack person {person_id} failed: {e}")
        return {}
