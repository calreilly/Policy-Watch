"""
Federal Register API Integration Service
No API key required. Provides executive orders, agency rules, and public notices.
Docs: https://www.federalregister.gov/developers/api/v1
"""
import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FederalRegisterService:
    """Client for the Federal Register API — rules, executive orders, and notices."""

    BASE_URL = "https://www.federalregister.gov/api/v1"

    @classmethod
    def search_documents(cls, query: str, doc_type: str = None, limit: int = 10) -> list:
        """
        Search Federal Register documents.

        doc_type options: 'RULE', 'PRORULE', 'NOTICE', 'PRESDOCU' (executive orders)
        """
        params = {
            "conditions[term]": query,
            "per_page": min(limit, 20),
            "order": "relevance",
        }
        if doc_type:
            params["conditions[type][]"] = doc_type

        try:
            resp = requests.get(f"{cls.BASE_URL}/documents.json", params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for doc in data.get("results", []):
                    results.append({
                        "title": doc.get("title", ""),
                        "type": doc.get("type", ""),
                        "abstract": doc.get("abstract", ""),
                        "publication_date": doc.get("publication_date", ""),
                        "html_url": doc.get("html_url", ""),
                        "pdf_url": doc.get("pdf_url", ""),
                        "agencies": [a.get("name", "") for a in doc.get("agencies", [])],
                        "document_number": doc.get("document_number", ""),
                    })
                return results
        except Exception as e:
            logger.warning(f"Federal Register search failed: {e}")
        return []

    @classmethod
    def get_recent_executive_orders(cls, limit: int = 5) -> list:
        """Fetch the most recent Presidential documents (executive orders, memoranda)."""
        params = {
            "conditions[type][]": "PRESDOCU",
            "conditions[presidential_document_type][]": "executive_order",
            "per_page": limit,
            "order": "newest",
        }
        try:
            resp = requests.get(f"{cls.BASE_URL}/documents.json", params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for doc in data.get("results", []):
                    results.append({
                        "title": doc.get("title", ""),
                        "executive_order_number": doc.get("executive_order_number"),
                        "signing_date": doc.get("signing_date", ""),
                        "publication_date": doc.get("publication_date", ""),
                        "html_url": doc.get("html_url", ""),
                        "abstract": doc.get("abstract", ""),
                    })
                return results
        except Exception as e:
            logger.warning(f"Federal Register executive order fetch failed: {e}")
        return []

    @classmethod
    def get_recent_rules(cls, limit: int = 10) -> list:
        """Fetch recently published final rules from federal agencies."""
        week_ago = (datetime.utcnow() - timedelta(days=14)).strftime("%m/%d/%Y")
        params = {
            "conditions[type][]": "RULE",
            "conditions[publication_date][gte]": week_ago,
            "per_page": limit,
            "order": "newest",
        }
        try:
            resp = requests.get(f"{cls.BASE_URL}/documents.json", params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for doc in data.get("results", []):
                    results.append({
                        "title": doc.get("title", ""),
                        "abstract": doc.get("abstract", ""),
                        "publication_date": doc.get("publication_date", ""),
                        "html_url": doc.get("html_url", ""),
                        "agencies": [a.get("name", "") for a in doc.get("agencies", [])],
                    })
                return results
        except Exception as e:
            logger.warning(f"Federal Register rules fetch failed: {e}")
        return []
