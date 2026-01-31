from fastapi import FastAPI, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi.middleware.cors import CORSMiddleware # CORS

from .db import Base, engine, get_db
from .models import NpsResponse
from .schemas import NpsCreate, NpsOut
from .settings import settings
from .emailer import render_template, send_email_html
import anyio
from urllib.parse import urlencode
from urllib.request import Request, urlopen

app = FastAPI(title="Quadraimob NPS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens (você pode restringir se necessário)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

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

    google_form_url = settings.GOOGLE_FORMS_FORM_RESPONSE_URL
    if google_form_url:
        google_form_data = {
            "entry.2044555968": payload.nome.strip(),
            "entry.983740490": row.email,
            "entry.662355508": payload.telefone.strip(),
            "entry.734581006": payload.imovel_unidade.strip(),
            "entry.259065602": payload.avaliacao_corretor or "",
            "entry.1384914731": payload.avaliacao_gerente or "",
            "entry.918578897": payload.avaliacao_processo_compra,
            "entry.482635285": "" if payload.nps is None else str(payload.nps),
            "entry.1592445622": payload.justificativa.strip() if payload.justificativa else "",
        }
    
        # https://docs.google.com/forms/d/e/1FAIpQLSeCJd8h4HxmCtmhxV3HKhAu3XQSsWfxXFhacOT2nH_j9rdWbQ/viewform?usp=pp_url
        # &entry.2044555968=NOME
        # &entry.983740490=EMAIL
        # &entry.662355508=TELEFONE
        # &entry.734581006=IMOVEL
        # &entry.259065602=Muito+insatisfeito
        # &entry.1384914731=Insatisfeito
        # &entry.918578897=Insatisfeito
        # &entry.482635285=10
        # &entry.1592445622=JUSTIFICATIVA
        # Envie os dados para o Formulário Google    

        def _post_google_form() -> None:
            data = urlencode(google_form_data).encode("utf-8")
            req = Request(
                google_form_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with urlopen(req, timeout=5) as _:
                return None

        try:
            await anyio.to_thread.run_sync(_post_google_form)
        except Exception:
            pass
    
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
