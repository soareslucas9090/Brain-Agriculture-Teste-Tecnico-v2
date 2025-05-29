from rest_framework import serializers


class DashboardTotaisSerializer(serializers.Serializer):
    total_fazendas = serializers.IntegerField(help_text="Total de fazendas cadastradas")
    total_hectares = serializers.DecimalField(
        max_digits=12, decimal_places=2, help_text="Total de hectares registrados"
    )


class DashboardPorEstadoSerializer(serializers.Serializer):
    estado = serializers.CharField(help_text="Nome do estado")
    sigla = serializers.CharField(help_text="Sigla do estado")
    quantidade = serializers.IntegerField(help_text="Quantidade de fazendas")
    percentual = serializers.DecimalField(
        max_digits=5, decimal_places=2, help_text="Percentual em relação ao total"
    )


class DashboardPorCulturaSerializer(serializers.Serializer):
    cultura = serializers.CharField(help_text="Nome da cultura")
    area_total = serializers.DecimalField(
        max_digits=12, decimal_places=2, help_text="Área total plantada em hectares"
    )
    percentual = serializers.DecimalField(
        max_digits=5, decimal_places=2, help_text="Percentual em relação ao total"
    )


class DashboardUsoSoloSerializer(serializers.Serializer):
    tipo = serializers.CharField(
        help_text="Tipo de uso (Área Agricultável ou Vegetação)"
    )
    area_total = serializers.DecimalField(
        max_digits=12, decimal_places=2, help_text="Área total em hectares"
    )
    percentual = serializers.DecimalField(
        max_digits=5, decimal_places=2, help_text="Percentual em relação ao total"
    )


class DashboardCompletoSerializer(serializers.Serializer):
    totais = DashboardTotaisSerializer()
    por_estado = DashboardPorEstadoSerializer(many=True)
    por_cultura = DashboardPorCulturaSerializer(many=True)
    uso_solo = DashboardUsoSoloSerializer(many=True)
