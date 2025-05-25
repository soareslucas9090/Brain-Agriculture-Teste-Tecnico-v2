from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import *

router = SimpleRouter()
router.register("usuarios", UsuariosViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
