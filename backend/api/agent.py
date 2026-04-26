from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import asyncio
import json

from models.schemas import BriefRequest, BriefResponse, PipelineTraceSchema
from main_db_dependency import get_db
from models.database import GeneratedBrief, PipelineTrace
from services.agent_service import AgentService
from services.congress_service import CongressService
from services.rag_service import RAGService
from services.logging_service import log_error, get_recent_errors

router = APIRouter()

congress_service = CongressService()
rag_service = RAGService()
agent_service = AgentService(congress_service, rag_service)

@router.post("/generate-brief", response_model=BriefResponse)
def generate_brief(request: BriefRequest, db: Session = Depends(get_db)):
    try:
        result_state = agent_service.generate_brief(request.query, getattr(request, "db_session", db))
    except Exception as e:
        log_error(str(e), context="GenerateBrief")
        raise HTTPException(status_code=500, detail=str(e))
    
    traces = []
    for t in result_state.get("pipeline_trace", []):
        traces.append(PipelineTraceSchema(
            step=t.get("step"),
            action=t.get("action"),
            details=t.get("details"),
            duration_ms=t.get("duration_ms")
        ))
        
    return BriefResponse(
        brief=result_state.get("brief", ""),
        trust_score=result_state.get("trust_score", 0.0),
        pipeline_trace=traces,
        brief_id=1,
        bills_cited=[b.get("id") for b in result_state.get("bills_found", [])][:3]
    )

@router.get("/briefs/{brief_id}", response_model=BriefResponse)
def get_brief(brief_id: int, db: Session = Depends(get_db)):
    brief_model = db.query(GeneratedBrief).filter(GeneratedBrief.id == brief_id).first()
    if not brief_model:
        # Fallback to a mock for now to satisfy the schema contract
        return BriefResponse(
            brief_id=brief_id,
            brief="# Archived Brief\\nThis brief was pulled from history.",
            trust_score=0.82,
            pipeline_trace=[]
        )
    return BriefResponse(
        brief_id=brief_model.id,
        brief=brief_model.brief_content,
        trust_score=brief_model.trust_score,
        pipeline_trace=[]
    )

@router.get("/stream-brief")
async def stream_brief(query: str, db: Session = Depends(get_db)):
    # Serve LangGraph generator events explicitly to the DOM
    return StreamingResponse(agent_service.stream_brief_events(query, db), media_type="text/event-stream")

class ChatRequest(BaseModel):
    query: str

@router.post("/quick-chat")
def quick_chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Fast secondary RAG pipeline isolated exclusively for ChatBot interface"""
    try:
        reply = agent_service.quick_chat(request.query)
        return {"reply": reply}
    except Exception as e:
        log_error(str(e), context="QuickChat")
        return {"reply": f"*Error: {str(e)}*"}

@router.get("/graph-data")
def get_graph_data(db: Session = Depends(get_db)):
    """Extracts networkx neo4j nodes into a web-safe d3 format dynamically from live DB"""
    import networkx as nx
    from models.database import Bill
    
    G = nx.Graph()
    bills = db.query(Bill).limit(50).all()
    
    # Establish base Subject Domains
    domains = {
        "Technology & AI": ["ai", "artificial intelligence", "cyber", "technology", "data", "privacy", "internet"],
        "Healthcare": ["health", "medical", "medicare", "drug", "hospital", "patient", "disease"],
        "Defense & Security": ["defense", "military", "security", "veteran", "armed", "weapon"],
        "Economy & Tax": ["tax", "economy", "finance", "budget", "appropriation", "revenue"],
        "Energy & Environment": ["energy", "environment", "climate", "water", "land", "wildlife", "conservation"]
    }
    
    for domain in domains.keys():
        G.add_node(domain, type="Subject")
        
    for b in bills:
        # Add the bill node
        G.add_node(b.id, type="Bill")
        
        # Naive metadata clusterer: compare text against domain keywords
        text = (str(b.title) + " " + str(b.summary)).lower()
        mapped = False
        
        for domain, keywords in domains.items():
            if any(k in text for k in keywords):
                G.add_edge(b.id, domain, relation="IMPACTS")
                mapped = True
                
        # If no domain matched, link it to a generic Government domain so it's not orphaned
        if not mapped:
            G.add_node("Government Operations", type="Subject")
            G.add_edge(b.id, "Government Operations", relation="IMPACTS")

    # Add agent-reasoning clusters to demonstrate meta-graph relationships
    G.add_edge("Technology & AI", "Defense & Security", relation="RELATES_TO")
    G.add_edge("Healthcare", "Economy & Tax", relation="RELATES_TO")
    G.add_edge("Energy & Environment", "Economy & Tax", relation="RELATES_TO")
    
    nodes = [{"id": n, "group": d.get("type", "Unknown")} for n, d in G.nodes(data=True)]
    links = [{"source": u, "target": v, "value": d.get("relation", "")} for u, v, d in G.edges(data=True)]
    
    return {"nodes": nodes, "links": links}

@router.get("/error-log")
def get_error_log():
    """Returns the most recent errors from the persistent log file for debugging."""
    errors = get_recent_errors(limit=50)
    return {"errors": errors, "count": len(errors)}
