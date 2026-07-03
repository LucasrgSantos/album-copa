"""Importa o catálogo de figurinhas a partir do JSON versionado.

Idempotente por `code` (RF-004/RF-012) e por `nome` da seleção (RF-013): reexecuções
atualizam, não duplicam, e nunca apagam dados.
"""

import json
from pathlib import Path

import structlog
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.figurinhas.models import Figurinha, Selecao

logger = structlog.get_logger(__name__)

DEFAULT_ARQUIVO = (
    Path(settings.BASE_DIR) / "contrib" / "fixture" / "panini-wc-2026-catalog.json"
)


class Command(BaseCommand):
    help = "Importa o catálogo de figurinhas (idempotente por code)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--arquivo",
            default=str(DEFAULT_ARQUIVO),
            help="Caminho do JSON de catálogo (default: contrib/fixture/panini-wc-2026-catalog.json).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simula a carga e reporta contagens sem gravar.",
        )

    def handle(self, *args, **options):
        arquivo = Path(options["arquivo"])
        dry_run = options["dry_run"]

        if not arquivo.exists():
            raise CommandError(f"Arquivo não encontrado: {arquivo}")
        try:
            data = json.loads(arquivo.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise CommandError(f"JSON inválido em {arquivo}: {exc}") from exc

        stickers = data.get("stickers", [])
        if not stickers:
            raise CommandError("Nenhuma figurinha encontrada na chave 'stickers'.")

        placeholder_dir = Path(settings.MEDIA_ROOT) / "figurinhas" / "placeholders"
        counters = {"selecoes": 0, "criadas": 0, "atualizadas": 0, "placeholders": 0}

        with transaction.atomic():
            for item in stickers:
                code = item["code"]
                nome = item["name"]
                team = item["team"]
                especial = code.endswith("s")

                selecao, sel_created = Selecao.objects.get_or_create(nome=team)
                if sel_created:
                    counters["selecoes"] += 1

                figurinha, created = Figurinha.objects.update_or_create(
                    code=code,
                    defaults={"name": nome, "selecao": selecao, "especial": especial},
                )
                counters["criadas" if created else "atualizadas"] += 1

                # Associa o placeholder (sem copiar o arquivo) quando não há imagem.
                if not figurinha.imagem:
                    rel = f"figurinhas/placeholders/{code}.png"
                    if (placeholder_dir / f"{code}.png").exists():
                        figurinha.imagem.name = rel
                        figurinha.save(update_fields=["imagem"])
                        counters["placeholders"] += 1

            canonical = data.get("canonicalCount")
            total = len(stickers)
            if canonical is not None and canonical != total:
                self.stdout.write(
                    self.style.WARNING(
                        f"canonicalCount ({canonical}) difere do total carregado ({total})."
                    )
                )

            if dry_run:
                transaction.set_rollback(True)

        logger.info(
            "importar_catalogo", dry_run=dry_run, total=len(stickers), **counters
        )
        resumo = (
            f"{'[dry-run] ' if dry_run else ''}"
            f"{counters['selecoes']} seleções novas · "
            f"{counters['criadas']} figurinhas criadas · "
            f"{counters['atualizadas']} atualizadas · "
            f"{counters['placeholders']} placeholders associados."
        )
        self.stdout.write(self.style.SUCCESS(resumo))
