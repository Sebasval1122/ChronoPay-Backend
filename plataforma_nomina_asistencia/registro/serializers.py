from rest_framework import serializers

from .models import Marcaje


class MarcajeSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source="empleado.get_full_name", read_only=True)
    sucursal_nombre = serializers.CharField(source="sucursal.nombre", read_only=True)

    class Meta:
        model = Marcaje
        fields = [
            "id",
            "empleado",
            "empleado_nombre",
            "sucursal",
            "sucursal_nombre",
            "fecha",
            "entrada",
            "salida",
            "registrado_por",
            "corregido_por",
            "motivo_correccion",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = [
            "empleado",
            "sucursal",
            "registrado_por",
            "corregido_por",
            "creado_en",
            "actualizado_en",
        ]
