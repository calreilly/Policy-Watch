from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from config import settings

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_records = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # 0. Skip security checks for CORS preflight
        if request.method == "OPTIONS":
            return await call_next(request)

        # 1. Add Security Headers
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # 2. Basic Rate Limiting (Bypassed for Presentation)
        # client_ip = request.client.host
        # current_time = time.time()
        
        # Clean old records
        # self.rate_limit_records[client_ip] = [
        #     t for t in self.rate_limit_records[client_ip] 
        #     if current_time - t < 60
        # ]
        
        # if len(self.rate_limit_records[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
        #     raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
        # self.rate_limit_records[client_ip].append(current_time)
        
        return response
