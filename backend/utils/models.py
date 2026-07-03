"""
Models base do projeto.

Toda tabela do projeto DEVE herdar de uma destas duas classes abstratas, conforme o contexto:

- `ModelPadrao`: para dados que **não** são editados por um usuário (ex.: dados de referência
  populados por importação/seed). Fornece apenas os carimbos de tempo `criado_em`/`alterado_em`.
- `ModelPadraoAuditavel`: para dados que **podem** ser editados por um usuário. Além dos carimbos
  de tempo, rastreia `criado_por`/`alterado_por` (quem criou e quem alterou por último).

Regra registrada em `.specify/specs/desenvolvimento` e no `CLAUDE.md`.
"""

from django.conf import settings
from django.db import models


class ModelPadrao(models.Model):
    """Base abstrata com carimbos de tempo. Herde daqui quando o registro não é editado por usuário."""

    # Preenchido uma única vez, na criação.
    criado_em = models.DateTimeField("criado em", auto_now_add=True)
    # Atualizado automaticamente a cada save().
    alterado_em = models.DateTimeField("alterado em", auto_now=True)

    class Meta:
        abstract = True


class ModelPadraoAuditavel(ModelPadrao):
    """Base abstrata auditável. Herde daqui quando o registro pode ser editado por um usuário.

    `criado_por`/`alterado_por` são preenchidos pela camada que conhece o usuário atual
    (ex.: `save_model` do Django Admin ou middleware de usuário corrente); por isso são
    `editable=False` e opcionais (criações automáticas — signals/importação — ficam sem autor).
    """

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="+",
        verbose_name="criado por",
    )
    alterado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="+",
        verbose_name="alterado por",
    )

    class Meta:
        abstract = True
