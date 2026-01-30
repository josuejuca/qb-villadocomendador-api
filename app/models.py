from sqlalchemy import String, Integer, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class NpsResponse(Base):
    __tablename__ = "nps_responses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # OBRIGATÓRIOS
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    telefone: Mapped[str] = mapped_column(String(40), nullable=False)
    imovel_unidade: Mapped[str] = mapped_column(String(180), nullable=False)
    avaliacao_processo_compra: Mapped[str] = mapped_column(String(40), nullable=False)

    # OPCIONAIS
    avaliacao_corretor: Mapped[str | None] = mapped_column(String(40), nullable=True)
    avaliacao_gerente: Mapped[str | None] = mapped_column(String(40), nullable=True)
    nps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    justificativa: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
