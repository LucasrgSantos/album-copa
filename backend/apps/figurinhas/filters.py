"""Filtragem da listagem de figurinhas (sem dependência de `django-filter`).

Todos os filtros são combináveis (AND). Parâmetros ausentes ou inválidos são
ignorados. Ver `research.md` D5 e `data-model.md`.
"""

from django.db.models import Q

_VERDADEIRO = {"true", "1", "sim", "yes", "t"}


def _parse_bool(valor: str) -> bool:
    return valor.strip().lower() in _VERDADEIRO


def filtrar_figurinhas(queryset, params):
    """Aplica os filtros `team`/`status`/`busca`/`especial` ao queryset."""
    team = params.get("team")
    if team:
        queryset = queryset.filter(selecao__nome=team)

    status = params.get("status")
    if status == "falta":
        queryset = queryset.filter(colecao__quantidade=0)
    elif status == "tenho":
        queryset = queryset.filter(colecao__quantidade__gt=0)

    especial = params.get("especial")
    if especial not in (None, ""):
        queryset = queryset.filter(especial=_parse_bool(especial))

    busca = params.get("busca")
    if busca:
        queryset = queryset.filter(Q(name__icontains=busca) | Q(code__icontains=busca))

    return queryset
