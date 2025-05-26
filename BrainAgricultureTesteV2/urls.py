from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .views_jwt import TokenObtainPairViewDOC, TokenRefreshViewDOC, TokenVerifyViewDOC

urlpatterns = [
    path("api/token/", TokenObtainPairViewDOC.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshViewDOC.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyViewDOC.as_view(), name="token_verify"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api/usuarios/v1/", include("Usuarios.urls")),
]
