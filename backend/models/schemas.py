from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import date, datetime

class SponsorSchema(BaseModel):
    name: str
    party: Optional[str] = None
    state: Optional[str] = None

class VoteSchema(BaseModel):
    chamber: str
    type: str
    date: date
    yes: Optional[int] = None
    no: Optional[int] = None
    result: str

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

class BillListResponse(BaseModel):
    status: str = "success"
    bills: List[BillDetail]
    count: int

class BriefRequest(BaseModel):
    query: str

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
