from pydantic import BaseModel, Field, validator
from typing import List, Optional, Any, Dict
from datetime import date, datetime

class SponsorSchema(BaseModel):
    member_name: str
    party: Optional[str] = None
    state: Optional[str] = None
    is_lead: Optional[int] = 0

class VoteSchema(BaseModel):
    vote_chamber: str
    vote_type: str
    vote_date: date
    yes_count: Optional[int] = None
    no_count: Optional[int] = None
    result: str

class FinanceSummary(BaseModel):
    total_raised: float
    total_spent: float
    cash_on_hand: float
    fec_url: str

class BillBase(BaseModel):
    id: str
    title: str
    status: Optional[str] = None
    summary: Optional[str] = None
    introduced_date: Optional[date] = None
    latest_action: Optional[str] = None
    url: Optional[str] = None

class BillDetail(BillBase):
    sponsors: List[SponsorSchema] = []
    votes: List[VoteSchema] = []
    related_bills: List[str] = []
    finance: Optional[FinanceSummary] = None

class BillListResponse(BaseModel):
    status: str = "success"
    bills: List[BillDetail]
    count: int

class BriefRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500, description="Legislative policy query")

    @validator('query')
    def validate_query(cls, v):
        # Simple injection guard
        dangerous = ["DROP", "DELETE", "INSERT", "UPDATE", "--", "/*", "*/"]
        if any(word.lower() in v.lower() for word in dangerous):
            raise ValueError('Query contains potentially malicious patterns')
        # Limit special characters ratio
        special = sum(1 for c in v if not c.isalnum() and not c.isspace())
        if special / max(len(v), 1) > 0.3:
            raise ValueError('Query has too many special characters')
        return v.strip()

class PipelineTraceSchema(BaseModel):
    step: int
    action: str
    details: Optional[str] = None
    duration_ms: Optional[int] = None

class BriefResponse(BaseModel):
    status: str = "success"
    brief_id: Optional[int] = None
    brief: str
    bills_cited: List[str] = []
    trust_score: float = 0.0
    pipeline_trace: List[PipelineTraceSchema] = []

class CompareRequest(BaseModel):
    bill_ids: List[str]

class ImpactReport(BaseModel):
    sectors: List[str]
    budgetary_impact: str
    timeline: str
    stakeholders: List[str]
    risks: str

class CompareResponse(BaseModel):
    comparisons: Dict[str, Any]
