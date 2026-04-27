import logging
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

class ErrorType(Enum):
    API_TIMEOUT = "api_timeout"
    RATE_LIMIT = "rate_limit"
    VALIDATION_ERROR = "validation_error"
    RETRIEVAL_EMPTY = "retrieval_empty"
    LLM_ERROR = "llm_error"
    UNKNOWN = "unknown"

@dataclass
class ErrorState:
    error_type: ErrorType
    message: str
    timestamp: str = datetime.utcnow().isoformat()
    recovery_attempted: bool = False
    retry_count: int = 0

def format_error(state: ErrorState) -> dict:
    """Return a JSON‑serialisable dict for API consumption"""
    return {
        "error_type": state.error_type.value,
        "message": state.message,
        "timestamp": state.timestamp,
        "recovery_attempted": state.recovery_attempted,
        "retry_count": state.retry_count,
    }
