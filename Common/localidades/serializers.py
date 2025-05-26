from rest_framework import serializers

from .models import Cidades, Estados


class CidadesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cidades
        fields = (
            "id",
            "nome",
            "codigo_ibge",
            "estado",
        )

    estado = serializers.PrimaryKeyRelatedField(queryset=Estados.objects.all())


class EstadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estados
        fields = (
            "id",
            "nome",
            "sigla",
            "codigo_ibge",
        )
