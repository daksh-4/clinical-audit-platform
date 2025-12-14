"""
Application configuration using Pydantic settings.
"""
from typing import List, Optional
from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    # Application
    PROJECT_NAME: str = "Clinical Audit Platform"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str  # Must be set in .env
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[PostgresDsn] = None
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> str:
        if isinstance(v, str):
            return v
        
        values = info.data
        return str(PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"{values.get('POSTGRES_DB') or ''}",
        ))
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = ""
    
    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_connection(cls, v: Optional[str], info) -> str:
        if isinstance(v, str) and v:
            return v
        
        values = info.data
        return f"redis://{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/{values.get('REDIS_DB')}"
    
    # Encryption
    FERNET_KEY: str  # Must be set in .env - use Fernet.generate_key()
    
    # Email (for notifications)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # NHS Login (future integration)
    NHS_LOGIN_CLIENT_ID: Optional[str] = None
    NHS_LOGIN_CLIENT_SECRET: Optional[str] = None
    NHS_LOGIN_REDIRECT_URI: Optional[str] = None
    
    # Security
    PASSWORD_MIN_LENGTH: int = 12
    MFA_ISSUER: str = "Clinical Audit Platform"
    
    # Data Protection
    PII_RETENTION_DAYS_DEFAULT: int = 3650  # 10 years
    AUDIT_LOG_RETENTION_DAYS: int = 2555  # 7 years
    
    # Export Settings
    EXPORT_MAX_RECORDS: int = 1000000
    EXPORT_LINK_EXPIRY_HOURS: int = 24
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 1000
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = [".csv", ".xlsx", ".json"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"


settings = Settings()
