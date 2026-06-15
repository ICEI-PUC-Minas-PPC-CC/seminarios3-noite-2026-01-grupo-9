"""
database.py — Configuração do SQLAlchemy (engine + sessão).

Ambiente: desenvolvimento local (SQLite).
Para homologação/produção, trocar DATABASE_URL para PostgreSQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import settings

# ---------- Engine ----------
# connect_args necessário apenas para SQLite (checagem de thread)
_connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args,
    echo=settings.DEBUG,  # Loga SQL no console em modo debug
)

# ---------- Session ----------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------- Base ----------
Base = declarative_base()


def get_db():
    """
    Dependency do FastAPI que fornece uma sessão de banco de dados
    e garante o fechamento ao final da requisição.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
