from pydantic import BaseModel, EmailStr, Field
from typing import Literal

Satisfacao = Literal[
    "Muito insatisfeito",
    "Insatisfeito",
    "Indiferente",
    "Satisfeito",
    "Muito satisfeito",
]

class NpsCreate(BaseModel):
    # OBRIGATÓRIOS
    nome: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    telefone: str = Field(..., min_length=8, max_length=40)
    imovel_unidade: str = Field(..., min_length=2, max_length=180)
    avaliacao_processo_compra: Satisfacao

    # OPCIONAIS
    avaliacao_corretor: Satisfacao | None = None
    avaliacao_gerente: Satisfacao | None = None
    nps: int | None = Field(default=None, ge=0, le=10)
    justificativa: str | None = Field(default=None, max_length=4000)


class NpsOut(BaseModel):
    id: int
    created_at: str
