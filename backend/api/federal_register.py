from fastapi import APIRouter
from services.federal_register_service import FederalRegisterService

router = APIRouter()


@router.get("/search")
def search_federal_register(query: str, doc_type: str = None, limit: int = 10):
    """Search Federal Register documents by keyword and optional type filter."""
    results = FederalRegisterService.search_documents(query, doc_type=doc_type, limit=limit)
    return {"status": "success", "results": results, "count": len(results)}


@router.get("/executive-orders")
def get_executive_orders(limit: int = 5):
    """Fetch the most recent executive orders."""
    results = FederalRegisterService.get_recent_executive_orders(limit=limit)
    return {"status": "success", "results": results, "count": len(results)}


@router.get("/recent-rules")
def get_recent_rules(limit: int = 10):
    """Fetch recently published final rules from federal agencies."""
    results = FederalRegisterService.get_recent_rules(limit=limit)
    return {"status": "success", "results": results, "count": len(results)}
