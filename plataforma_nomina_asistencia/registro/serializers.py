from rest_framework import serializers

from .models import Marcaje


class MarcajeSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source="empleado.get_full_name", read_only=True)
    sucursal_nombre = serializers.CharField(source="sucursal.nombre", read_only=True)
    horas_trabajadas = serializers.SerializerMethodField()

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
            "horas_trabajadas",
            "registrado_por",
            "corregido_por",
            "motivo_correccion",
            "creado_en",
            "actualizado_en",
            "horas_trabajadas",
        ]

    def get_horas_trabajadas(self, obj):
        if not obj.salida:
            return None
        segundos = max((obj.salida - obj.entrada).total_seconds(), 0)
        return round(segundos / 3600, 2)
        read_only_fields = [
            "empleado",
            "sucursal",
            "registrado_por",
            "corregido_por",
            "creado_en",
            "actualizado_en",
        ]
