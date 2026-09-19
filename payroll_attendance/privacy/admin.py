from django.contrib import admin

from .models import DataConsent, DataPolicy


@admin.register(DataPolicy)
class PoliticaTratamientoAdmin(admin.ModelAdmin):
    list_display = ("version", "vigente", "published_at")
    list_filter = ("vigente",)
    search_fields = ("version", "content")
    readonly_fields = ("published_at",)


@admin.register(DataConsent)
class ConsentimientoDatosAdmin(admin.ModelAdmin):
    list_display = ("user", "policy", "aceptado", "granted_at")
    list_filter = ("aceptado", "policy")
    search_fields = ("usuario__username", "usuario__cedula", "politica__version")
    readonly_fields = ("granted_at",)
