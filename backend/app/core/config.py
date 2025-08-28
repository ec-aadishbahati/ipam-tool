import re
from pydantic import validator
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
    
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    ADMIN_EMAIL: str

    @validator('ADMIN_PASSWORD')
    def validate_admin_password(cls, v):
        if len(v) < 12:
            raise ValueError('Admin password must be at least 12 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Admin password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Admin password must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Admin password must contain number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Admin password must contain special character')
        return v

    @validator('CORS_ORIGINS')
    def validate_cors_origins(cls, v, values):
        if not v and values.get('ENV') == 'production':
            raise ValueError('CORS_ORIGINS required in production')
        
        if v:
            origins = [o.strip() for o in v.split(',')]
            for origin in origins:
                if origin == "*" and values.get('ENV') == 'production':
                    raise ValueError('Wildcard CORS origins not allowed in production')
        
        return v

    class Config:
        env_file = ".env"


settings = Settings()
