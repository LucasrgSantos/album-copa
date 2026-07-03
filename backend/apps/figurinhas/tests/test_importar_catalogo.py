import json

import pytest
from django.core.management import call_command

from apps.figurinhas.models import ColecaoFigurinha, Figurinha, Selecao

pytestmark = pytest.mark.django_db

CATALOGO = {
    "canonicalCount": 4,
    "stickers": [
        {"code": "BRA1", "name": "Jogador A", "team": "Brazil"},
        {"code": "BRA2", "name": "Jogador B", "team": "Brazil"},
        {"code": "GER2s", "name": "Especial C", "team": "Germany"},
        {"code": "00", "name": "Panini Logo", "team": "We Are Panini"},
    ],
}


def _arquivo(tmp_path, data=CATALOGO):
    caminho = tmp_path / "catalogo.json"
    caminho.write_text(json.dumps(data), encoding="utf-8")
    return str(caminho)


def test_carga_cria_selecoes_figurinhas_e_posses(tmp_path, settings):
    settings.MEDIA_ROOT = str(tmp_path / "media")
    call_command("importar_catalogo", arquivo=_arquivo(tmp_path))

    assert Selecao.objects.count() == 3  # Brazil, Germany, We Are Panini
    assert Figurinha.objects.count() == 4
    assert ColecaoFigurinha.objects.count() == 4
    assert ColecaoFigurinha.objects.filter(quantidade=0).count() == 4


def test_especial_derivado_e_code_preservado(tmp_path, settings):
    settings.MEDIA_ROOT = str(tmp_path / "media")
    call_command("importar_catalogo", arquivo=_arquivo(tmp_path))

    especial = Figurinha.objects.get(code="GER2s")
    assert especial.especial is True
    assert especial.selecao.nome == "Germany"
    assert Figurinha.objects.get(code="00").especial is False


def test_reexecucao_idempotente(tmp_path, settings):
    settings.MEDIA_ROOT = str(tmp_path / "media")
    arquivo = _arquivo(tmp_path)
    call_command("importar_catalogo", arquivo=arquivo)
    call_command("importar_catalogo", arquivo=arquivo)

    assert Selecao.objects.count() == 3
    assert Figurinha.objects.count() == 4
    assert ColecaoFigurinha.objects.count() == 4


def test_dry_run_nao_grava(tmp_path, settings):
    settings.MEDIA_ROOT = str(tmp_path / "media")
    call_command("importar_catalogo", "--dry-run", arquivo=_arquivo(tmp_path))
    assert Figurinha.objects.count() == 0
    assert Selecao.objects.count() == 0


def test_placeholder_associado_quando_existe(tmp_path, settings):
    settings.MEDIA_ROOT = str(tmp_path / "media")
    ph_dir = tmp_path / "media" / "figurinhas" / "placeholders"
    ph_dir.mkdir(parents=True)
    (ph_dir / "BRA1.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    call_command("importar_catalogo", arquivo=_arquivo(tmp_path))

    assert (
        Figurinha.objects.get(code="BRA1").imagem.name
        == "figurinhas/placeholders/BRA1.png"
    )
    # RF-005 / caso de borda: sem placeholder, figurinha fica sem imagem, sem abortar.
    assert not Figurinha.objects.get(code="BRA2").imagem
    assert Figurinha.objects.count() == 4


def test_arquivo_inexistente_falha(tmp_path):
    from django.core.management.base import CommandError

    with pytest.raises(CommandError):
        call_command("importar_catalogo", arquivo=str(tmp_path / "nao_existe.json"))
