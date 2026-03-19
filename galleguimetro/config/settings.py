import os
from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    debug: bool = False

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/galleguimetro_db"

    # JWT Auth
    secret_key: str = "CHANGE-ME-IN-PRODUCTION-use-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Qdrant
    qdrant_url: str = "http://localhost:7333"
    qdrant_api_key: Optional[str] = None

    # Logging
    log_level: str = "INFO"
    sqlalchemy_echo: bool = False

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


settings = Settings()
