from django.contrib import admin

from .models import AttendanceRecord


@admin.register(AttendanceRecord)
class MarcajeAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "clock_in_time", "clock_out_time", "branch")
    list_filter = ("date", "branch")
    search_fields = ("empleado__username", "empleado__cedula")
    readonly_fields = ("created_at", "updated_at")