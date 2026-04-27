import numpy as np

def calculate_mrr(relevant_ids, retrieved_ids):
    """
    Mean Reciprocal Rank calculation.
    """
    for i, rid in enumerate(retrieved_ids):
        if rid in relevant_ids:
            return 1.0 / (i + 1)
    return 0.0

def calculate_ndcg(relevant_ids, retrieved_ids, k=10):
    """
    Normalized Discounted Cumulative Gain at k.
    """
    retrieved_ids = retrieved_ids[:k]
    dcg = 0.0
    for i, rid in enumerate(retrieved_ids):
        if rid in relevant_ids:
            # Assume binary relevance (1 or 0)
            dcg += 1.0 / np.log2(i + 2)
            
    # Calculate IDCG (Ideal DCG)
    idcg = 0.0
    for i in range(min(len(relevant_ids), k)):
        idcg += 1.0 / np.log2(i + 2)
        
    return dcg / idcg if idcg > 0 else 0.0

def evaluate_retrieval(dataset: list):
    """
    Dataset format: [{"query": str, "relevant_ids": [str]}]
    """
    from services.rag_service import RAGService
    rag = RAGService()
    
    mrr_scores = []
    ndcg_scores = []
    
    for item in dataset:
        retrieved = rag.retrieve_relevant_bills(item["query"], top_k=10)
        retrieved_ids = [r.get("bill_id") for r in retrieved]
        
        mrr_scores.append(calculate_mrr(item["relevant_ids"], retrieved_ids))
        ndcg_scores.append(calculate_ndcg(item["relevant_ids"], retrieved_ids))
        
    return {
        "mean_mrr": float(np.mean(mrr_scores)) if mrr_scores else 0.0,
        "mean_ndcg": float(np.mean(ndcg_scores)) if ndcg_scores else 0.0,
        "count": len(dataset)
    }

def load_test_dataset(path: str = "test_queries.json"):
    import json
    import os
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)
