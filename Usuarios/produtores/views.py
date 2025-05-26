from typing import override

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema

from Core.BasicModelViewSet import BasicModelViewSet
from Core.Permissions import EhAdmin, EhMeuDadoOuSouAdmin

from .models import Produtores
from .serializers import ProdutoresSerializer


@extend_schema(tags=["Usuarios - Produtores"])
class ProdutoresViewSet(BasicModelViewSet):
    queryset = Produtores.objects.all()
    serializer_class = ProdutoresSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["usuario__nome", "usuario__cpf_cnpj", "usuario__is_active"]
    http_method_names = ["get", "post", "patch", "delete"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="usuario__nome",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtrar por nome do usuário",
            ),
            OpenApiParameter(
                name="usuario__cpf_cnpj",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtrar por CPF ou CNPJ do usuário",
            ),
            OpenApiParameter(
                name="usuario__is_active",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filtrar por usuários ativos/inativos",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()

        if not EhAdmin().has_permission(self.request, self):
            qs = qs.filter(usuario=self.request.user)

        return qs

    def get_permissions(self):
        if self.request.method == "GET":
            return [EhMeuDadoOuSouAdmin()]
        return [EhAdmin()]

    def get_dono_do_registro(self):
        try:
            produtor = Produtores.objects.get(pk=self.kwargs.get("pk"))
            return self.request.user.id == produtor.usuario.id
        except:
            return False
