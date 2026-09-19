from rest_framework import serializers

from .models import DataConsent, DataPolicy


class PoliticaTratamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataPolicy
        fields = "__all__"
        read_only_fields = ["published_at"]

    def validate(self, attrs):
        if not attrs.get("content", "").strip():
            raise serializers.ValidationError("El content de la política es obligatorio.")
        return attrs


class ConsentimientoDatosSerializer(serializers.ModelSerializer):
    policy_version = serializers.CharField(source="policy.version", read_only=True)

    class Meta:
        model = DataConsent
        fields = [
            "id", "user", "policy", "policy_version", "aceptado", "granted_at",
        ]
        read_only_fields = ["user", "granted_at", "policy_version"]

    def validate_politica(self, policy):
        if not policy.vigente:
            raise serializers.ValidationError(
                "Solo puedes aceptar la política de tratamiento vigente."
            )
        return policy