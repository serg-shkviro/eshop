from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения"""
    
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "myapp"
    
    DB_ECHO: bool = False
    
    SECRET_KEY: str = "your-secret-key-change-this-in-production-please-make-it-secure"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Первый администратор (создается при запуске, если нет администраторов)
    FIRST_ADMIN_EMAIL: Optional[str] = None
    FIRST_ADMIN_PASSWORD: Optional[str] = None
    FIRST_ADMIN_NAME: Optional[str] = None
    
    # Настройки CORS
    CORS_ORIGINS: str = "http://localhost:3000,https://localhost:3000,http://localhost:5173,https://localhost:5173,http://localhost:8080,https://localhost:8080,http://localhost:4200,https://localhost:4200,http://localhost:5174,https://localhost:5174"
    
    @property
    def DATABASE_URL(self) -> str:
        """Формирует URL базы данных из компонентов"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True
    )


settings = Settings()

