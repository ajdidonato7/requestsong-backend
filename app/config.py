import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # MongoDB settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "requestr")
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://*.vercel.app",     # Allow Vercel domains
        "https://*.fly.dev",        # Allow Fly.io domains
        "https://*.onrender.com",   # Allow Render domains
    ]
    
    @property
    def cors_origins(self):
        """Get CORS origins with wildcard support"""
        origins = self.ALLOWED_ORIGINS.copy()
        # Add specific frontend URL if deployed
        frontend_url = os.getenv("FRONTEND_URL")
        if frontend_url:
            origins.append(frontend_url)
        return origins
    
    # Production settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

settings = Settings()