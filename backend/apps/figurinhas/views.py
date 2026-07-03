"""Views da API REST de figurinhas (`/api/v1/`).

Sem autenticação (uso individual, RF-015). Pontos de atenção contra N+1:
- listagem/detalhe usam `select_related("selecao", "colecao")`;
- o progresso é calculado por agregação (sem laço por seleção).
"""

import structlog
from django.db.models import Count, Q
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .filters import filtrar_figurinhas
from .models import ColecaoFigurinha, Figurinha, Selecao
from .serializers import (
    AtualizarQuantidadeSerializer,
    FigurinhaSerializer,
    ProgressoSerializer,
    TimeSerializer,
)

logger = structlog.get_logger(__name__)


class FigurinhaViewSet(ReadOnlyModelViewSet):
    """Catálogo (listagem paginada + detalhe) e ações de quantidade."""

    queryset = Figurinha.objects.select_related("selecao", "colecao").order_by("code")
    serializer_class = FigurinhaSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    lookup_field = "code"
    lookup_value_regex = "[^/]+"  # aceita códigos com sufixo/dígitos (ex.: GER2s, 00)

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtros valem só para a listagem; detalhe e ações de escrita resolvem
        # a figurinha apenas por `code` (senão query-params de filtro dariam 404).
        if self.action == "list":
            queryset = filtrar_figurinhas(queryset, self.request.query_params)
        return queryset

    def _resposta_atualizada(self, figurinha):
        return Response(self.get_serializer(figurinha).data)

    @action(detail=True, methods=["patch"], url_path="quantidade")
    def quantidade(self, request, code=None):
        """Define a quantidade de posse (valor absoluto, >= 0)."""
        figurinha = self.get_object()
        entrada = AtualizarQuantidadeSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        colecao = figurinha.colecao
        colecao.quantidade = entrada.validated_data["quantidade"]
        colecao.save()
        logger.info(
            "quantidade_definida", code=figurinha.code, quantidade=colecao.quantidade
        )
        return self._resposta_atualizada(figurinha)

    @action(detail=True, methods=["post"], url_path="incrementar")
    def incrementar(self, request, code=None):
        """quantidade += 1."""
        figurinha = self.get_object()
        colecao = figurinha.colecao
        colecao.quantidade += 1
        colecao.save()
        logger.info(
            "quantidade_incrementada",
            code=figurinha.code,
            quantidade=colecao.quantidade,
        )
        return self._resposta_atualizada(figurinha)

    @action(detail=True, methods=["post"], url_path="decrementar")
    def decrementar(self, request, code=None):
        """quantidade -= 1, nunca abaixo de 0 (idempotente em 0)."""
        figurinha = self.get_object()
        colecao = figurinha.colecao
        colecao.quantidade = max(0, colecao.quantidade - 1)
        colecao.save()
        logger.info(
            "quantidade_decrementada",
            code=figurinha.code,
            quantidade=colecao.quantidade,
        )
        return self._resposta_atualizada(figurinha)


class TimesView(ListAPIView):
    """Lista de seleções distintas para popular filtros do frontend."""

    queryset = Selecao.objects.order_by("nome")
    serializer_class = TimeSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    pagination_class = None


class ProgressoView(APIView):
    """Progresso consolidado do álbum (por agregação, sem N+1)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    @staticmethod
    def _percentual(possuidas, total):
        return round(possuidas / total * 100, 1) if total else 0.0

    def get(self, request):
        total = Figurinha.objects.count()
        total_possuidas = ColecaoFigurinha.objects.filter(quantidade__gt=0).count()
        total_faltantes = total - total_possuidas

        selecoes = Selecao.objects.annotate(
            total=Count("figurinhas"),
            possuidas=Count(
                "figurinhas",
                filter=Q(figurinhas__colecao__quantidade__gt=0),
            ),
        ).order_by("nome")

        por_team = [
            {
                "team": selecao.nome,
                "total": selecao.total,
                "possuidas": selecao.possuidas,
                "percentual": self._percentual(selecao.possuidas, selecao.total),
            }
            for selecao in selecoes
        ]

        dados = {
            "total": total,
            "total_possuidas": total_possuidas,
            "total_faltantes": total_faltantes,
            "percentual": self._percentual(total_possuidas, total),
            "por_team": por_team,
        }
        return Response(ProgressoSerializer(dados).data)
