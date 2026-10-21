import os
import tempfile
from pathlib import Path

import pytest

# configura banco e pasta de uploads temporários antes de importar a aplicação
_tmp = Path(tempfile.mkdtemp(prefix="energy-tests-"))
os.environ["DATABASE_URL"] = f"sqlite:///{(_tmp / 'test.db').as_posix()}"
os.environ["UPLOAD_DIR"] = str(_tmp / "uploads")
os.environ["REDIS_URL"] = "redis://localhost:6399/0"

from fastapi.testclient import TestClient  # noqa: E402

from app.core import redis_client as redis_module  # noqa: E402
from app.core.database import Base, engine, init_db  # noqa: E402
from main import app  # noqa: E402


class FakeRedis:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, ttl, value):
        self.store[key] = value

    def delete(self, *keys):
        for key in keys:
            self.store.pop(key, None)

    def ping(self):
        return True


@pytest.fixture
def fake_redis(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(redis_module, "redis_client", fake)
    return fake


@pytest.fixture
def client(fake_redis):
    Base.metadata.drop_all(bind=engine)
    init_db()
    with TestClient(app) as c:
        yield c


CSV_VALIDO = (
    "cliente,consumo_kwh,preco_mwh,data\n"
    "Alpha,1000,200,01/01/2026\n"
    "Beta,500,300,15/01/2026\n"
    "Alpha,2000,200,01/02/2026\n"
)


@pytest.fixture
def csv_valido():
    return CSV_VALIDO.encode()
