from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Usuario, HistorialSalarial


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            "id", "username", "first_name", "last_name", "email",
            "cedula", "telefono", "rol", "sucursal", "salario_actual",
            "activo", "date_joined",
        ]
        read_only_fields = ["date_joined"]


class CrearUsuarioSerializer(serializers.ModelSerializer):
    """Serializer usado solo al crear un usuario (recibe password)."""

    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = Usuario
        fields = [
            "id", "username", "password", "first_name", "last_name", "email",
            "cedula", "telefono", "rol", "sucursal", "salario_actual",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()

        # Si se crea con un salario inicial, se deja registrado en el historial
        if usuario.salario_actual is not None:
            HistorialSalarial.objects.create(
                usuario=usuario,
                salario_anterior=None,
                salario_nuevo=usuario.salario_actual,
                motivo="Salario inicial al crear el usuario",
            )
        return usuario


class CambiarSalarioSerializer(serializers.Serializer):
    """Serializer para el endpoint de cambio de salario."""

    salario_nuevo = serializers.DecimalField(max_digits=12, decimal_places=2)
    motivo = serializers.CharField(max_length=255, required=False, allow_blank=True)


class HistorialSalarialSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialSalarial
        fields = [
            "id", "usuario", "salario_anterior", "salario_nuevo",
            "fecha_cambio", "motivo", "registrado_por",
        ]
        read_only_fields = fields