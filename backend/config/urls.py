from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.figurinhas.urls")),
]

if settings.DEBUG:
    # Serve os arquivos de mídia (imagens/placeholders) em desenvolvimento.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
