"""
Governança Centralizada de Configurações e Segredos (Framework SETISD)
======================================================================
Carrega e valida as variáveis de ambiente obrigatórias e opcionais da aplicação.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Configurações centralizadas da aplicação carregadas a partir do ambiente (.env)."""

    ENV: str = os.getenv("ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

    # Bancos de Dados
    SQLITE_DSN: str = os.getenv("SQLITE_DSN", os.getenv("APP_DB_URL", "sqlite+aiosqlite:///./app.db"))
    POSTGRES_DSN: str = os.getenv("POSTGRES_DSN", "")
    ORACLE_DSN: str = os.getenv("ORACLE_DSN", "")

    # Active Directory / LDAP
    AD_URL: str = os.getenv("AD_URL", "ldap://ebserhnet.gov.br")
    AD_BASEDN: str = os.getenv("AD_BASEDN", "DC=ebserhnet,DC=gov,DC=br")
    AD_BIND_USER: str = os.getenv("AD_BIND_USER", "")
    AD_BIND_PASSWORD: str = os.getenv("AD_BIND_PASSWORD", "")

    # Segurança JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_EXP_HOURS: int = int(os.getenv("JWT_EXP_HOURS", "24"))
    REFRESH_TOKEN_EXP_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXP_DAYS", "30"))

    # CORS
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:8000,http://localhost:8000",
        ).split(",")
        if origin.strip()
    ]


settings = Settings()

