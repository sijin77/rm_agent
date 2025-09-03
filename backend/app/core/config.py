"""
Настройки приложения
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/rm_agent.db"
    
    # App
    DEBUG: bool = True
    PROJECT_NAME: str = "RM Agent"
    VERSION: str = "1.0.0"
    
    # LLM
    LLM_API_URL: str = "http://localhost:8080"  # llama.cpp сервер
    LLM_MODEL: str = "llama-3.1-8b"
    
    class Config:
        env_file = ".env"


settings = Settings()
