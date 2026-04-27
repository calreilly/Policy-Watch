from fastapi import APIRouter
from services.openstates_service import OpenStatesService

router = APIRouter()


@router.get("/search")
def search_state_bills(query: str, state: str = None, limit: int = 10):
    """Search state-level legislation via OpenStates."""
    results = OpenStatesService.search_state_bills(query, state=state, limit=limit)
    return {"status": "success", "results": results, "count": len(results)}


@router.get("/legislators")
def get_state_legislators(state: str, limit: int = 10):
    """Fetch legislators for a given state."""
    results = OpenStatesService.get_state_legislators(state, limit=limit)
    return {"status": "success", "results": results, "count": len(results)}
