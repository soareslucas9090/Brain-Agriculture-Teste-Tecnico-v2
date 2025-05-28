from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CulturaViewSet, FazendasViewSet, SafraViewSet

router = DefaultRouter()
router.register(r"fazendas", FazendasViewSet, basename="fazendas")
router.register(r"safras", SafraViewSet, basename="safras")
router.register(r"culturas", CulturaViewSet, basename="culturas")

urlpatterns = [
    path("", include(router.urls)),
]
