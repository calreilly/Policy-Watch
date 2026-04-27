from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from main_db_dependency import get_db
from services.rag_service import RAGService
import time

router = APIRouter()
rag_service = RAGService()

@router.get("/")
def health_check(db: Session = Depends(get_db)):
    """
    Detailed health check for PolicyWatch components:
    - Database connectivity
    - RAG Service (ChromaDB)
    - System health uptime
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "components": {}
    }

    # 1. Check Database
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        health_status["components"]["database"] = "reachable"
    except Exception as e:
        health_status["components"]["database"] = f"unreachable: {str(e)}"
        health_status["status"] = "degraded"

    # 2. Check RAG Service
    try:
        count = rag_service.collection.count()
        health_status["components"]["rag_service"] = {
            "status": "active",
            "vector_count": count
        }
    except Exception as e:
        health_status["components"]["rag_service"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    return health_status
