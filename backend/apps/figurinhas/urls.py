"""Rotas da API de figurinhas (montadas sob `/api/v1/` em `config.urls`)."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import FigurinhaViewSet, ProgressoView, TimesView

router = DefaultRouter()
router.register(r"figurinhas", FigurinhaViewSet, basename="figurinha")

urlpatterns = [
    path("colecao/progresso/", ProgressoView.as_view(), name="progresso"),
    path("times/", TimesView.as_view(), name="times"),
    *router.urls,
]
