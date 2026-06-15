"""
routers/transcricoes.py — Endpoints CRUD para transcrições.

Segurança:
- Todas as queries usam o ORM SQLAlchemy (prepared statements internos).
- Validação de entrada via Pydantic schemas.
- IP anonimizado com SHA-256 antes de persistir.
- Nenhum dado sensível é armazenado.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import Transcricao
from schemas import (
    EstatisticasResponse,
    PaginacaoResponse,
    TranscricaoCreate,
    TranscricaoResponse,
)

router = APIRouter(prefix="/api", tags=["Transcrições"])


# ── POST /api/transcricoes ──────────────────────────────

@router.post("/transcricoes", response_model=TranscricaoResponse, status_code=201)
def criar_transcricao(
    payload: TranscricaoCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Salva uma nova transcrição de voz no banco de dados.
    O IP do cliente é anonimizado (SHA-256) antes de ser armazenado.
    """
    # Anonimizar IP do cliente
    client_ip = request.client.host if request.client else "unknown"
    ip_hash = Transcricao.anonimizar_ip(client_ip)

    nova = Transcricao(
        texto=payload.texto,
        idioma=payload.idioma,
        duracao_ms=payload.duracao_ms,
        confianca=payload.confianca,
        session_id=payload.session_id,
        ip_hash=ip_hash,
    )

    db.add(nova)
    db.commit()
    db.refresh(nova)

    return nova


# ── GET /api/transcricoes ───────────────────────────────

@router.get("/transcricoes", response_model=PaginacaoResponse)
def listar_transcricoes(
    pagina: int = Query(default=1, ge=1, description="Número da página"),
    por_pagina: int = Query(default=20, ge=1, le=100, description="Itens por página"),
    session_id: str | None = Query(default=None, description="Filtrar por sessão"),
    db: Session = Depends(get_db),
):
    """
    Lista transcrições com paginação. Opcionalmente filtra por session_id.
    """
    query = db.query(Transcricao)

    if session_id:
        query = query.filter(Transcricao.session_id == session_id)

    total = query.count()
    total_paginas = max(1, (total + por_pagina - 1) // por_pagina)

    items = (
        query
        .order_by(Transcricao.criado_em.desc())
        .offset((pagina - 1) * por_pagina)
        .limit(por_pagina)
        .all()
    )

    return PaginacaoResponse(
        items=items,
        total=total,
        pagina=pagina,
        por_pagina=por_pagina,
        total_paginas=total_paginas,
    )


# ── GET /api/transcricoes/{id} ──────────────────────────

@router.get("/transcricoes/{transcricao_id}", response_model=TranscricaoResponse)
def obter_transcricao(
    transcricao_id: int,
    db: Session = Depends(get_db),
):
    """Retorna os detalhes de uma transcrição específica."""
    item = db.query(Transcricao).filter(Transcricao.id == transcricao_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Transcrição não encontrada")

    return item


# ── DELETE /api/transcricoes/{id} ────────────────────────

@router.delete("/transcricoes/{transcricao_id}", status_code=204)
def excluir_transcricao(
    transcricao_id: int,
    db: Session = Depends(get_db),
):
    """
    Exclui uma transcrição pelo ID.

    ⚠️ AVISO: Esta operação é irreversível. O registro será permanentemente
    removido do banco de dados.
    """
    item = db.query(Transcricao).filter(Transcricao.id == transcricao_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Transcrição não encontrada")

    db.delete(item)
    db.commit()

    return None


# ── GET /api/estatisticas ───────────────────────────────

@router.get("/estatisticas", response_model=EstatisticasResponse)
def obter_estatisticas(db: Session = Depends(get_db)):
    """Retorna métricas gerais de uso da plataforma."""

    total = db.query(func.count(Transcricao.id)).scalar() or 0

    total_sessoes = (
        db.query(func.count(func.distinct(Transcricao.session_id)))
        .filter(Transcricao.session_id.isnot(None))
        .scalar()
    ) or 0

    media_confianca = db.query(func.avg(Transcricao.confianca)).scalar()
    media_duracao = db.query(func.avg(Transcricao.duracao_ms)).scalar()

    # Transcrições de hoje (UTC)
    hoje_inicio = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    transcricoes_hoje = (
        db.query(func.count(Transcricao.id))
        .filter(Transcricao.criado_em >= hoje_inicio)
        .scalar()
    ) or 0

    return EstatisticasResponse(
        total_transcricoes=total,
        total_sessoes=total_sessoes,
        media_confianca=round(media_confianca, 2) if media_confianca else None,
        media_duracao_ms=round(media_duracao, 1) if media_duracao else None,
        transcricoes_hoje=transcricoes_hoje,
    )
