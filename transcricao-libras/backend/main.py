"""
main.py — Ponto de entrada do servidor FastAPI.

Ambiente: desenvolvimento local (localhost:8000).
Serve tanto a API quanto os arquivos estáticos do frontend.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
from database import Base, engine
from routers.transcricoes import router as transcricoes_router

# ── Criar tabelas no banco (dev apenas) ────────────────
# Em produção, usar Alembic para migrações controladas.
Base.metadata.create_all(bind=engine)

# ── App FastAPI ─────────────────────────────────────────
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ── CORS ────────────────────────────────────────────────
# Necessário para o frontend se comunicar com a API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────
app.include_router(transcricoes_router)


# ── Health Check ────────────────────────────────────────
@app.get("/api/health")
def health_check():
    """Verifica se o backend está funcionando."""
    return {"status": "ok", "mensagem": "Backend do Tradutor Libras funcionando"}


# ── Servir Frontend (arquivos estáticos) ────────────────
# O frontend é servido como arquivos estáticos a partir da pasta ../frontend
# Isso permite deploy unificado (um único servidor para tudo).
frontend_path = Path(__file__).resolve().parent.parent / "frontend"
if frontend_path.is_dir():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")