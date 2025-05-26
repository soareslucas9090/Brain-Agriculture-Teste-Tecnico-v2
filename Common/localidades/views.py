import requests
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from Core.Permissions import EhAdmin

from .models import Cidade, Estado


@extend_schema(tags=["Common - Localidades"])
class AtualizarLocalidadesIBGEView(APIView):
    permission_classes = [EhAdmin]

    def post(self, request):
        estados_url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
        estados_resp = requests.get(estados_url)
        if estados_resp.status_code != 200:
            return Response(
                {"erro": "Erro ao buscar estados do IBGE"},
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
