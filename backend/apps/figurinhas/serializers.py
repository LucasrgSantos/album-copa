"""Serializers da API de figurinhas."""

from rest_framework import serializers

from .models import Figurinha


class FigurinhaSerializer(serializers.ModelSerializer):
    """Representação de leitura de uma figurinha, com posse e time.

    `team` é mapeado de `selecao.nome`; `quantidade`/`possuo` vêm da posse 1:1
    (`colecao`). O queryset da view usa `select_related("selecao", "colecao")`
    para evitar N+1 ao ler esses campos.
    """

    team = serializers.CharField(source="selecao.nome", read_only=True)
    imagem = serializers.ImageField(read_only=True)
    quantidade = serializers.SerializerMethodField()
    possuo = serializers.SerializerMethodField()

    class Meta:
        model = Figurinha
        fields = ["code", "name", "team", "especial", "imagem", "quantidade", "possuo"]

    def get_quantidade(self, obj) -> int:
        colecao = getattr(obj, "colecao", None)
        return colecao.quantidade if colecao is not None else 0

    def get_possuo(self, obj) -> bool:
        colecao = getattr(obj, "colecao", None)
        return bool(colecao is not None and colecao.quantidade > 0)


class AtualizarQuantidadeSerializer(serializers.Serializer):
    """Corpo do PATCH de quantidade: inteiro >= 0 (RF-009/RF-017)."""

    quantidade = serializers.IntegerField(min_value=0)


class TimeSerializer(serializers.Serializer):
    """Uma seleção como opção de filtro."""

    team = serializers.CharField(source="nome", read_only=True)


class PorTeamSerializer(serializers.Serializer):
    team = serializers.CharField()
    total = serializers.IntegerField()
    possuidas = serializers.IntegerField()
    percentual = serializers.FloatField()


class ProgressoSerializer(serializers.Serializer):
    """Progresso consolidado do álbum."""

    total = serializers.IntegerField()
    total_possuidas = serializers.IntegerField()
    total_faltantes = serializers.IntegerField()
    percentual = serializers.FloatField()
    por_team = PorTeamSerializer(many=True)
