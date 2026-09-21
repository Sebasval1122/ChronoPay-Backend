from django.conf import settings
from django.db import models


class BranchBudget(models.Model):
	branch = models.ForeignKey(
		"branches.Branch",
		on_delete=models.CASCADE,
		related_name="budgets",
	)
	year = models.PositiveIntegerField()
	month = models.PositiveIntegerField()
	budgeted_amount = models.DecimalField(max_digits=14, decimal_places=2)
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ("branch", "year", "month")
