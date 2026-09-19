from rest_framework import serializers
from .models import LaborRule, Holiday


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = ["id", "labor_rule", "date", "description"]


class LaborRuleSerializer(serializers.ModelSerializer):
    dias_festivos = HolidaySerializer(many=True, read_only=True)

    class Meta:
        model = LaborRule
        fields = [
            "id",
            "country",
            "daytime_start",
            "nighttime_start",
            "daytime_overtime_rate",
            "nighttime_overtime_rate",
            "nighttime_rate",
            "sunday_holiday_rate",
            "sunday_holiday_night_rate",
            "sunday_holiday_overtime_rate",
            "nighttime_overtime_rate_dominical_o_festivo",
            "max_weekly_hours",
            "max_daily_regular_hours",
            "active",
            "dias_festivos",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]