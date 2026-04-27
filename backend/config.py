from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "PolicyWatch"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    OPENAI_API_KEY: str
    CONGRESS_API_KEY: str = "dummy"
    
    # Security
    ALLOWED_ORIGINS: List[str] = ["*"]
    RATE_LIMIT_PER_MINUTE: int = 200
    
    # DB
    DATABASE_URL: str = "sqlite:///./policywatch.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
