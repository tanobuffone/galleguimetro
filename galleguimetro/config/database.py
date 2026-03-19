from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/galleguimetro_db")

# URL async (reemplazar postgresql:// con postgresql+asyncpg://)
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Base declarativa para modelos ORM
Base = declarative_base()

# Motor síncrono (para migraciones con Alembic)
sync_engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQLALCHEMY_ECHO", "False").lower() == "true",
    pool_pre_ping=True,
    pool_recycle=300,
)

SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Motor asíncrono (para la aplicación FastAPI)
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=os.getenv("SQLALCHEMY_ECHO", "False").lower() == "true",
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=20,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """Dependencia FastAPI para obtener sesión async de base de datos."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db():
    """Sesión síncrona para scripts y migraciones."""
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Crea todas las tablas (síncrono, para scripts)."""
    Base.metadata.create_all(bind=sync_engine)


def drop_tables():
    """Elimina todas las tablas. SOLO DESARROLLO."""
    Base.metadata.drop_all(bind=sync_engine)
