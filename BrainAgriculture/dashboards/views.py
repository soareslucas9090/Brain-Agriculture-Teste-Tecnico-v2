from datetime import datetime
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .business import DashboardBusiness
from .serializers import (
    DashboardCompletoSerializer,
    DashboardTotaisSerializer,
    DashboardPorEstadoSerializer,
    DashboardPorCulturaSerializer,
    DashboardUsoSoloSerializer
)


@extend_schema(tags=["BrainAgriculture - Dashboards"])
class DashboardViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Dashboard completo",
        description="Retorna todos os dados do dashboard incluindo totais e gráficos",
        responses={200: DashboardCompletoSerializer},
        parameters=[
            OpenApiParameter(
                name='ano',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Ano de referência para cálculo de uso do solo',
                required=False,
                default=datetime.now().year
            )
        ]
    )
    def list(self, request):
        ano_referencia = request.query_params.get('ano', datetime.now().year)
        
        try:
            ano_referencia = int(ano_referencia)
        except ValueError:
            ano_referencia = datetime.now().year

        data = DashboardBusiness.get_dashboard_completo(ano_referencia)

        serializer = DashboardCompletoSerializer(data)
        return Response(serializer.data)

    @extend_schema(
        summary="Totais do dashboard",
        description="Retorna o total de fazendas e hectares cadastrados",
        responses={200: DashboardTotaisSerializer}
    )
    @action(detail=False, methods=['get'])
    def totais(self, request):
        data = DashboardBusiness.get_totais()
        serializer = DashboardTotaisSerializer(data)
        return Response(serializer.data)

    @extend_schema(
        summary="Fazendas por estado",
        description="Retorna a distribuição de fazendas por estado",
        responses={200: DashboardPorEstadoSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def por_estado(self, request):
        data = DashboardBusiness.get_distribuicao_por_estado()
        serializer = DashboardPorEstadoSerializer(data, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Área por cultura",
        description="Retorna a distribuição de área por cultura plantada",
        responses={200: DashboardPorCulturaSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def por_cultura(self, request):
        data = DashboardBusiness.get_distribuicao_por_cultura()
        serializer = DashboardPorCulturaSerializer(data, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Uso do solo",
        description="Retorna a distribuição entre área agricultável e vegetação",
        responses={200: DashboardUsoSoloSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                name='ano',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Ano de referência para cálculo',
                required=False,
                default=datetime.now().year
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def uso_solo(self, request):
        ano_referencia = request.query_params.get('ano', datetime.now().year)
        
        try:
            ano_referencia = int(ano_referencia)
        except ValueError:
            ano_referencia = datetime.now().year

        data = DashboardBusiness.get_uso_solo(ano_referencia)
        serializer = DashboardUsoSoloSerializer(data, many=True)
        return Response(serializer.data)