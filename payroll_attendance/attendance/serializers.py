"""Compatibilidad para el módulo público de attendance."""

from rest_framework import serializers

from .models import AttendanceRecord


class AttendanceRecordSerializer(serializers.ModelSerializer):
	employee_name = serializers.CharField(source="employee.get_full_name", read_only=True)
	branch_name = serializers.CharField(source="branch.name", read_only=True)
	worked_hours = serializers.SerializerMethodField()

	class Meta:
		model = AttendanceRecord
		fields = [
			"id", "employee", "employee_name", "branch", "branch_name",
			"date", "clock_in_time", "clock_out_time", "worked_hours", "recorded_by",
			"corrected_by", "correction_reason", "created_at", "updated_at",
		]
		read_only_fields = [
			"employee", "branch", "recorded_by", "corrected_by",
			"created_at", "updated_at", "worked_hours",
		]

	def get_worked_hours(self, obj):
		if not obj.clock_out_time:
			return None
		segundos = max((obj.clock_out_time - obj.clock_in_time).total_seconds(), 0)
		return round(segundos / 3600, 2)
