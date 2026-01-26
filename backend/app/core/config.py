import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://username:password@localhost/virtue_tryon_db"
    
    # JWT
    SECRET_KEY: str = "u0YJp3Nn9q7ZxA4fNQ2sLeH8wCkVt1mG5rSdIbXuP0FyDzahEc"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    PROJECT_NAME: str = "Virtue Try-On API"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: list = ["*"]  # Allow all origins in development
    
    @field_validator('DEBUG', mode='before')
    @classmethod
    def parse_debug(cls, v):
        """Handle DEBUG env var that might be string"""
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes')
        return bool(v)
    
    # File paths
    UPLOAD_DIR: str = "static/uploads"
    OUTPUT_DIR: str = "static/generated_outputs"
    INTERMEDIATE_DIR: str = "static/intermediate_outputs"
    
    # AI Model
    MODEL_NAME: str = "yisol/IDM-VTON"  # Hugging Face model
    VTO_MODEL_REPO: str = "yisol/IDM-VTON"  # VTO model repository (NOT a Space!)
    # Options: 
    #   "yisol/IDM-VTON" - Currently downloaded, using with workaround
    #   "runwayml/stable-diffusion-v1-5" - General SD model (fallback)
    #   "stabilityai/stable-diffusion-xl-base-1.0" - SDXL (fallback)
    DEVICE: str = "cpu"  # or "cuda"
    SAVE_INTERMEDIATE_OUTPUTS: bool = True
    
    # HuggingFace Token (add to .env file)
    HF_TOKEN: Optional[str] = None
    
    # Gradio Space Configuration (for API-based VTO)
    GRADIO_SPACE_NAME: str = "frogleo/AI-Clothes-Changer"
    USE_GRADIO_SPACE: bool = True  # Set to False to use local models
    VTON_DENOISE_STEPS: int = 30  # Higher = better quality, slower
    VTON_SEED: int = 42  # For reproducibility
    
    # File size limits (in bytes)
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False  # Allow case-insensitive env vars
        extra = "ignore"  # Ignore extra fields in .env file
        env_prefix = ""  # No prefix for env vars

settings = Settings()