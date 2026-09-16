"""Servicios de cálculo de nómina."""


def calcular_retencion_fuente(base_gravable):
	"""Punto de extensión para el cálculo de retención en la fuente."""
	raise NotImplementedError("El cálculo de retención aún no está implementado.")


def aplicar_novedades(detalle_nomina, novedades):
	"""Punto de extensión para aplicar novedades al detalle de nómina."""
	raise NotImplementedError("La aplicación de novedades aún no está implementada.")
