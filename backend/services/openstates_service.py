"""
OpenStates API Integration Service
Provides state-level legislative data: bills, legislators, and committee information.
Uses the v3 GraphQL API at https://v3.openstates.org/graphql
"""
import os
import requests
import logging

logger = logging.getLogger(__name__)


class OpenStatesService:
    """Client for the Open States GraphQL API — state-level legislation tracking."""

    GRAPHQL_URL = "https://v3.openstates.org/graphql"
    API_KEY = os.environ.get("OPENSTATES_API_KEY", "")

    @classmethod
    def _headers(cls):
        return {
            "X-API-KEY": cls.API_KEY,
            "Content-Type": "application/json",
        }

    @classmethod
    def search_state_bills(cls, query: str, state: str = None, limit: int = 10) -> list:
        """Search state-level bills via GraphQL."""
        state_filter = f', jurisdiction: "{state}"' if state else ""
        gql = f"""
        {{
          bills(searchQuery: "{query}"{state_filter}, first: {limit}, sort: "UPDATED_DESC") {{
            edges {{
              node {{
                id
                identifier
                title
                classification
                updatedAt
                openstatesUrl
                legislativeSession {{
                  identifier
                  jurisdiction {{
                    name
                  }}
                }}
                abstracts {{
                  abstract
                }}
                sponsorships {{
                  name
                  entityType
                  primary
                }}
              }}
            }}
          }}
        }}
        """
        try:
            resp = requests.post(
                cls.GRAPHQL_URL,
                json={"query": gql},
                headers=cls._headers(),
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                edges = data.get("data", {}).get("bills", {}).get("edges", [])
                results = []
                for edge in edges:
                    node = edge.get("node", {})
                    jurisdiction = (
                        node.get("legislativeSession", {})
                        .get("jurisdiction", {})
                        .get("name", "")
                    )
                    session = (
                        node.get("legislativeSession", {}).get("identifier", "")
                    )
                    abstracts = node.get("abstracts", [])
                    summary = abstracts[0].get("abstract", "") if abstracts else ""
                    sponsors = [
                        {
                            "name": s.get("name", ""),
                            "primary": s.get("primary", False),
                        }
                        for s in node.get("sponsorships", [])[:5]
                    ]
                    results.append({
                        "id": node.get("identifier", ""),
                        "title": node.get("title", ""),
                        "classification": node.get("classification", []),
                        "jurisdiction": jurisdiction,
                        "session": session,
                        "updated_at": node.get("updatedAt", ""),
                        "url": node.get("openstatesUrl", ""),
                        "summary": summary[:500] if summary else "",
                        "sponsors": sponsors,
                    })
                return results
            else:
                logger.warning(f"OpenStates returned {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            logger.warning(f"OpenStates search failed: {e}")
        return []

    @classmethod
    def get_state_legislators(cls, state: str, limit: int = 10) -> list:
        """Fetch current legislators for a given state."""
        gql = f"""
        {{
          people(memberOf: "{state}", first: {limit}) {{
            edges {{
              node {{
                id
                name
                party
                currentMemberships {{
                  organization {{
                    name
                    classification
                  }}
                  role
                }}
                openstatesUrl
              }}
            }}
          }}
        }}
        """
        try:
            resp = requests.post(
                cls.GRAPHQL_URL,
                json={"query": gql},
                headers=cls._headers(),
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                edges = data.get("data", {}).get("people", {}).get("edges", [])
                return [
                    {
                        "name": e["node"].get("name", ""),
                        "party": e["node"].get("party", ""),
                        "url": e["node"].get("openstatesUrl", ""),
                        "memberships": [
                            {
                                "org": m.get("organization", {}).get("name", ""),
                                "role": m.get("role", ""),
                            }
                            for m in e["node"].get("currentMemberships", [])[:3]
                        ],
                    }
                    for e in edges
                ]
        except Exception as e:
            logger.warning(f"OpenStates legislator fetch failed: {e}")
        return []
