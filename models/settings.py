from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str 
    google_places_api_key: str
    
    class Config:
        env_file = ".env"  # Pydantic handles this natively

settings = Settings()
