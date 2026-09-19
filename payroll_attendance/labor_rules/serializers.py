from rest_framework import serializers
from .models import ReglaLaboral, DiaFestivo


class DiaFestivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaFestivo
        fields = ["id", "regla_laboral", "fecha", "descripcion"]


class ReglaLaboralSerializer(serializers.ModelSerializer):
    dias_festivos = DiaFestivoSerializer(many=True, read_only=True)

    class Meta:
        model = ReglaLaboral
        fields = [
            "id",
            "pais",
            "hora_inicio_diurno",
            "hora_inicio_nocturno",
            "recargo_hora_extra_diurna",
            "recargo_hora_extra_nocturna",
            "recargo_nocturno",
            "recargo_dominical_o_festivo",
            "recargo_nocturno_dominical_o_festivo",
            "recargo_hora_extra_dominical_o_festivo",
            "recargo_hora_extra_nocturna_dominical_o_festivo",
            "horas_maximas_semanales",
            "horas_maximas_diarias_ordinarias",
            "activo",
            "dias_festivos",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = ["creado_en", "actualizado_en"]