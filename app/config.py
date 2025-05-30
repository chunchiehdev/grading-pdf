import os

class Settings:
    # Redis configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # File upload configuration
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "50")) * 1024 * 1024  # 50MB default

settings = Settings() 