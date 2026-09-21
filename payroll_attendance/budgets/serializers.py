from rest_framework import serializers

from .models import BranchBudget


class BranchBudgetSerializer(serializers.ModelSerializer):
	class Meta:
		model = BranchBudget
		fields = [
			"id",
			"branch",
			"year",
			"month",
			"budgeted_amount",
			"created_by",
			"created_at",
			"updated_at",
		]
		read_only_fields = ["created_by", "created_at", "updated_at"]

	def validate_month(self, value):
		if not 1 <= value <= 12:
			raise serializers.ValidationError("month must be between 1 and 12.")
		return value