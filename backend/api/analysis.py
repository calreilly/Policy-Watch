from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from main_db_dependency import get_db
from models.database import Bill
from services.impact_agent import ImpactAgent

router = APIRouter()

@router.get("/health")
async def analysis_health():
    return {"status": "ok", "message": "Analysis engine online"}

@router.post("/impact-report/{bill_id}")
async def get_impact_report(bill_id: str, db: Session = Depends(get_db)):
    """Generate an on-demand AI impact report for a specific bill."""
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found in the intelligence cache.")
    
    agent = ImpactAgent()
    report = agent.generate_impact_report(bill.title, bill.summary or bill.latest_action_text)
    
from services.sentiment_service import SentimentService

@router.post("/sentiment/{bill_id}")
async def get_sentiment(bill_id: str, db: Session = Depends(get_db)):
    """Analyze public sentiment for a specific bill."""
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    # Extract just the number for better social searching (e.g., HR-8191)
    bill_number = bill.id.split("-", 1)[1] if "-" in bill.id else bill.id
    
    service = SentimentService()
    pulse = service.analyze_public_pulse(bill_number, bill.title)
    
    return {"status": "success", "pulse": pulse}
