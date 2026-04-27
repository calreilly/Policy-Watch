from fastapi import APIRouter
from services.evaluation import evaluate_retrieval, load_test_dataset

router = APIRouter()

# In-memory cache for last evaluation run
_last_results = None

@router.get("/run")
def run_evaluation():
    """Execute the RAG evaluation suite against the test dataset."""
    global _last_results
    dataset = load_test_dataset()
    if not dataset:
        return {"status": "error", "message": "Test dataset not found or empty"}
    
    _last_results = evaluate_retrieval(dataset)
    return {"status": "success", "results": _last_results}

@router.get("/results")
def get_evaluation_results():
    """Retrieve the results of the most recent evaluation run."""
    if _last_results is None:
        return {"status": "error", "message": "No evaluation has been run yet"}
    return {"status": "success", "results": _last_results}
