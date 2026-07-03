"""Registro de auditoria (django-auditlog).

Auditamos `ColecaoFigurinha` para rastrear toda alteração de `quantidade`
(valor anterior e novo), conforme RF-010.
"""

from auditlog.registry import auditlog

from .models import ColecaoFigurinha

auditlog.register(ColecaoFigurinha)
