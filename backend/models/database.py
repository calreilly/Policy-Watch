from sqlalchemy import create_engine, Column, String, Integer, Date, DateTime, Float, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Bill(Base):
    __tablename__ = "bills"
    
    id = Column(String, primary_key=True)  # e.g., "118-S-686"
    congress = Column(Integer)
    bill_type = Column(String)
    bill_number = Column(Integer)
    title = Column(String, nullable=False)
    summary = Column(Text)
    introduced_date = Column(Date)
    latest_action_date = Column(Date)
    latest_action_text = Column(String)
    status = Column(String)
    url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    sponsors = relationship("Sponsor", back_populates="bill", cascade="all, delete-orphan")
    votes = relationship("BillVote", back_populates="bill", cascade="all, delete-orphan")
    embeddings = relationship("BillEmbedding", back_populates="bill", cascade="all, delete-orphan")

class Sponsor(Base):
    __tablename__ = "sponsors"
    
    id = Column(Integer, primary_key=True)
    bill_id = Column(String, ForeignKey("bills.id"), nullable=False)
    member_name = Column(String, nullable=False)
    member_id = Column(String)
    party = Column(String)  # 'R', 'D', 'I'
    state = Column(String)
    is_lead = Column(Integer, default=0)
    
    bill = relationship("Bill", back_populates="sponsors")

class BillVote(Base):
    __tablename__ = "bill_votes"
    
    id = Column(Integer, primary_key=True)
    bill_id = Column(String, ForeignKey("bills.id"), nullable=False)
    vote_chamber = Column(String)  # 'House' or 'Senate'
    vote_type = Column(String)
    vote_date = Column(Date)
    yes_count = Column(Integer)
    no_count = Column(Integer)
    abstain_count = Column(Integer)
    result = Column(String)  # 'Passed' or 'Failed'
    
    bill = relationship("Bill", back_populates="votes")

class BillEmbedding(Base):
    __tablename__ = "bill_embeddings"
    
    id = Column(Integer, primary_key=True)
    bill_id = Column(String, ForeignKey("bills.id"), nullable=False)
    chunk_index = Column(Integer)
    text_chunk = Column(Text)
    embedding_id = Column(String)  # ChromaDB ID
    created_at = Column(DateTime, default=datetime.utcnow)
    
    bill = relationship("Bill", back_populates="embeddings")

class GeneratedBrief(Base):
    __tablename__ = "generated_briefs"
    
    id = Column(Integer, primary_key=True)
    user_query = Column(String, nullable=False)
    brief_content = Column(Text)
    bills_cited = Column(String)  # JSON array
    agent_reasoning = Column(Text)
    trust_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    traces = relationship("PipelineTrace", back_populates="brief", cascade="all, delete-orphan")

class PipelineTrace(Base):
    __tablename__ = "pipeline_traces"
    
    id = Column(Integer, primary_key=True)
    brief_id = Column(Integer, ForeignKey("generated_briefs.id"))
    step_number = Column(Integer)
    action = Column(String)
    details = Column(Text)  # JSON
    duration_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    brief = relationship("GeneratedBrief", back_populates="traces")
