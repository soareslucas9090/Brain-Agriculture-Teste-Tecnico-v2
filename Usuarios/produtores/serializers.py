from rest_framework import serializers

from .models import Produtores, Usuarios


class ProdutoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produtores
        fields = ("id", "usuario")

    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuarios.objects.all())

    def validate_usuario(self, value):
        if Produtores.objects.filter(usuario=value).exists():
            raise serializers.ValidationError(
                "Perfil de produtor já criado para este usuário."
            )

        return value
