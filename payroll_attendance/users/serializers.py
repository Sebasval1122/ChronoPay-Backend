from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User, SalaryHistory


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email",
            "national_id", "phone", "rol", "branch", "current_salary",
            "active", "date_joined",
        ]
        read_only_fields = ["date_joined"]


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer usado solo al crear un user (recibe password)."""

    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = [
            "id", "username", "password", "first_name", "last_name", "email",
            "national_id", "phone", "rol", "branch", "current_salary",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Si se crea con un salario inicial, se deja registrado en el historial
        if user.current_salary is not None:
            SalaryHistory.objects.create(
                user=user,
                previous_salary=None,
                new_salary=user.current_salary,
                reason="Salario inicial al crear el user",
            )
        return user


class ChangeSalarySerializer(serializers.Serializer):
    """Serializer para el endpoint de cambio de salario."""

    new_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    reason = serializers.CharField(max_length=255, required=False, allow_blank=True)


class SalaryHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryHistory
        fields = [
            "id", "user", "previous_salary", "new_salary",
            "change_date", "reason", "recorded_by",
        ]
        read_only_fields = fields