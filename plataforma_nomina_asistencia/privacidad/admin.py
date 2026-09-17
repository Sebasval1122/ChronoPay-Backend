from django.contrib import admin

from .models import ConsentimientoDatos, PoliticaTratamiento


@admin.register(PoliticaTratamiento)
class PoliticaTratamientoAdmin(admin.ModelAdmin):
    list_display = ("version", "vigente", "publicada_en")
    list_filter = ("vigente",)
    search_fields = ("version", "contenido")
    readonly_fields = ("publicada_en",)


@admin.register(ConsentimientoDatos)
class ConsentimientoDatosAdmin(admin.ModelAdmin):
    list_display = ("usuario", "politica", "aceptado", "otorgado_en")
    list_filter = ("aceptado", "politica")
    search_fields = ("usuario__username", "usuario__cedula", "politica__version")
    readonly_fields = ("otorgado_en",)
