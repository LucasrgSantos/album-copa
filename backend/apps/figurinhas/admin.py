from django.contrib import admin
from django.db.models import Count
from unfold.admin import ModelAdmin, StackedInline

from .models import ColecaoFigurinha, Figurinha, Selecao


class AutoriaAdminMixin:
    """Preenche `criado_por`/`alterado_por` (models `ModelPadraoAuditavel`) com o usuário logado."""

    def save_model(self, request, obj, form, change):
        if not change and getattr(obj, "criado_por_id", None) is None:
            obj.criado_por = request.user
        obj.alterado_por = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            if hasattr(obj, "alterado_por_id"):
                if obj.pk is None and getattr(obj, "criado_por_id", None) is None:
                    obj.criado_por = request.user
                obj.alterado_por = request.user
            obj.save()
        formset.save_m2m()
        for obj in formset.deleted_objects:
            obj.delete()


@admin.register(Selecao)
class SelecaoAdmin(ModelAdmin):
    list_display = ("nome", "total_figurinhas")
    search_fields = ("nome",)
    readonly_fields = ("criado_em", "alterado_em")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_total=Count("figurinhas"))

    @admin.display(description="figurinhas", ordering="_total")
    def total_figurinhas(self, obj):
        return obj._total


class ColecaoFigurinhaInline(StackedInline):
    model = ColecaoFigurinha
    extra = 0
    can_delete = False
    fields = ("quantidade", "alterado_em", "alterado_por")
    readonly_fields = ("alterado_em", "alterado_por")


@admin.register(Figurinha)
class FigurinhaAdmin(AutoriaAdminMixin, ModelAdmin):
    list_display = (
        "code",
        "selecao",
        "name",
        "especial",
        "thumbnail",
        "quantidade_atual",
    )
    search_fields = ("code", "name", "selecao__nome")
    list_filter = ("selecao", "especial")
    autocomplete_fields = ("selecao",)
    list_select_related = ("selecao", "colecao")
    readonly_fields = (
        "thumbnail",
        "criado_em",
        "alterado_em",
        "criado_por",
        "alterado_por",
    )
    inlines = [ColecaoFigurinhaInline]

    @admin.display(description="imagem")
    def thumbnail(self, obj):
        return obj.thumbnail()

    @admin.display(description="quantidade")
    def quantidade_atual(self, obj):
        colecao = getattr(obj, "colecao", None)
        return colecao.quantidade if colecao else 0
