"""Gera imagens placeholder (300x420) para cada figurinha do catálogo.

Executado uma vez (ou sob demanda), antes de `manage.py importar_catalogo`. Cria um PNG por
`code` em `backend/media/figurinhas/placeholders/<code>.png`, com cor de fundo determinística por
seleção (para reconhecimento visual) e borda vermelha (Torch Red) para as especiais (sufixo `s`).

Independente do Django — usa apenas Pillow e caminhos relativos ao próprio script.
"""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
CATALOGO = BASE_DIR / "contrib" / "fixture" / "panini-wc-2026-catalog.json"
OUT_DIR = BASE_DIR / "media" / "figurinhas" / "placeholders"

# 3:4 exato (300/400) para casar com o container `aspect-[3/4]` do card no frontend:
# assim o `object-cover` não recorta o rodapé (onde fica o nome do jogador).
LARGURA, ALTURA = 300, 400
TORCH_RED = (230, 29, 37)  # #E61D25 — borda das especiais (identidade do álbum)

# Fontes TrueType comuns (multiplataforma); caindo para a bitmap padrão do Pillow
# se nenhuma existir. A bitmap padrão é minúscula — por isso preferimos TrueType.
_FONTES_TTF = ("DejaVuSans-Bold.ttf", "Arialbd.ttf", "arialbd.ttf", "Arial.ttf")


def _fonte(tamanho: int) -> ImageFont.ImageFont:
    """Carrega uma fonte TrueType no tamanho pedido; usa a bitmap padrão como último recurso."""
    for nome in _FONTES_TTF:
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    try:  # Pillow >= 10.1 aceita tamanho na fonte padrão.
        return ImageFont.load_default(tamanho)
    except TypeError:
        return ImageFont.load_default()


def cor_por_selecao(nome: str) -> tuple[int, int, int]:
    """Cor de fundo determinística a partir do nome da seleção."""
    digest = hashlib.md5(nome.encode("utf-8")).hexdigest()
    # Componentes um pouco escurecidas para o texto branco contrastar.
    return tuple(int(digest[i : i + 2], 16) * 3 // 4 for i in (0, 2, 4))


def _texto_centralizado(draw, y, texto, fonte):
    """Desenha `texto` horizontalmente centralizado na largura do card, no topo `y`."""
    draw.text((LARGURA / 2, y), texto, fill="white", font=fonte, anchor="ma")


def _quebrar(texto: str, limite: int) -> list[str]:
    """Quebra `texto` em até 2 linhas de no máximo `limite` caracteres (por palavra)."""
    linhas: list[str] = []
    atual = ""
    for palavra in texto.split():
        candidata = f"{atual} {palavra}".strip()
        if len(candidata) <= limite:
            atual = candidata
        else:
            linhas.append(atual)
            atual = palavra
        if len(linhas) == 2:  # limita a duas linhas
            break
    if atual and len(linhas) < 2:
        linhas.append(atual)
    return linhas[:2]


def gerar() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads(CATALOGO.read_text(encoding="utf-8"))
    stickers = data.get("stickers", [])

    fonte_code = _fonte(64)
    fonte_team = _fonte(24)
    fonte_nome = _fonte(28)

    for item in stickers:
        code, nome, team = item["code"], item["name"], item["team"]
        especial = code.endswith("s")

        img = Image.new("RGB", (LARGURA, ALTURA), cor_por_selecao(team))
        draw = ImageDraw.Draw(img)

        # Código em destaque (grande e centralizado), seleção logo abaixo.
        _texto_centralizado(draw, 132, code, fonte_code)
        _texto_centralizado(draw, 212, team, fonte_team)

        # Nome em até 2 linhas centralizadas, com margem de rodapé confortável
        # (não encosta na borda inferior nem na moldura vermelha das especiais).
        linhas = _quebrar(nome, 18)
        y = ALTURA - 96 - (len(linhas) - 1) * 34
        for linha in linhas:
            _texto_centralizado(draw, y, linha, fonte_nome)
            y += 34

        if especial:
            draw.rectangle([4, 4, LARGURA - 5, ALTURA - 5], outline=TORCH_RED, width=6)

        img.save(OUT_DIR / f"{code}.png")

    return len(stickers)


if __name__ == "__main__":
    total = gerar()
    print(f"{total} placeholders gerados em {OUT_DIR}")
