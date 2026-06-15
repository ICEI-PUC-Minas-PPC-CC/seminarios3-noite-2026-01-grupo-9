"""
schemas.py — Schemas Pydantic para validação de entrada e saída da API.

Todos os exemplos usam dados fictícios (mock). Nenhum dado real é referenciado.
A validação via Pydantic protege contra injeção de dados maliciosos.
"""

from datetime import datetime

from pydantic import BaseModel, Field


# ── Entrada ─────────────────────────────────────────────

class TranscricaoCreate(BaseModel):
    """Payload enviado pelo frontend ao criar uma transcrição."""

    texto: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Texto transcrito pela Web Speech API",
        json_schema_extra={"example": "Olá, tudo bem? Essa é uma frase de teste."},
    )
    idioma: str = Field(
        default="pt-BR",
        max_length=10,
        description="Código BCP-47 do idioma",
        json_schema_extra={"example": "pt-BR"},
    )
    duracao_ms: int | None = Field(
        default=None,
        ge=0,
        le=600_000,  # Máximo: 10 minutos
        description="Duração da gravação em milissegundos",
        json_schema_extra={"example": 3200},
    )
    confianca: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confiança do reconhecimento (0 a 1)",
        json_schema_extra={"example": 0.92},
    )
    session_id: str | None = Field(
        default=None,
        max_length=36,
        description="UUID da sessão do frontend",
        json_schema_extra={"example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"},
    )


# ── Saída ───────────────────────────────────────────────

class TranscricaoResponse(BaseModel):
    """Representação de uma transcrição retornada pela API."""

    id: int
    texto: str
    idioma: str
    duracao_ms: int | None
    confianca: float | None
    session_id: str | None
    criado_em: datetime

    model_config = {"from_attributes": True}


class PaginacaoResponse(BaseModel):
    """Resposta paginada de transcrições."""

    items: list[TranscricaoResponse]
    total: int
    pagina: int
    por_pagina: int
    total_paginas: int


class EstatisticasResponse(BaseModel):
    """Métricas gerais de uso da plataforma."""

    total_transcricoes: int
    total_sessoes: int
    media_confianca: float | None
    media_duracao_ms: float | None
    transcricoes_hoje: int
