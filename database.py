import os
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/nexus")

# Garante o driver assíncrono (asyncpg), mesmo se a URL vier sem ele
# (ex: Replit/Heroku/Supabase costumam fornecer "postgres://..." ou "postgresql://...")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# O asyncpg não aceita o parâmetro "sslmode" (isso é da lib psycopg2).
# Se a URL vier com "?sslmode=require" (comum em strings copiadas do Supabase),
# removemos da URL e ativamos SSL via connect_args, que é o formato que o asyncpg entende.
connect_args = {}
parts = urlsplit(DATABASE_URL)
query_pairs = parse_qsl(parts.query, keep_blank_values=True)
filtered_pairs = []
for key, value in query_pairs:
    if key.lower() == "sslmode":
        if value.lower() not in ("disable", "allow"):
            connect_args["ssl"] = "require"
    else:
        filtered_pairs.append((key, value))
DATABASE_URL = urlunsplit(parts._replace(query=urlencode(filtered_pairs)))

engine = create_async_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    await engine.dispose()

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
