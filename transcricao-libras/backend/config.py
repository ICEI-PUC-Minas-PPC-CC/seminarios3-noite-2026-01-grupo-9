"""
config.py — Configurações da aplicação.

Lê variáveis de ambiente (ou .env) com valores padrão seguros
para desenvolvimento local. NUNCA contém dados reais de produção.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ---------- Banco de Dados ----------
    # Padrão: SQLite local (arquivo na pasta do projeto)
    DATABASE_URL: str = "sqlite:///./transcricoes.db"

    # ---------- CORS ----------
    # Origens permitidas para requisições do frontend.
    # Em dev usamos localhost; em homologação, ajustar conforme necessário.
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5500",   # Live Server do VS Code
    ]

    # ---------- Geral ----------
    DEBUG: bool = True
    APP_TITLE: str = "Tradutor de Voz para Libras — API"
    APP_VERSION: str = "0.1.0"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


# Instância única reutilizada em toda a aplicação
settings = Settings()
