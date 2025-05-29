from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from Core.BasicMyDataAndModelViewSet import BasicMyDataAndModelViewSet
from Usuarios.produtores.models import Produtores

from .business import CulturaBusinessService, FazendaBusinessService
from .models import Culturas, Fazendas, Safras
from .serializers import (
    CulturaCreateUpdateSerializer,
    CulturaSerializer,
    FazendasSerializer,
    SafraSerializer,
)


@extend_schema(tags=["BrainAgriculture - Fazendas"])
class FazendasViewSet(BasicMyDataAndModelViewSet):
    queryset = Fazendas.objects.all()
    serializer_class = FazendasSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["nome", "produtor", "cidade"]
    http_method_names = ["get", "post", "patch", "delete"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="nome",
                description="Filtrar por nome da fazenda",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="produtor",
                description="Filtrar por ID do produtor",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="cidade",
                description="Filtrar por ID da cidade",
                required=False,
                type=int,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            produtor = Produtores.objects.get(
                id=serializer.validated_data["produtor"].id
            )
        except:
            return Response(
                {"detail": "Produtor não encontrado."}, status=status.HTTP_404_NOT_FOUND
            )

        if produtor.usuario != request.user:
            return Response(
                {
                    "detail": "Você não tem permissão para acessar recursos de outros usuários.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().create(request, *args, **kwargs)

    def get_dono_do_registro(self, obj):
        try:
            return self.request.user.id == obj.produtor.usuario.id
        except:
            return False

    def get_queryset(self):
        user = self.request.user

        if user.is_admin:
            return Fazendas.objects.all()

        if hasattr(user, "produtor_perfil"):
            return Fazendas.objects.filter(produtor=user.produtor_perfil)

        return Fazendas.objects.none()

    @action(detail=True, methods=["get"])
    def area_info(self, request, pk=None):
        fazenda = self.get_object()
        ano = request.query_params.get("ano")

        if not ano:
            ano = datetime.now().year
        else:
            try:
                ano = int(ano)
            except ValueError:
                return Response(
                    {"detail": "Ano deve ser um número inteiro"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        area_info = FazendaBusinessService.calcular_area_info(fazenda, ano)

        data = {"fazenda": fazenda.nome, "ano": ano, **area_info, "safras": []}

        safras = fazenda.safras.filter(ano=ano)
        for safra in safras:
            data["safras"].append(
                {
                    "id": safra.id,
                    "nome": safra.nome,
                    "area_vegetacao_total": safra.area_vegetacao_total,
                    "culturas": [
                        {
                            "id": cultura.id,
                            "nome": cultura.nome,
                            "area_plantada": cultura.area_plantada,
                        }
                        for cultura in safra.culturas.all()
                    ],
                }
            )

        return Response(data)


@extend_schema(tags=["BrainAgriculture - Safras"])
class SafraViewSet(BasicMyDataAndModelViewSet):
    queryset = Safras.objects.all()
    serializer_class = SafraSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["fazenda", "ano"]
    http_method_names = ["get", "post", "patch", "delete"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="fazenda",
                description="Filtrar por ID da fazenda",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="ano",
                description="Filtrar por ano da safra",
                required=False,
                type=int,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            fazenda = Fazendas.objects.get(id=serializer.validated_data["fazenda"].id)
        except:
            return Response(
                {"detail": "Fazenda não encontrada."}, status=status.HTTP_404_NOT_FOUND
            )

        if fazenda.produtor.usuario != request.user:
            return Response(
                {
                    "detail": "Você não tem permissão para acessar recursos de outros usuários.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().create(request, *args, **kwargs)

    def get_dono_do_registro(self, obj):
        try:
            return self.request.user.id == obj.fazenda.produtor.usuario.id
        except:
            return False

    def get_queryset(self):
        user = self.request.user

        if user.is_admin:
            return Safras.objects.all()

        if hasattr(user, "produtor_perfil"):
            return Safras.objects.filter(fazenda__produtor=user.produtor_perfil)

        return Safras.objects.none()

    @action(detail=True, methods=["get"])
    def culturas_resumo(self, request, pk=None):
        safra = self.get_object()

        resumo = CulturaBusinessService.calcular_resumo_safra(safra)

        data = {
            "safra": safra.nome,
            "fazenda": safra.fazenda.nome,
            "ano": safra.ano,
            **resumo,
        }

        return Response(data)


@extend_schema(tags=["BrainAgriculture - Culturas"])
class CulturaViewSet(BasicMyDataAndModelViewSet):
    queryset = Culturas.objects.all()
    serializer_class = CulturaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["nome", "safra", "safra__fazenda", "safra__ano"]
    http_method_names = ["get", "post", "patch", "delete"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="nome",
                description="Filtrar por nome da cultura",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="safra",
                description="Filtrar por ID da safra",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="safra__fazenda",
                description="Filtrar por ID da fazenda",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="safra__ano",
                description="Filtrar por ano da safra",
                required=False,
                type=int,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            safra = Safras.objects.get(id=serializer.validated_data["safra"].id)
        except:
            return Response(
                {"detail": "Safra não encontrada."}, status=status.HTTP_404_NOT_FOUND
            )

        if safra.fazenda.produtor.usuario != request.user:
            return Response(
                {
                    "detail": "Você não tem permissão para acessar recursos de outros usuários.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().create(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return CulturaCreateUpdateSerializer
        return CulturaSerializer

    def get_dono_do_registro(self, obj):
        try:
            return self.request.user.id == obj.safra.fazenda.produtor.usuario.id
        except:
            return False

    def get_queryset(self):
        user = self.request.user

        if user.is_admin:
            return Culturas.objects.all()

        if hasattr(user, "produtor_perfil"):
            return Culturas.objects.filter(
                safra__fazenda__produtor=user.produtor_perfil
            )

        return Culturas.objects.none()

    @action(detail=True, methods=["get"])
    def area_disponivel(self, request, pk=None):
        cultura = self.get_object()

        area_info = CulturaBusinessService.calcular_area_disponivel_cultura(cultura)

        data = {
            "cultura": cultura.nome,
            "safra": cultura.safra.nome,
            "fazenda": cultura.safra.fazenda.nome,
            **area_info,
        }

        return Response(data)
