#!/usr/bin/env python
"""Utilidad de administración para el proyecto Django."""

import os
import sys


def main():
	"""Ejecuta las tareas administrativas de Django."""
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
	try:
		from django.core.management import execute_from_command_line
	except ImportError as exc:
		raise ImportError(
			"Django no está instalado o no está disponible en el entorno actual."
		) from exc
	execute_from_command_line(sys.argv)


if __name__ == "__main__":
	main()
