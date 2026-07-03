import pytest
from auditlog.models import LogEntry
from rest_framework.test import APIClient

from apps.figurinhas.models import Figurinha, Selecao

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def fig():
    selecao = Selecao.objects.create(nome="Brazil")
    return Figurinha.objects.create(code="BRA1", name="Alisson", selecao=selecao)


def test_definir_quantidade(client, fig):
    resp = client.patch(
        "/api/v1/figurinhas/BRA1/quantidade/", {"quantidade": 3}, format="json"
    )
    assert resp.status_code == 200
    assert resp.json()["quantidade"] == 3
    assert resp.json()["possuo"] is True
    # reflete na consulta seguinte
    assert client.get("/api/v1/figurinhas/BRA1/").json()["quantidade"] == 3


def test_definir_quantidade_negativa_rejeitada_preserva_valor(client, fig):
    fig.colecao.quantidade = 2
    fig.colecao.save()
    resp = client.patch(
        "/api/v1/figurinhas/BRA1/quantidade/", {"quantidade": -1}, format="json"
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "invalid"
    fig.colecao.refresh_from_db()
    assert fig.colecao.quantidade == 2


def test_incrementar(client, fig):
    resp = client.post("/api/v1/figurinhas/BRA1/incrementar/")
    assert resp.status_code == 200
    assert resp.json()["quantidade"] == 1


def test_decrementar_piso_zero(client, fig):
    resp = client.post("/api/v1/figurinhas/BRA1/decrementar/")
    assert resp.status_code == 200
    assert resp.json()["quantidade"] == 0


def test_decrementar(client, fig):
    fig.colecao.quantidade = 2
    fig.colecao.save()
    resp = client.post("/api/v1/figurinhas/BRA1/decrementar/")
    assert resp.json()["quantidade"] == 1


def test_acao_de_escrita_ignora_filtros_da_query(client, fig):
    # Regressão: com a figurinha em "tenho", um incremento carregando ?status=falta
    # (filtro herdado da lista) não pode dar 404 — a ação resolve só por code.
    fig.colecao.quantidade = 1
    fig.colecao.save()
    resp = client.post("/api/v1/figurinhas/BRA1/incrementar/?status=falta")
    assert resp.status_code == 200
    assert resp.json()["quantidade"] == 2


def test_api_publica_dispensa_autenticacao(client, fig):
    # Regressão: apesar do padrão global IsAuthenticated, as views públicas
    # fazem opt-in de AllowAny; sem credenciais deve responder 200 (não 401/403).
    assert client.get("/api/v1/figurinhas/").status_code == 200
    assert client.get("/api/v1/figurinhas/BRA1/").status_code == 200
    assert (
        client.post("/api/v1/figurinhas/BRA1/incrementar/").status_code == 200
    )


def test_alteracao_via_api_gera_auditlog(client, fig):
    client.patch(
        "/api/v1/figurinhas/BRA1/quantidade/", {"quantidade": 4}, format="json"
    )
    entries = LogEntry.objects.get_for_object(fig.colecao)
    assert entries.exists()
    changes = entries.latest("timestamp").changes_dict
    assert "quantidade" in changes
    _, novo = changes["quantidade"]
    assert str(novo) == "4"
