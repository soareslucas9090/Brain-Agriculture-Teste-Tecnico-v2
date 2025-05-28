from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import *

router = SimpleRouter()
router.register(r"estados", EstadosViewSet)
router.register(r"cidades", CidadesViewSet)

urlpatterns = [
    path(
        "atualizar_localidades/",
        AtualizarLocalidadesIBGEView.as_view(),
        name="atualizar-localidades",
    ),
    path("", include(router.urls)),
]
