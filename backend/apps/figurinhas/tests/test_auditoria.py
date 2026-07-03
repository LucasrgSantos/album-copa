import pytest
from auditlog.models import LogEntry

from apps.figurinhas.models import Figurinha, Selecao

pytestmark = pytest.mark.django_db


def test_alteracao_de_quantidade_gera_logentry_com_anterior_e_novo():
    selecao = Selecao.objects.create(nome="Brazil")
    figurinha = Figurinha.objects.create(code="BRA1", name="A", selecao=selecao)
    colecao = figurinha.colecao

    colecao.quantidade = 5
    colecao.save()

    entries = LogEntry.objects.get_for_object(colecao)
    assert entries.exists()

    changes = entries.latest("timestamp").changes_dict
    assert "quantidade" in changes
    anterior, novo = changes["quantidade"]
    assert str(anterior) == "0"
    assert str(novo) == "5"
