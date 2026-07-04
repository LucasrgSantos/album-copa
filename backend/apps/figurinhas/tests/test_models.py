import pytest

from apps.figurinhas.models import ColecaoFigurinha, Figurinha, Selecao

pytestmark = pytest.mark.django_db


def _figurinha(code="BRA1", nome="Jogador", team="Brazil", especial=False):
    selecao, _ = Selecao.objects.get_or_create(nome=team)
    return Figurinha.objects.create(
        code=code, name=nome, selecao=selecao, especial=especial
    )


def test_signal_cria_colecao_zerada():
    fig = _figurinha()
    colecao = ColecaoFigurinha.objects.get(figurinha=fig)
    assert colecao.quantidade == 0
    assert ColecaoFigurinha.objects.count() == 1


def test_signal_idempotente_nao_duplica_colecao():
    fig = _figurinha()
    fig.name = "Outro nome"
    fig.save()  # segundo save não deve criar nova posse
    assert ColecaoFigurinha.objects.filter(figurinha=fig).count() == 1


def test_property_tenho():
    fig = _figurinha()
    colecao = fig.colecao
    assert colecao.tenho is False
    colecao.quantidade = 3
    colecao.save()
    assert colecao.tenho is True


def test_campos_base_presentes():
    fig = _figurinha()
    # Campos herdados de ModelPadrao / ModelPadraoAuditavel.
    assert fig.criado_em is not None
    assert fig.alterado_em is not None
    assert hasattr(fig, "criado_por")
    assert hasattr(fig, "alterado_por")


def test_selecao_herda_model_padrao_auditavel():
    selecao = Selecao.objects.create(nome="Argentina")
    assert selecao.criado_em is not None
    assert selecao.alterado_em is not None
    # `bandeira` é editável no admin → Selecao é auditável (tem autoria).
    assert hasattr(selecao, "criado_por")
    assert hasattr(selecao, "alterado_por")
    assert selecao.bandeira == ""
