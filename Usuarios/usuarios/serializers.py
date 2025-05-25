from rest_framework import serializers

from .models import Usuarios


class UsuariosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = ("id", "nome", "cpf_cnpj", "is_active")

    nome = serializers.CharField(read_only=True)
    cpf_cnpj = serializers.CharField(read_only=True)
    is_active = serializers.CharField(read_only=True)


class Usuarios2AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        fields = "__all__"

    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        password = value

        if len(password) < 8:
            raise serializers.ValidationError(
                "A senha deve ter pelo menos 8 caracteres."
            )

        return password
