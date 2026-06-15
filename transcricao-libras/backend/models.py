"""
models.py — Modelos do banco de dados (ORM SQLAlchemy).

Todos os campos usam tipos seguros. Nenhum dado sensível é armazenado
(sem senhas, sem PII). O campo ip_hash é um hash SHA-256 anonimizado.
"""

import hashlib
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from database import Base


class Transcricao(Base):
    """
    Representa uma transcrição de voz capturada pela Web Speech API.

    Campos:
    - texto:      O texto final reconhecido pelo navegador.
    - idioma:     Código BCP-47 do idioma (ex: "pt-BR").
    - duracao_ms: Duração aproximada da gravação em milissegundos.
    - confianca:  Nível de confiança do reconhecimento (0.0 a 1.0).
    - session_id: UUID gerado no frontend para agrupar transcrições de uma sessão.
    - ip_hash:    Hash SHA-256 do IP do cliente (anonimizado, para analytics).
    - criado_em:  Timestamp UTC de criação (gerado automaticamente).
    """

    __tablename__ = "transcricoes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    texto = Column(Text, nullable=False)
    idioma = Column(String(10), nullable=False, default="pt-BR")
    duracao_ms = Column(Integer, nullable=True)
    confianca = Column(Float, nullable=True)
    session_id = Column(String(36), nullable=True, index=True)
    ip_hash = Column(String(64), nullable=True)
    criado_em = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        preview = self.texto[:40] + "..." if len(self.texto) > 40 else self.texto
        return f"<Transcricao(id={self.id}, texto='{preview}')>"

    @staticmethod
    def anonimizar_ip(ip: str) -> str:
        """Gera um hash SHA-256 do IP para anonimização."""
        return hashlib.sha256(ip.encode("utf-8")).hexdigest()
