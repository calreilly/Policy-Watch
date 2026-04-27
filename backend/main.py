from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

# Structured logging setup
from core.logging_config import setup_logging
setup_logging()

load_dotenv()

from main_db_dependency import engine, Base, SessionLocal
from api import bills, agent, health, comparison, federal_register, openstates, govtrack, evaluation_router, analysis
from core.metrics import record_request, get_metrics_response
from services.cost_tracker import get_costs, get_usage
from services.congress_service import CongressService
from services.rag_service import RAGService
from models.database import Bill

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    congress_service = CongressService()
    rag_service = RAGService()
    try:
        congress_service.seed_database(db)
        all_bills = db.query(Bill).all()
        rag_service.seed_embeddings(all_bills)
        
        # Seed Global Benchmarks
        eu_ai_act = {
            "title": "EU Artificial Intelligence Act (Regulation 2024/1689)",
            "source": "European Parliament",
            "text": """
            Fundamental framework for AI regulation in the EU. 
            Risk categories: Prohibited (Clear threat), High-Risk (Critical infrastructure, hiring, credit), 
            Limited-Risk (Transparency requirements), Minimal-Risk (No obligations).
            Obligations for GPAI models: Transparency, documentation, human oversight. 
            Phased implementation from 2024 to 2027.
            """
        }
        rag_service.seed_global_benchmarks([eu_ai_act])
    except Exception as e:
        print(f"Startup warning: Database seeding failed: {e}")
    finally:
        db.close()
    yield

from fastapi.middleware.gzip import GZipMiddleware
from middleware.security import SecurityMiddleware

app = FastAPI(title="PolicyWatch API", lifespan=lifespan)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Middleware execution order is LAST added -> FIRST added
# We want: CORS (Outer) -> Security (Rate Limit/Headers) -> Metrics -> Router

@app.middleware("http")
async def metrics_middleware(request, call_next):
    record_request(request.method, request.url.path)
    return await call_next(request)

app.add_middleware(SecurityMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://localhost:5174", "http://localhost:5175",
        "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:5175",
        "http://localhost:4173", "http://127.0.0.1:4173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(bills.router, prefix="/api/bills", tags=["bills"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(comparison.router, prefix="/api/comparison", tags=["comparison"])
app.include_router(federal_register.router, prefix="/api/federal-register", tags=["federal-register"])
app.include_router(openstates.router, prefix="/api/openstates", tags=["openstates"])
app.include_router(govtrack.router, prefix="/api/govtrack", tags=["govtrack"])
app.include_router(evaluation_router.router, prefix="/api/evaluation", tags=["evaluation"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])

@app.get("/metrics")
def metrics():
    return Response(get_metrics_response(), media_type="text/plain")

@app.get("/api/admin/cost-analytics")
def cost_analytics():
    return {
        "usage": get_usage(),
        "costs": get_costs()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
