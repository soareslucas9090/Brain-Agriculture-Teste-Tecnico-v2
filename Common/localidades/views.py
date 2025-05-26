import os

import requests
from django_filters.rest_framework import DjangoFilterBackend
from dotenv import load_dotenv
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from Core.Permissions import EhAdmin

from .models import Cidades, Estados
from .serializers import CidadesSerializer, EstadosSerializer


@extend_schema(tags=["Common - Localidades"])
class AtualizarLocalidadesIBGEView(APIView):
    permission_classes = [EhAdmin]

    def post(self, request):
        load_dotenv()

        estados_url = os.environ.get("IBGE_ESTADOS_API_URL")
        municipios_url = os.environ.get("IBGE_MUCICIPIOS_API_URL")

        estados_count = requests.get(f"{estados_url}/?view=nivelado")
        municipios_count = requests.get(f"{municipios_url}/?view=nivelado")

        if estados_count.status_code != 200 or municipios_count.status_code != 200:
            return Response(
                {"erro": "Erro ao buscar dados do IBGE."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        if (
            len(estados_count.json()) != Estados.objects.count()
            or len(municipios_count.json()) != Cidades.objects.count()
        ):

            estados_resp = requests.get(estados_url)

            if estados_resp.status_code != 200:
                return Response(
                    {"erro": "Erro ao buscar estados do IBGE."},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            estados_data = estados_resp.json()
            estados_criados, estados_atualizados = 0, 0
            cidades_criadas, cidades_atualizadas = 0, 0

            for estado in estados_data:
                estado_obj, created = Estado.objects.update_or_create(
                    codigo_ibge=estado["id"],
                    defaults={
                        "nome": estado["nome"],
                        "sigla": estado["sigla"],
                    },
                )
                if created:
                    estados_criados += 1
                else:
                    estados_atualizados += 1

                cidades_url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{estado['id']}/municipios"
                cidades_resp = requests.get(cidades_url)
                if cidades_resp.status_code != 200:
                    continue
                cidades_data = cidades_resp.json()
                for cidade in cidades_data:
                    cidade_obj, created = Cidade.objects.update_or_create(
                        codigo_ibge=cidade["id"],
                        defaults={
                            "nome": cidade["nome"],
                            "estado": estado_obj,
                        },
                    )
                    if created:
                        cidades_criadas += 1
                    else:
                        cidades_atualizadas += 1

            return Response(
                {
                    "estados_criados": estados_criados,
                    "estados_atualizados": estados_atualizados,
                    "cidades_criadas": cidades_criadas,
                    "cidades_atualizadas": cidades_atualizadas,
                },
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                {
                    "detail": "Cidades e Estados já atualizados.",
                },
                status=status.HTTP_200_OK,
            )


@extend_schema(tags=["Common - Localidades"])
class CidadesViewSet(ReadOnlyModelViewSet):
    queryset = Cidades.objects.all()
    serializer_class = CidadesSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["nome", "estado__nome", "estado__sigla", "codigo_ibge"]
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="nome",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtrar por nome da cidade.",
            ),
            OpenApiParameter(
                name="estado__nome",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtrar pelo nome do estado.",
            ),
            OpenApiParameter(
                name="estado__sigla",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtrar pela sigla do estado.",
            ),
            OpenApiParameter(
                name="codigo_ibge",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filtrar pelo código do IBGE.",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema(tags=["Common - Localidades"])
class EstadosViewSet(ReadOnlyModelViewSet):
    queryset = Estados.objects.all()
    serializer_class = EstadosSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["nome", "sigla", "codigo_ibge"]
    http_method_names = ["get"]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="nome",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtrar por nome da cidade.",
            ),
            OpenApiParameter(
                name="sigla",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtrar pela sigla do estado.",
            ),
            OpenApiParameter(
                name="codigo_ibge",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filtrar pelo código do IBGE.",
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
