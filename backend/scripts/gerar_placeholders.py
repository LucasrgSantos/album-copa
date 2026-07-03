"""Gera imagens placeholder (300x420) para cada figurinha do catálogo.

Executado uma vez (ou sob demanda), antes de `manage.py importar_catalogo`. Cria um PNG por
`code` em `backend/media/figurinhas/placeholders/<code>.png`, com cor de fundo determinística por
seleção (para reconhecimento visual) e borda dourada para as figurinhas especiais (sufixo `s`).

Independente do Django — usa apenas Pillow e caminhos relativos ao próprio script.
"""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
CATALOGO = BASE_DIR / "contrib" / "fixture" / "panini-wc-2026-catalog.json"
OUT_DIR = BASE_DIR / "media" / "figurinhas" / "placeholders"

LARGURA, ALTURA = 300, 420
DOURADO = (255, 215, 0)


def cor_por_selecao(nome: str) -> tuple[int, int, int]:
    """Cor de fundo determinística a partir do nome da seleção."""
    digest = hashlib.md5(nome.encode("utf-8")).hexdigest()
    # Componentes um pouco escurecidas para o texto branco contrastar.
    return tuple(int(digest[i : i + 2], 16) * 3 // 4 for i in (0, 2, 4))


def gerar() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads(CATALOGO.read_text(encoding="utf-8"))
    stickers = data.get("stickers", [])
    fonte = ImageFont.load_default()

    for item in stickers:
        code, nome, team = item["code"], item["name"], item["team"]
        especial = code.endswith("s")

        img = Image.new("RGB", (LARGURA, ALTURA), cor_por_selecao(team))
        draw = ImageDraw.Draw(img)
        draw.text((16, 24), code, fill="white", font=fonte)
        draw.text((16, 64), team[:30], fill="white", font=fonte)
        draw.text((16, 104), nome[:30], fill="white", font=fonte)
        if especial:
            draw.rectangle([4, 4, LARGURA - 5, ALTURA - 5], outline=DOURADO, width=6)

        img.save(OUT_DIR / f"{code}.png")

    return len(stickers)


if __name__ == "__main__":
    total = gerar()
    print(f"{total} placeholders gerados em {OUT_DIR}")
