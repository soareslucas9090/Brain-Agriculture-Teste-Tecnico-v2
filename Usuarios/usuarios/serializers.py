from rest_framework import serializers

from Core.Validations import validar_cpf_cnpj

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
    is_admin = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(read_only=True, required=False)
    is_active = serializers.BooleanField(default=True, required=False)

    def validate_cpf_cnpj(self, value):
        if validar_cpf_cnpj(value, levantar_excessao=False):
            return value
        else:
            raise serializers.ValidationError("O CPF deve conter 11 dígitos.")

    def validate_password(self, value):
        password = value

        if len(password) < 8:
            raise serializers.ValidationError(
                "A senha deve ter pelo menos 8 caracteres."
            )

        return password
