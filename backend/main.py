from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

load_dotenv()

from main_db_dependency import engine, Base, SessionLocal
from api import bills, agent
from services.congress_service import CongressService
from services.rag_service import RAGService
from models.database import Bill

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Recreate tables fresh on every boot so we always pull current data
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    congress_service = CongressService()
    rag_service = RAGService()
    
    print("Fetching live legislation from Congress.gov...")
    congress_service.seed_database(db)
    
    print("Building RAG index from current bills...")
    all_bills = db.query(Bill).all()
    rag_service.seed_embeddings(all_bills)
    
    db.close()
    print(f"Startup complete. {len(all_bills)} live bills indexed.")
    yield

app = FastAPI(title="PolicyWatch API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bills.router, prefix="/api/bills", tags=["bills"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
