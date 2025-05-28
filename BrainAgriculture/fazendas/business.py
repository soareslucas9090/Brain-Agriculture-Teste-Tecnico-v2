from datetime import datetime
from decimal import Decimal
from typing import Optional

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

LIMITE_MAXIMO_SUGERIDO_FAZENDA = 100000


class AreaValidationService:
    @staticmethod
    def validate_area_total_fazenda(area_total: Decimal) -> None:
        """
        Valida se a área total da fazenda é válida.

        Args:
            area_total: Área total em hectares

        Raises:
            serializers.ValidationError: Se a área for inválida
        """
        if area_total <= 0:
            raise serializers.ValidationError(
                _("A área total deve ser maior que zero.")
            )

        if area_total > LIMITE_MAXIMO_SUGERIDO_FAZENDA:
            raise serializers.ValidationError(
                _("A área total não pode exceder 100.000 hectares.")
            )

    @staticmethod
    def validate_area_plantada(area_plantada: Decimal) -> None:
        """
        Valida se a área plantada é válida.

        Args:
            area_plantada: Área plantada em hectares

        Raises:
            serializers.ValidationError: Se a área for inválida
        """
        if area_plantada <= 0:
            raise serializers.ValidationError(
                _("A área plantada deve ser maior que zero.")
            )

    @staticmethod
    def validate_area_cultura_disponivel(
        safra, area_plantada: Decimal, cultura_atual_id: Optional[int] = None
    ) -> None:
        """
        Valida se a área plantada da cultura não excede a área disponível.

        Args:
            safra: Instância da safra
            area_plantada: Área que se deseja plantar
            cultura_atual_id: ID da cultura atual (para atualizações)

        Raises:
            serializers.ValidationError: Se a área exceder a disponível
        """

        area_utilizada = Decimal("0")
        if cultura_atual_id:

            area_utilizada = sum(
                cultura.area_plantada
                for cultura in safra.culturas.exclude(id=cultura_atual_id)
            )
        else:
            area_utilizada = safra.area_vegetacao_total

        area_total_utilizada = area_utilizada + area_plantada

        area_agricultavel = safra.fazenda.area_agricultavel(safra.ano)

        if area_total_utilizada > area_agricultavel:
            area_disponivel = area_agricultavel - area_utilizada
            raise serializers.ValidationError(
                {
                    "area_plantada": _(
                        f"A área plantada ({area_plantada} ha) excede a área agricultável disponível "
                        f"({area_disponivel} ha). Área total da fazenda: {safra.fazenda.area_total} ha, área já utilizada: {area_utilizada} ha."
                    )
                }
            )


class SafraValidationService:
    @staticmethod
    def validate_ano_safra(ano: int) -> None:
        """
        Valida se o ano da safra é válido.

        Args:
            ano: Ano da safra

        Raises:
            serializers.ValidationError: Se o ano for inválido
        """
        ano_atual = datetime.now().year

        if ano < 1900 or ano > ano_atual + 1:
            raise serializers.ValidationError(
                _(f"O ano deve estar entre 1900 e {ano_atual + 1}.")
            )

    @staticmethod
    def validate_safra_unica_por_fazenda_ano(
        fazenda, ano: int, safra_atual_id: Optional[int] = None
    ) -> None:
        """
        Valida se já existe uma safra para a fazenda no ano especificado.

        Args:
            fazenda: Instância da fazenda
            ano: Ano da safra
            safra_atual_id: ID da safra atual (para atualizações)

        Raises:
            serializers.ValidationError: Se já existir uma safra
        """
        from .models import Safras

        if safra_atual_id:
            existing = Safras.objects.filter(fazenda=fazenda, ano=ano).exclude(
                id=safra_atual_id
            )
        else:
            existing = Safras.objects.filter(fazenda=fazenda, ano=ano)

        if existing.exists():
            raise serializers.ValidationError(
                _(f"Já existe uma safra para esta fazenda no ano {ano}.")
            )


class FazendaBusinessService:
    @staticmethod
    def calcular_area_info(fazenda, ano: int) -> dict:
        """
        Calcula informações detalhadas sobre as áreas da fazenda.

        Args:
            fazenda: Instância da fazenda
            ano: Ano de referência

        Returns:
            Dict com informações das áreas
        """
        return {
            "area_total": fazenda.area_total,
            "area_agricultavel": fazenda.area_agricultavel(ano),
            "area_vegetacao": fazenda.area_vegetacao(ano),
            "percentual_agricultavel": (
                fazenda.area_agricultavel(ano) / fazenda.area_total * 100
                if fazenda.area_total > 0
                else 0
            ),
            "percentual_vegetacao": (
                fazenda.area_vegetacao(ano) / fazenda.area_total * 100
                if fazenda.area_total > 0
                else 0
            ),
        }


class CulturaBusinessService:
    @staticmethod
    def calcular_area_disponivel_cultura(cultura) -> dict:
        """
        Calcula a área disponível para uma cultura específica.

        Args:
            cultura: Instância da cultura

        Returns:
            Dict com informações da área disponível
        """
        safra = cultura.safra

        area_outras_culturas = sum(
            c.area_plantada for c in safra.culturas.exclude(id=cultura.id)
        )

        area_agricultavel = safra.fazenda.area_agricultavel(safra.ano)

        area_disponivel = area_agricultavel - area_outras_culturas

        return {
            "area_atual": cultura.area_plantada,
            "area_agricultavel_total": area_agricultavel,
            "area_outras_culturas": area_outras_culturas,
            "area_disponivel_para_expansao": area_disponivel,
            "area_maxima_possivel": area_disponivel + cultura.area_plantada,
            "percentual_utilizacao": (
                cultura.area_plantada / area_agricultavel * 100
                if area_agricultavel > 0
                else 0
            ),
        }

    @staticmethod
    def calcular_resumo_safra(safra) -> dict:
        """
        Calcula um resumo das culturas de uma safra.

        Args:
            safra: Instância da safra

        Returns:
            Dict com resumo da safra
        """
        area_agricultavel = safra.fazenda.area_agricultavel(safra.ano)
        area_vegetacao_total = safra.area_vegetacao_total

        return {
            "area_total_fazenda": safra.fazenda.area_total,
            "area_agricultavel": area_agricultavel,
            "area_vegetacao_total": area_vegetacao_total,
            "area_disponivel": area_agricultavel - area_vegetacao_total,
            "total_culturas": safra.culturas.count(),
            "percentual_utilizacao": (
                area_vegetacao_total / area_agricultavel * 100
                if area_agricultavel > 0
                else 0
            ),
            "culturas_detalhes": [
                {
                    "id": cultura.id,
                    "nome": cultura.nome,
                    "area_plantada": cultura.area_plantada,
                    "percentual_da_safra": (
                        cultura.area_plantada / area_vegetacao_total * 100
                        if area_vegetacao_total > 0
                        else 0
                    ),
                }
                for cultura in safra.culturas.all()
            ],
        }
