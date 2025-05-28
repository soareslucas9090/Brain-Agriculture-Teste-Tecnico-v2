from datetime import datetime

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from Usuarios.produtores.models import Produtores

from .business import (
    AreaValidationService,
    CulturaBusinessService,
    FazendaBusinessService,
    SafraValidationService,
)
from .models import Culturas, Fazendas, Safras


class FazendasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fazendas
        fields = [
            "id",
            "nome",
            "produtor",
            "produtor_nome",
            "cidade",
            "cidade_nome",
            "area_total",
            "area_agricultavel",
            "area_vegetacao",
        ]
        read_only_fields = ["id"]

    area_agricultavel = serializers.SerializerMethodField()
    area_vegetacao = serializers.SerializerMethodField()
    produtor_nome = serializers.CharField(
        source="produtor.usuario.nome", read_only=True
    )
    cidade_nome = serializers.CharField(source="cidade.nome", read_only=True)
    produtor = serializers.PrimaryKeyRelatedField(queryset=Produtores.objects.all())

    def get_area_agricultavel(self, obj):
        ano_atual = datetime.now().year

        return obj.area_agricultavel(ano_atual)

    def get_area_vegetacao(self, obj):
        ano_atual = datetime.now().year

        return obj.area_vegetacao(ano_atual)

    def validate_area_total(self, value):
        AreaValidationService.validate_area_total_fazenda(value)

        return value


class SafraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Safras
        fields = [
            "id",
            "nome",
            "fazenda",
            "fazenda_nome",
            "ano",
            "area_vegetacao_total",
            "area_agricultavel_disponivel",
        ]
        read_only_fields = ["id", "nome"]

    fazenda_nome = serializers.CharField(source="fazenda.nome", read_only=True)
    area_vegetacao_total = serializers.ReadOnlyField()
    area_agricultavel_disponivel = serializers.SerializerMethodField()
    fazenda = serializers.PrimaryKeyRelatedField(queryset=Fazendas.objects.all())

    def get_area_agricultavel_disponivel(self, obj):
        return obj.fazenda.area_agricultavel(obj.ano)

    def validate_ano(self, value):
        SafraValidationService.validate_ano_safra(value)

        return value

    def validate(self, attrs):
        fazenda = attrs.get("fazenda")
        ano = attrs.get("ano")

        SafraValidationService.validate_safra_unica_por_fazenda_ano(
            fazenda, ano, self.instance.id if self.instance else None
        )

        return attrs


class CulturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Culturas
        fields = [
            "id",
            "nome",
            "safra",
            "safra_nome",
            "fazenda_nome",
            "ano_safra",
            "area_plantada",
        ]
        read_only_fields = ["id"]

    safra_nome = serializers.CharField(source="safra.nome", read_only=True)
    fazenda_nome = serializers.CharField(source="safra.fazenda.nome", read_only=True)
    ano_safra = serializers.IntegerField(source="safra.ano", read_only=True)
    safra = serializers.PrimaryKeyRelatedField(queryset=Safras.objects.all())

    def validate_area_plantada(self, value):
        AreaValidationService.validate_area_plantada(value)

        return value

    def validate(self, attrs):
        safra = attrs.get("safra", self.instance.safra if self.instance else None)
        area_plantada = attrs.get("area_plantada")
        
        if self.instance and area_plantada is not None:
            safra = self.instance.safra
            
        if safra and area_plantada is not None:
            if isinstance(area_plantada, str):
                area_plantada = Decimal(area_plantada)
            
            AreaValidationService.validate_area_cultura_disponivel(
                safra, area_plantada, self.instance.id if self.instance else None
            )

        return attrs


class CulturaCreateUpdateSerializer(CulturaSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
        
    def to_representation(self, instance):
        return CulturaSerializer(instance, context=self.context).data
