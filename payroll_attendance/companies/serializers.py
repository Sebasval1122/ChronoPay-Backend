from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


Usuario = get_user_model()


class RegistroEmpresaSerializer(serializers.Serializer):
    nombre_empresa = serializers.CharField(max_length=150)
    nombre_admin = serializers.CharField(max_length=150)
    apellido_admin = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, validators=[validate_password])

    def to_internal_value(self, data):
        campos_permitidos = set(self.fields)
        campos_recibidos = set(data)
        campos_extra = campos_recibidos - campos_permitidos
        if campos_extra:
            raise serializers.ValidationError(
                {"detail": "La solicitud contiene campos no permitidos."}
            )
        return super().to_internal_value(data)

    def validate(self, attrs):
        email = attrs["email"].strip()
        username = attrs["username"].strip()
        if Usuario.objects.filter(username__iexact=username).exists() or Usuario.objects.filter(
            email__iexact=email
        ).exists():
            raise serializers.ValidationError(
                "No fue posible completar el registro con los datos proporcionados."
            )
        attrs["email"] = email
        attrs["username"] = username
        return attrs
