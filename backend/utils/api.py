"""Handler de exceção padrão da API.

Envolve o handler do DRF para garantir que todo erro responda no formato
`{ "detail": "<mensagem legível>", "code": "<slug estável>" }`, conforme
`.specify/specs/desenvolvimento`. Nunca expõe stacktrace.
"""

from rest_framework.views import exception_handler as drf_exception_handler

# Fallback de `code` por status HTTP quando a exceção não traz `default_code`
# (ex.: `Http404` do Django, convertido pelo DRF).
_CODE_POR_STATUS = {
    400: "invalid",
    401: "not_authenticated",
    403: "permission_denied",
    404: "not_found",
    405: "method_not_allowed",
    406: "not_acceptable",
    415: "unsupported_media_type",
    429: "throttled",
    500: "error",
}


def _mensagens(valor):
    """Achata mensagens de erro (str/list/dict) numa string legível."""
    if isinstance(valor, dict):
        partes = []
        for campo, msgs in valor.items():
            texto = _mensagens(msgs)
            partes.append(texto if campo == "detail" else f"{campo}: {texto}")
        return " ".join(partes)
    if isinstance(valor, (list, tuple)):
        return " ".join(_mensagens(item) for item in valor)
    return str(valor)


def _extrair_detail(data):
    if (
        isinstance(data, dict)
        and "detail" in data
        and not isinstance(data["detail"], (dict, list))
    ):
        return str(data["detail"])
    return _mensagens(data) or "Erro."


def exception_handler(exc, context):
    """Resposta de erro padronizada `{ detail, code }`."""
    response = drf_exception_handler(exc, context)
    if response is None:
        # Exceção não tratada pelo DRF (erro 500): deixa o Django lidar.
        return None

    code = getattr(exc, "default_code", None) or _CODE_POR_STATUS.get(
        response.status_code, "error"
    )
    response.data = {"detail": _extrair_detail(response.data), "code": code}
    return response
