"""Modelos públicos del módulo de asistencia.

El modelo se mantiene en ``registro`` para conservar las migraciones existentes.
Este módulo lo reexporta para que la API pueda organizarse bajo ``asistencia``.
"""

from registro.models import Marcaje

__all__ = ["Marcaje"]
