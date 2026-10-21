from app.core.config import settings


def _upload(client, content, filename="dados.csv"):
    return client.post("/api/upload", files={"file": (filename, content, "text/csv")})


def test_health(client):
    resp = client.get("/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "database": "ok", "cache": "ok"}


def test_upload_e_relatorios(client, csv_valido):
    resp = _upload(client, csv_valido)

    assert resp.status_code == 200
    body = resp.json()
    assert body["metrics"] == {"total_consumo": 3500.0, "total_custo": 750.0}
    assert body["upload_id"] == 1

    relatorios = {r["cliente"]: r for r in client.get("/api/relatorios").json()}
    assert relatorios["Alpha"]["total_consumo"] == 3000
    assert relatorios["Beta"]["total_custo"] == 150

    resumo = client.get("/api/relatorios/resumo").json()
    assert resumo == {"total_clientes": 2, "total_geral_consumo": 3500.0, "total_geral_custo": 750.0}

    assert client.get("/api/clientes").json() == ["Alpha", "Beta"]


def test_consumos_filtros(client, csv_valido):
    _upload(client, csv_valido)

    assert len(client.get("/api/consumos").json()) == 3
    assert len(client.get("/api/consumos", params={"cliente": "Alpha"}).json()) == 2

    filtrado = client.get("/api/consumos", params={"data_inicio": "2026-01-10"}).json()
    assert [c["cliente"] for c in filtrado] == ["Beta", "Alpha"]


def test_upload_invalido_retorna_400(client):
    resp = _upload(client, b"cliente,consumo_kwh\nA,1\n")

    assert resp.status_code == 400
    assert "preco_mwh" in resp.json()["detail"]
    assert client.get("/api/uploads").json() == []


def test_upload_extensao_nao_suportada(client):
    resp = _upload(client, b"qualquer", "dados.txt")

    assert resp.status_code == 400


def test_upload_muito_grande(client, monkeypatch):
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 0)

    resp = _upload(client, b"cliente,consumo_kwh,preco_mwh\nA,1,1\n")

    assert resp.status_code == 413


def test_upload_nome_com_path_traversal(client, csv_valido, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))

    resp = _upload(client, csv_valido, "../../malicioso.csv")

    assert resp.status_code == 200
    assert resp.json()["filename"] == "malicioso.csv"
    assert [p.name for p in tmp_path.iterdir()] == ["1_malicioso.csv"]


def test_delete_upload_remove_consumos(client, csv_valido):
    first = _upload(client, csv_valido).json()["upload_id"]
    _upload(client, csv_valido)

    assert len(client.get("/api/consumos").json()) == 6

    resp = client.delete(f"/api/uploads/{first}")

    assert resp.status_code == 200
    assert resp.json()["consumos_removidos"] == 3
    assert len(client.get("/api/consumos").json()) == 3
    assert len(client.get("/api/uploads").json()) == 1


def test_delete_upload_inexistente(client):
    assert client.delete("/api/uploads/999").status_code == 404


def test_cache_invalidado_apos_upload(client, csv_valido, fake_redis):
    assert client.get("/api/relatorios").json() == []
    assert "relatorios" in fake_redis.store

    _upload(client, csv_valido)

    assert "relatorios" not in fake_redis.store
    assert len(client.get("/api/relatorios").json()) == 2


def test_api_funciona_sem_redis(client, csv_valido, monkeypatch):
    import redis

    from app.core import redis_client as redis_module

    class RedisFora:
        def __getattr__(self, name):
            def falha(*args, **kwargs):
                raise redis.ConnectionError("fora do ar")
            return falha

    monkeypatch.setattr(redis_module, "redis_client", RedisFora())

    assert _upload(client, csv_valido).status_code == 200
    assert len(client.get("/api/relatorios").json()) == 2
    assert client.get("/health").json()["cache"] == "indisponível"
