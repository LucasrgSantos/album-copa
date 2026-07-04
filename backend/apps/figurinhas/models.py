from django.db import models
from django.utils.html import format_html

from utils.models import ModelPadraoAuditavel


class Selecao(ModelPadraoAuditavel):
    """Seleção nacional ou seção especial à qual as figurinhas pertencem.

    Populada pela importação do catálogo, mas a `bandeira` é editável no admin
    (preenchimento manual para as seções que não são países) → herda
    `ModelPadraoAuditavel`.
    """

    nome = models.CharField("nome", max_length=64, unique=True)
    bandeira = models.URLField(
        "bandeira",
        max_length=255,
        blank=True,
        default="",
        help_text="URL da imagem da bandeira do país (vazio para seções sem bandeira).",
    )

    class Meta:
        ordering = ["nome"]
        verbose_name = "Seleção"
        verbose_name_plural = "Seleções"

    def __str__(self):
        return self.nome


class Figurinha(ModelPadraoAuditavel):
    """Item do catálogo. Editável pelo admin (imagem) → herda `ModelPadraoAuditavel`."""

    code = models.CharField("código", max_length=16, unique=True)
    selecao = models.ForeignKey(
        Selecao,
        on_delete=models.PROTECT,
        related_name="figurinhas",
        verbose_name="seleção",
    )
    name = models.CharField("nome", max_length=255)
    especial = models.BooleanField("especial", default=False)
    imagem = models.ImageField("imagem", upload_to="figurinhas/", null=True, blank=True)

    class Meta:
        ordering = ["code"]
        verbose_name = "Figurinha"
        verbose_name_plural = "Figurinhas"

    def __str__(self):
        return f"{self.code} — {self.name}"

    def thumbnail(self):
        """Miniatura da imagem para o admin; vazio seguro quando não há imagem."""
        if self.imagem:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:4px;" />',
                self.imagem.url,
            )
        return ""

    thumbnail.short_description = "imagem"


class ColecaoFigurinha(ModelPadraoAuditavel):
    """Posse individual (uso sem login de usuário final). Editável pelo admin (quantidade)."""

    figurinha = models.OneToOneField(
        Figurinha,
        on_delete=models.CASCADE,
        related_name="colecao",
        verbose_name="figurinha",
    )
    quantidade = models.PositiveIntegerField("quantidade", default=0)

    class Meta:
        verbose_name = "Coleção"
        verbose_name_plural = "Coleção"

    def __str__(self):
        return f"{self.figurinha.code}: {self.quantidade}"

    @property
    def tenho(self):
        return self.quantidade > 0
