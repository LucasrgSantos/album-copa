import pytest
from rest_framework.test import APIClient

from apps.figurinhas.models import Figurinha, Selecao

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


def criar(code, name, team, quantidade=0):
    selecao, _ = Selecao.objects.get_or_create(nome=team)
    fig = Figurinha.objects.create(code=code, name=name, selecao=selecao)
    if quantidade:
        fig.colecao.quantidade = quantidade
        fig.colecao.save()
    return fig


def test_progresso_conta_distintas_nao_repetidas(client):
    criar("BRA1", "Alisson", "Brazil", quantidade=5)  # repetida: conta 1
    criar("BRA2", "Neymar", "Brazil", quantidade=0)
    criar("ARG1", "Messi", "Argentina", quantidade=1)
    criar("ARG2", "Dibu", "Argentina", quantidade=0)

    body = client.get("/api/v1/colecao/progresso/").json()
    assert body["total"] == 4
    assert body["total_possuidas"] == 2  # não 6 (repetida não infla)
    assert body["total_faltantes"] == 2
    assert body["percentual"] == 50.0

    por = {p["team"]: p for p in body["por_team"]}
    assert por["Brazil"]["total"] == 2
    assert por["Brazil"]["possuidas"] == 1
    assert por["Brazil"]["percentual"] == 50.0
    assert por["Argentina"]["possuidas"] == 1


def test_progresso_base_vazia(client):
    body = client.get("/api/v1/colecao/progresso/").json()
    assert body["total"] == 0
    assert body["total_possuidas"] == 0
    assert body["total_faltantes"] == 0
    assert body["percentual"] == 0.0
    assert body["por_team"] == []


def test_progresso_sem_n_mais_1(client, django_assert_num_queries):
    criar("BRA1", "A", "Brazil", quantidade=1)
    criar("ARG1", "B", "Argentina", quantidade=0)
    # Constante: count(total) + count(possuidas) + agregação por seleção.
    with django_assert_num_queries(3):
        client.get("/api/v1/colecao/progresso/")
