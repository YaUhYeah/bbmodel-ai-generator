import os
from pydantic import BaseModel
from typing import List, Optional

class Settings(BaseModel):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI-Powered bbmodel Generator"
    
    # SECURITY
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # AI Model settings
    MODEL_CHECKPOINT: str = "stabilityai/stable-diffusion-2-1"
    DEVICE: str = "cuda" if os.getenv("USE_CUDA", "0") == "1" else "cpu"
    
    # Storage
    MODELS_DIR: str = "./static/models"
    TEXTURES_DIR: str = "./static/textures"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()