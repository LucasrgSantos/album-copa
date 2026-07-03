from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ColecaoFigurinha, Figurinha


@receiver(post_save, sender=Figurinha)
def garantir_colecao(sender, instance, created, **kwargs):
    """Toda figurinha nova nasce com uma `ColecaoFigurinha` (quantidade=0).

    `get_or_create` mantém a idempotência: reimportações não recriam a posse.
    """
    if created:
        ColecaoFigurinha.objects.get_or_create(
            figurinha=instance, defaults={"quantidade": 0}
        )
