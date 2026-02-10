import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator

class Settings(BaseSettings):
    # Database
    # Default to SQLite for local development, PostgreSQL for production (Render)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./virtue_tryon.db")
    
    # JWT
    SECRET_KEY: str = "u0YJp3Nn9q7ZxA4fNQ2sLeH8wCkVt1mG5rSdIbXuP0FyDzahEc"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000  # Will be overridden in __init__
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"  # Default False in production
    PROJECT_NAME: str = "Virtue Try-On API"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: list = ["*"]  # Allow all origins in development
    
    def __init__(self, **kwargs):
        """Initialize with manual PORT handling to avoid empty string validation error"""
        # Remove PORT from kwargs if present (to handle manually)
        port_env = os.getenv("PORT", "")
        if 'PORT' in kwargs:
            # If PORT is in kwargs but empty, remove it
            if isinstance(kwargs['PORT'], str) and not kwargs['PORT'].strip():
                del kwargs['PORT']
            elif isinstance(kwargs['PORT'], str):
                try:
                    kwargs['PORT'] = int(kwargs['PORT'].strip())
                except (ValueError, TypeError):
                    del kwargs['PORT']
        
        super().__init__(**kwargs)
        
        # Set PORT manually after initialization
        if port_env and port_env.strip():
            try:
                port_value = int(port_env.strip())
            except (ValueError, TypeError):
                port_value = 8000
        else:
            port_value = 8000
        
        object.__setattr__(self, 'PORT', port_value)
    
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
    # Default: frogleo/AI-Clothes-Changer → /infer
    # If frogleo fails, backend falls back to yisol/IDM-VTON (/tryon) in GradioVTONService.
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
        env_ignore_empty = True  # Ignore empty environment variables

settings = Settings()