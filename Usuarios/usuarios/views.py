from typing import override

from django.contrib.auth.models import AnonymousUser
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema

from Core.BasicModelViewSet import BasicModelViewSet
from Core.Permissions import EhAdmin, EhMeuDadoOuSouAdmin

from .models import Usuarios
from .serializers import Usuarios2AdminSerializer, UsuariosSerializer


@extend_schema(tags=["Usuarios - Usuarios"])
class UsuariosViewSet(BasicModelViewSet):
    queryset = Usuarios.objects.all()
    serializer_class = Usuarios2AdminSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["nome", "cpf_cnpj", "is_active", "is_admin"]
    http_method_names = ["get", "post", "patch", "delete"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="nome",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtrar por nome do usuário",
            ),
            OpenApiParameter(
                name="cpf_cnpj",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtrar por CPF ou CNPJ",
            ),
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filtrar por usuários ativos/inativos",
            ),
            OpenApiParameter(
                name="is_admin",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filtrar por administradores",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if (
            isinstance(self.request.user, AnonymousUser)
            or not self.request.user.is_admin
        ):
            return UsuariosSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.kwargs.get("pk", None) and self.request.method == "GET":
            return [EhMeuDadoOuSouAdmin()]
        return [EhAdmin()]

    def get_dono_do_registro(self, obj):
        return self.request.user.id == int(self.kwargs.get("pk", None))
