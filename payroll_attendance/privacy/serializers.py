from rest_framework import serializers

from .models import ConsentimientoDatos, PoliticaTratamiento


class PoliticaTratamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoliticaTratamiento
        fields = "__all__"
        read_only_fields = ["publicada_en"]

    def validate(self, attrs):
        if not attrs.get("contenido", "").strip():
            raise serializers.ValidationError("El contenido de la política es obligatorio.")
        return attrs


class ConsentimientoDatosSerializer(serializers.ModelSerializer):
    politica_version = serializers.CharField(source="politica.version", read_only=True)

    class Meta:
        model = ConsentimientoDatos
        fields = [
            "id", "usuario", "politica", "politica_version", "aceptado", "otorgado_en",
        ]
        read_only_fields = ["usuario", "otorgado_en", "politica_version"]

    def validate_politica(self, politica):
        if not politica.vigente:
            raise serializers.ValidationError(
                "Solo puedes aceptar la política de tratamiento vigente."
            )
        return politica