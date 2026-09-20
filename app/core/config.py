from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = "your_key_here_optional"
    max_file_size_mb: int = 50
    session_timeout_minutes: int = 60
    upload_dir: str = "./uploads"

    class Config:
        env_file = ".env"

settings = Settings()
