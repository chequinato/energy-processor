from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

DATABASE_URL = settings.DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(bind=None):
    """
    Cria as tabelas e aplica ajustes simples de schema em bancos já existentes
    (create_all não adiciona colunas novas em tabelas que já existem).
    """
    bind = bind or engine

    # garante que todos os models estão registrados no metadata
    from app.models import cliente, consumo, upload  # noqa: F401

    Base.metadata.create_all(bind=bind)

    colunas = {c["name"] for c in inspect(bind).get_columns("consumos")}
    if "upload_id" not in colunas:
        with bind.begin() as conn:
            conn.execute(text("ALTER TABLE consumos ADD COLUMN upload_id INTEGER REFERENCES uploads(id)"))
