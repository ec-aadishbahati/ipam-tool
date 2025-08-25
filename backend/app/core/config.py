from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: str = ""
    CORS_ORIGIN_REGEX: str = ""
    LOG_LEVEL: str = "info"
    ENV: str = "production"

    class Config:
        env_file = ".env"


settings = Settings()
