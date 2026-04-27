from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from main_db_dependency import get_db
from models.database import Bill
from models.schemas import CompareRequest, CompareResponse
from services.impact_analyzer import ImpactAnalyzer
from services.agent_service import AgentService
from services.congress_service import CongressService
from services.rag_service import RAGService

router = APIRouter()

# Instantiate services (or use dependency injection if preferred)
congress_service = CongressService()
rag_service = RAGService()
agent_service = AgentService(congress_service, rag_service)
impact_analyzer = ImpactAnalyzer(agent_service)

@router.post("/compare-bills", response_model=CompareResponse)
def compare_bills(request: CompareRequest, db: Session = Depends(get_db)):
    """
    Side-by-side comparison of multiple bills using LLM impact assessment.
    """
    if not request.bill_ids:
        raise HTTPException(status_code=400, detail="No bill IDs provided")

    comparisons = {}
    for bill_id in request.bill_ids:
        bill = db.query(Bill).filter(Bill.id == bill_id).first()
        if not bill:
            comparisons[bill_id] = {"error": "Bill not found"}
            continue
        
        # Get impact analysis
        impact = impact_analyzer.analyze_impact(bill.id, bill.title, bill.summary or "No summary available.")
        
        comparisons[bill_id] = {
            "title": bill.title,
            "status": bill.status,
            "impact": impact
        }
    
    return CompareResponse(comparisons=comparisons)
