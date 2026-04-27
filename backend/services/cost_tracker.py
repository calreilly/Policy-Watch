from typing import Dict

# Simple per‑model token pricing (USD per 1k tokens)
MODEL_PRICING = {
    "gpt-4o-mini": 0.015,  # $0.015 per 1k tokens (example)
    "gpt-4o": 0.03,
    "gpt-3.5-turbo": 0.002,
}

# In‑memory aggregation (reset on process restart)
_token_usage: Dict[str, int] = {}
_costs: Dict[str, float] = {}

def add_token_usage(model: str, count: int = 1):
    """Record token usage for a model and update cost aggregation."""
    global _token_usage, _costs
    _token_usage[model] = _token_usage.get(model, 0) + count
    price_per_1k = MODEL_PRICING.get(model, 0.0)
    _costs[model] = _costs.get(model, 0.0) + (price_per_1k * count / 1000.0)

def get_usage() -> Dict[str, int]:
    return _token_usage.copy()

def get_costs() -> Dict[str, float]:
    return _costs.copy()
