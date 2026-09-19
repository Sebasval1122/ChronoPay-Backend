from rest_framework import serializers

from .models import Sucursal


class SucursalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sucursal
        fields = [
            "id",
            "nombre",
            "codigo",
            "direccion",
            "ciudad",
            "telefono",
            "activo",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = ["creado_en", "actualizado_en"]
