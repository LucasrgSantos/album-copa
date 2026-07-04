import pytest
from rest_framework.test import APIClient

from apps.figurinhas.models import Figurinha, Selecao

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


def criar(code, name, team, especial=False, quantidade=0):
    selecao, _ = Selecao.objects.get_or_create(nome=team)
    fig = Figurinha.objects.create(
        code=code, name=name, selecao=selecao, especial=especial
    )
    if quantidade:
        fig.colecao.quantidade = quantidade
        fig.colecao.save()
    return fig


@pytest.fixture
def catalogo():
    criar("BRA1", "Alisson", "Brazil", quantidade=2)
    criar("BRA2", "Neymar", "Brazil", quantidade=0)
    criar("ARG1", "Messi", "Argentina", quantidade=1)
    criar("GER2s", "Escudo Alemanha", "Germany", especial=True, quantidade=0)


def test_lista_paginada_com_campos(client, catalogo):
    resp = client.get("/api/v1/figurinhas/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 4
    assert "results" in body
    item = next(i for i in body["results"] if i["code"] == "BRA1")
    assert set(item) >= {
        "code",
        "name",
        "team",
        "especial",
        "imagem",
        "quantidade",
        "possuo",
    }
    assert item["team"] == "Brazil"
    assert item["quantidade"] == 2
    assert item["possuo"] is True
    assert item["imagem"] is None  # sem imagem cadastrada


def test_possuo_coerente_com_quantidade(client, catalogo):
    resultados = client.get("/api/v1/figurinhas/").json()["results"]
    for item in resultados:
        assert item["possuo"] is (item["quantidade"] > 0)


def test_filtro_team(client, catalogo):
    resp = client.get("/api/v1/figurinhas/?team=Brazil")
    assert {i["code"] for i in resp.json()["results"]} == {"BRA1", "BRA2"}


def test_filtro_status(client, catalogo):
    falta = client.get("/api/v1/figurinhas/?status=falta").json()["results"]
    assert {i["code"] for i in falta} == {"BRA2", "GER2s"}
    tenho = client.get("/api/v1/figurinhas/?status=tenho").json()["results"]
    assert {i["code"] for i in tenho} == {"BRA1", "ARG1"}


def test_filtro_busca(client, catalogo):
    resp = client.get("/api/v1/figurinhas/?busca=messi")
    assert {i["code"] for i in resp.json()["results"]} == {"ARG1"}
    # busca também casa por code
    resp = client.get("/api/v1/figurinhas/?busca=GER2s")
    assert {i["code"] for i in resp.json()["results"]} == {"GER2s"}


def test_filtro_especial(client, catalogo):
    resp = client.get("/api/v1/figurinhas/?especial=true")
    assert {i["code"] for i in resp.json()["results"]} == {"GER2s"}


def test_filtros_combinados(client, catalogo):
    resp = client.get("/api/v1/figurinhas/?team=Brazil&status=tenho")
    assert {i["code"] for i in resp.json()["results"]} == {"BRA1"}


def test_detalhe(client, catalogo):
    resp = client.get("/api/v1/figurinhas/GER2s/")
    assert resp.status_code == 200
    assert resp.json()["especial"] is True


def test_detalhe_inexistente_retorna_erro_padrao(client, catalogo):
    resp = client.get("/api/v1/figurinhas/ZZZ9/")
    assert resp.status_code == 404
    body = resp.json()
    assert body["code"] == "not_found"
    assert "detail" in body


def test_times(client, catalogo):
    resp = client.get("/api/v1/times/")
    assert resp.status_code == 200
    body = resp.json()
    assert {t["team"] for t in body} == {"Argentina", "Brazil", "Germany"}
    # Toda opção traz o campo bandeira (vazio até ser populado).
    assert all("bandeira" in t for t in body)


def test_times_com_bandeira_populada(client, catalogo):
    from django.core.management import call_command

    call_command("popular_bandeiras")
    por_team = {t["team"]: t["bandeira"] for t in client.get("/api/v1/times/").json()}
    assert por_team["Brazil"] == "https://flagcdn.com/w80/br.png"
    assert por_team["Argentina"] == "https://flagcdn.com/w80/ar.png"


def test_listagem_em_uma_requisicao_sem_n_mais_1(client, catalogo, django_assert_num_queries):
    # Catálogo inteiro em uma única query (select_related traz selecao/colecao),
    # sem query extra de count — a paginação devolve tudo em uma página.
    with django_assert_num_queries(1):
        resp = client.get("/api/v1/figurinhas/")
    body = resp.json()
    assert body["count"] == 4
    assert body["next"] is None
    assert len(body["results"]) == 4


def test_ordenacao_por_numeracao(client):
    # BRA10 deve vir DEPOIS de BRA2 (ordenação natural, não lexicográfica).
    for code in ("BRA10", "BRA2", "BRA1"):
        criar(code, code, "Brazil")
    resultados = client.get("/api/v1/figurinhas/?team=Brazil").json()["results"]
    assert [i["code"] for i in resultados] == ["BRA1", "BRA2", "BRA10"]
