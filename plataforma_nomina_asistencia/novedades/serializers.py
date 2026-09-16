from rest_framework import serializers

from .models import Incapacidad, Licencia, Permiso


class IncapacidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incapacidad
        fields = "__all__"
        read_only_fields = ["creada_en"]


class LicenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Licencia
        fields = "__all__"
        read_only_fields = ["creada_en"]


class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = "__all__"
        read_only_fields = ["creada_en"]