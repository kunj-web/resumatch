from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Groq
    GROQ_API_KEY: str
    GROQ_MODEL: str = "openai/gpt-oss-120b"

    # Supabase Storage
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_BUCKET: str = "resumes"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
