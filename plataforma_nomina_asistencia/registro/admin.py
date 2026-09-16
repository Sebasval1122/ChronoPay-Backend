from django.contrib import admin

from .models import Marcaje


@admin.register(Marcaje)
class MarcajeAdmin(admin.ModelAdmin):
    list_display = ("empleado", "fecha", "entrada", "salida", "sucursal")
    list_filter = ("fecha", "sucursal")
    search_fields = ("empleado__username", "empleado__cedula")
    readonly_fields = ("creado_en", "actualizado_en")
