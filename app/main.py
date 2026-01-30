from fastapi import FastAPI, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .db import Base, engine, get_db
from .models import NpsResponse
from .schemas import NpsCreate, NpsOut
from .settings import settings
from .emailer import render_template, send_email_html

app = FastAPI(title="Quadraimob NPS API", version="1.0.0")

@app.on_event("startup")
async def on_startup():
    # cria tabela automaticamente (para produção, prefira Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def check_api_key(x_api_key: str | None):
    if settings.API_KEY:
        if not x_api_key or x_api_key != settings.API_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/api/v1/nps", response_model=NpsOut)
async def create_nps(
    payload: NpsCreate,
    db: AsyncSession = Depends(get_db),
):

    row = NpsResponse(
        nome=payload.nome.strip(),
        email=str(payload.email).lower(),
        telefone=payload.telefone.strip(),
        imovel_unidade=payload.imovel_unidade.strip(),
        avaliacao_processo_compra=payload.avaliacao_processo_compra,
        avaliacao_corretor=payload.avaliacao_corretor,
        avaliacao_gerente=payload.avaliacao_gerente,
        nps=payload.nps,
        justificativa=(payload.justificativa.strip() if payload.justificativa else None),
    )

    db.add(row)
    await db.commit()
    await db.refresh(row)

    html = render_template("autoresposta.jinja", {"nome": row.nome})

    try:
        await send_email_html(
            to_email=row.email,
            subject="Recebemos sua avaliação — quadraimob",
            html=html,
        )
    except Exception:
        pass

    return NpsOut(id=row.id, created_at=str(row.created_at))
