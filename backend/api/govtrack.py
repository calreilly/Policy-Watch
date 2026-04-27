from fastapi import APIRouter
from services.govtrack_service import GovTrackService

router = APIRouter()


@router.get("/bills")
def search_govtrack_bills(query: str, congress: int = 119, limit: int = 10):
    """Search GovTrack for bills by keyword."""
    results = GovTrackService.search_bills(query, congress=congress, limit=limit)
    return {"status": "success", "results": results, "count": len(results)}


@router.get("/bills/{bill_id}")
def get_govtrack_bill(bill_id: int):
    """Fetch a single bill by GovTrack numeric ID."""
    result = GovTrackService.fetch_bill_by_id(bill_id)
    return {"status": "success", "result": result}


@router.get("/votes")
def get_recent_votes(congress: int = 119, limit: int = 10):
    """Fetch recent roll-call votes."""
    results = GovTrackService.fetch_recent_votes(congress=congress, limit=limit)
    return {"status": "success", "results": results, "count": len(results)}


@router.get("/votes/{vote_id}")
def get_vote_detail(vote_id: int):
    """Fetch detailed breakdown for a single vote."""
    result = GovTrackService.fetch_vote_detail(vote_id)
    return {"status": "success", "result": result}


@router.get("/legislators")
def search_legislators(name: str = None, state: str = None, limit: int = 10):
    """Search legislators by name or state."""
    results = GovTrackService.search_legislators(name=name, state=state, limit=limit)
    return {"status": "success", "results": results, "count": len(results)}
