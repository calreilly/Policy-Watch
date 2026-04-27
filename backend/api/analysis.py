import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from main_db_dependency import get_db
from models.database import Bill
from services.impact_agent import ImpactAgent

router = APIRouter()

# Simple TTL In-Memory Cache (Bill ID -> {type -> {result, expiry}})
ANALYSIS_CACHE = {}
CACHE_TTL = 3600 # 1 hour

def get_cached(bill_id, analysis_type):
    now = time.time()
    if bill_id in ANALYSIS_CACHE and analysis_type in ANALYSIS_CACHE[bill_id]:
        entry = ANALYSIS_CACHE[bill_id][analysis_type]
        if now < entry['expiry']:
            return entry['data']
    return None

def set_cached(bill_id, analysis_type, data):
    if bill_id not in ANALYSIS_CACHE:
        ANALYSIS_CACHE[bill_id] = {}
    ANALYSIS_CACHE[bill_id][analysis_type] = {
        'data': data,
        'expiry': time.time() + CACHE_TTL
    }

@router.get("/health")
async def analysis_health():
    return {"status": "ok", "message": "Analysis engine online"}

@router.post("/impact-report/{bill_id}")
async def get_impact_report(bill_id: str, db: Session = Depends(get_db)):
    """Generate an on-demand AI impact report for a specific bill."""
    cached = get_cached(bill_id, "impact")
    if cached: return {"status": "success", "report": cached}

    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found in the intelligence cache.")
    
    agent = ImpactAgent()
    report = agent.generate_impact_report(bill.title, bill.summary or bill.latest_action_text)
    
    set_cached(bill_id, "impact", report)
    return {"status": "success", "report": report}

from services.sentiment_service import SentimentService

@router.post("/sentiment/{bill_id}")
async def get_sentiment(bill_id: str, db: Session = Depends(get_db)):
    """Analyze public sentiment for a specific bill."""
    cached = get_cached(bill_id, "sentiment")
    if cached: return {"status": "success", "pulse": cached}

    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    bill_number = bill.id.split("-", 1)[1] if "-" in bill.id else bill.id
    
    service = SentimentService()
    pulse = service.analyze_public_pulse(bill_number, bill.title)
    
    set_cached(bill_id, "sentiment", pulse)
    return {"status": "success", "pulse": pulse}

@router.post("/global-alignment/{bill_id}")
async def get_global_alignment(bill_id: str, db: Session = Depends(get_db)):
    """Compare a bill's alignment with international policy standards."""
    cached = get_cached(bill_id, "alignment")
    if cached: return {"status": "success", "alignment": cached}

    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
        
    from services.rag_service import RAGService
    rag = RAGService()
    text = f"{bill.title} {bill.summary}"
    alignment = rag.compare_against_global(text)
    
    set_cached(bill_id, "alignment", alignment)
    return {"status": "success", "alignment": alignment}

@router.post("/lobbying/{bill_id}")
async def get_lobbying_influence(bill_id: str, db: Session = Depends(get_db)):
    """Analyze the industry/lobbying influence on the bill's sponsors."""
    cached = get_cached(bill_id, "lobbying")
    if cached: return {"status": "success", "influence": cached}

    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
        
    lead_sponsor = next((s for s in bill.sponsors if s.is_lead), None)
    if not lead_sponsor:
        return {"status": "error", "message": "No lead sponsor identified"}

    from services.fec_service import FECService
    from services.lobbying_service import LobbyingService
    
    clean_name = lead_sponsor.member_name.split("[")[0].replace("Rep. ", "").replace("Sen. ", "").strip()
    cand = FECService.search_candidate(clean_name)
    
    if not cand:
        result = LobbyingService.get_mock_influence("UNKNOWN")
        set_cached(bill_id, "lobbying", result)
        return {"status": "success", "influence": result}
        
    influence = LobbyingService.get_industry_influence(cand["candidate_id"])
    set_cached(bill_id, "lobbying", influence)
    return {"status": "success", "influence": influence}

@router.post("/prognosis/{bill_id}")
async def get_passage_prognosis(bill_id: str, db: Session = Depends(get_db)):
    """Generate a predictive passage prognosis for a specific bill."""
    cached = get_cached(bill_id, "prognosis")
    if cached: return {"status": "success", "prognosis": cached}

    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
        
    from services.prediction_service import PredictionService
    
    bill_data = {
        "title": bill.title,
        "summary": bill.summary,
        "sponsors": [{"party": s.party, "is_lead": s.is_lead} for s in bill.sponsors]
    }
    
    prognosis = PredictionService.calculate_prognosis(bill_data)
    set_cached(bill_id, "prognosis", prognosis)
    return {"status": "success", "prognosis": prognosis}
