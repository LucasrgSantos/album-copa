"""Popula `Selecao.bandeira` com a URL da bandeira de cada país (flagcdn.com).

Idempotente: mapeia o nome da seleção → código ISO 3166-1 alpha-2 → URL do flagcdn.
Seções que não são países (ex.: "We Are Panini", "FIFA World Cup 2026") ficam sem
bandeira — devem ser preenchidas manualmente no django-admin (RF/decisão do produto).

Uso:
    python manage.py popular_bandeiras            # grava
    python manage.py popular_bandeiras --dry-run  # só reporta
"""

import structlog
from django.core.management.base import BaseCommand

from apps.figurinhas.models import Selecao

logger = structlog.get_logger(__name__)

# Tamanho da imagem no flagcdn (w80 = ~80px de largura, leve e nítido em telas retina).
_BASE_URL = "https://flagcdn.com/w80/{iso}.png"

# Nome da seleção (exatamente como no catálogo) → ISO 3166-1 alpha-2 (flagcdn).
# Subdivisões do Reino Unido usam os códigos especiais gb-eng / gb-sct do flagcdn.
TEAM_ISO = {
    "Algeria": "dz",
    "Argentina": "ar",
    "Australia": "au",
    "Austria": "at",
    "Belgium": "be",
    "Bosnia and Herzegovina": "ba",
    "Brazil": "br",
    "Canada": "ca",
    "Cape Verde": "cv",
    "Colombia": "co",
    "Congo DR": "cd",
    "Croatia": "hr",
    "Curaçao": "cw",
    "Czechia": "cz",
    "Ecuador": "ec",
    "Egypt": "eg",
    "England": "gb-eng",
    "France": "fr",
    "Germany": "de",
    "Ghana": "gh",
    "Haiti": "ht",
    "Iran": "ir",
    "Iraq": "iq",
    "Ivory Coast": "ci",
    "Japan": "jp",
    "Jordan": "jo",
    "Mexico": "mx",
    "Morocco": "ma",
    "Netherlands": "nl",
    "New Zealand": "nz",
    "Norway": "no",
    "Panama": "pa",
    "Paraguay": "py",
    "Portugal": "pt",
    "Qatar": "qa",
    "Saudi Arabia": "sa",
    "Scotland": "gb-sct",
    "Senegal": "sn",
    "South Africa": "za",
    "South Korea": "kr",
    "Spain": "es",
    "Sweden": "se",
    "Switzerland": "ch",
    "Tunisia": "tn",
    "Türkiye": "tr",
    "USA": "us",
    "Uruguay": "uy",
    "Uzbekistan": "uz",
}


class Command(BaseCommand):
    help = "Popula Selecao.bandeira com a URL da bandeira (flagcdn) por país."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simula e reporta as contagens sem gravar.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        atualizadas = 0
        sem_mapa = []

        for selecao in Selecao.objects.all():
            iso = TEAM_ISO.get(selecao.nome)
            if not iso:
                sem_mapa.append(selecao.nome)
                continue
            url = _BASE_URL.format(iso=iso)
            if selecao.bandeira != url:
                selecao.bandeira = url
                if not dry_run:
                    selecao.save(update_fields=["bandeira", "alterado_em"])
                atualizadas += 1

        logger.info(
            "popular_bandeiras",
            dry_run=dry_run,
            atualizadas=atualizadas,
            sem_bandeira=len(sem_mapa),
        )
        resumo = (
            f"{'[dry-run] ' if dry_run else ''}{atualizadas} bandeiras definidas · "
            f"{len(sem_mapa)} seleções sem mapeamento (preencher no admin): "
            f"{', '.join(sorted(sem_mapa)) or '—'}."
        )
        self.stdout.write(self.style.SUCCESS(resumo))
