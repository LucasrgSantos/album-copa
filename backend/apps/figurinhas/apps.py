from django.apps import AppConfig


class FigurinhasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.figurinhas"
    verbose_name = "Figurinhas"

    def ready(self):
        # Conecta o signal de criação de posse e registra a auditoria.
        from . import signals  # noqa: F401
        from . import audit  # noqa: F401
