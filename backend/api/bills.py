from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from models.schemas import BillListResponse, BillDetail
from models.database import Bill
from main_db_dependency import get_db
from services.congress_service import CongressService
from services.logging_service import log_error

router = APIRouter()

@router.get("/today", response_model=BillListResponse)
def get_bills_today(db: Session = Depends(get_db)):
    """Return the most recently updated bills in the database."""
    bills = (
        db.query(Bill)
        .order_by(desc(Bill.introduced_date))
        .limit(12)
        .all()
    )
    results = []
    for b in bills:
        results.append(BillDetail(
            id=b.id,
            title=b.title,
            status=b.status,
            introduced_date=b.introduced_date,
            latest_action=b.latest_action_text,
            summary=b.summary,
            url=b.url,
        ))
    return BillListResponse(bills=results, count=len(results))

@router.get("/search", response_model=BillListResponse)
def search_bills(q: str, db: Session = Depends(get_db)):
    """Search bills by keyword across title and latest_action_text."""
    bills = (
        db.query(Bill)
        .filter(
            Bill.title.ilike(f"%{q}%") | Bill.latest_action_text.ilike(f"%{q}%")
        )
        .order_by(desc(Bill.introduced_date))
        .limit(15)
        .all()
    )
    results = []
    for b in bills:
        results.append(BillDetail(
            id=b.id,
            title=b.title,
            status=b.status,
            introduced_date=b.introduced_date,
            latest_action=b.latest_action_text,
            summary=b.summary,
            url=b.url,
        ))
    return BillListResponse(bills=results, count=len(results))

@router.post("/refresh")
def refresh_bills(db: Session = Depends(get_db)):
    """On-demand endpoint to pull the latest bills from Congress.gov right now."""
    result = CongressService.seed_database(db)
    if not result.get("success"):
        raise HTTPException(status_code=429, detail=result.get("error", "Rate limit exceeded"))
    count = db.query(Bill).count()
    return {"status": "refreshed", "total_bills": count, "new": result.get("new"), "updated": result.get("updated")}

@router.get("/{bill_id}", response_model=BillDetail)
def get_bill_detail(bill_id: str, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    from services.rag_service import RAGService
    
    # Live Congress API Extraction
    sponsors = CongressService.fetch_bill_sponsors(bill.congress, bill.bill_type, bill.bill_number)
    votes = CongressService.fetch_bill_votes(bill.congress, bill.bill_type, bill.bill_number)
    
    # GraphRAG Similarity Computation
    rag = RAGService()
    related_bills = []
    try:
        similar = rag.retrieve_relevant_bills(str(bill.title), top_k=4)
        related_bills = [s.get("bill_id") for s in similar if s.get("bill_id") and s.get("bill_id") != bill.id][:3]
    except Exception as e:
        log_error(str(e), context="BillModal/RAG")

    # Fallback to empty states if actual extraction limit breaks during demo
    if not sponsors and not votes:
         sponsors = [{"name": "Rate Limited / No Sponsors", "party": "-", "state": "-", "is_lead": 1}]
         
    return BillDetail(
        id=bill.id,
        title=bill.title,
        summary=bill.summary,
        introduced_date=bill.introduced_date,
        status=bill.status,
        latest_action=bill.latest_action_text,
        url=bill.url,
        sponsors=sponsors,
        votes=votes,
        related_bills=related_bills
    )

@router.get("/news/feed")
def get_live_news():
    """DuckDuckGo scraper wrapper strictly for breaking dashboard news feeds"""
    from duckduckgo_search import DDGS
    import logging
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text("Congress legislation news \"bill\"", max_results=5))
            return {"status": "success", "articles": results}
    except Exception as e:
        log_error(str(e), context="LiveNewsFeed")
        return {"status": "error", "articles": []}
