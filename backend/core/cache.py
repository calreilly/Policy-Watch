import functools
import json
import time
from typing import Any

# Simple In-Memory Cache (demonstration)
# In production, replace this with Redis
_GLOBAL_CACHE = {}

def cached(ttl_seconds: int = 300):
    """
    Decorator to cache function results.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            if cache_key in _GLOBAL_CACHE:
                result, timestamp = _GLOBAL_CACHE[cache_key]
                if time.time() - timestamp < ttl_seconds:
                    return result
            
            # Execute and cache
            result = func(*args, **kwargs)
            _GLOBAL_CACHE[cache_key] = (result, time.time())
            return result
        return wrapper
    return decorator

def clear_cache():
    global _GLOBAL_CACHE
    _GLOBAL_CACHE = {}
