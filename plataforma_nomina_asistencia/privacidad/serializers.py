from rest_framework import serializers

from .models import ConsentimientoDatos, PoliticaTratamiento


class PoliticaTratamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliticaTratamiento
        fields = "__all__"


class ConsentimientoDatosSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentimientoDatos
        fields = "__all__"
        read_only_fields = ["otorgado_en"]