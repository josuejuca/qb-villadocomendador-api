from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.engine.url import make_url
from urllib.parse import urlencode

from .settings import settings


def _sanitize_database_url_for_asyncpg(database_url: str):
    url = make_url(database_url)
    query = dict(url.query)

    connect_args: dict = {}
    sslmode = query.pop("sslmode", None)
    if sslmode:
        sslmode = str(sslmode).lower()
        if sslmode in {"require", "verify-ca", "verify-full"}:
            connect_args["ssl"] = True
        elif sslmode == "disable":
            connect_args["ssl"] = False

    try:
        url = url.set(query=query)
    except AttributeError:
        # Older SQLAlchemy URL objects may not support .set(); fall back to string rebuild.
        base = str(url).split("?", 1)[0]
        rebuilt = f"{base}?{urlencode(query, doseq=True)}" if query else base
        url = make_url(rebuilt)

    return url, connect_args


_db_url, _connect_args = _sanitize_database_url_for_asyncpg(settings.DATABASE_URL)
engine = create_async_engine(
    _db_url,
    echo=False,
    pool_pre_ping=True,
    connect_args=_connect_args,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with SessionLocal() as session:
        yield session
