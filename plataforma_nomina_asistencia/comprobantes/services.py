from io import BytesIO

from django.http import HttpResponse


def generar_comprobante_pdf(detalle):
	"""Genera un comprobante PDF sencillo sin depender de plantillas HTML."""
	from reportlab.lib.pagesizes import letter
	from reportlab.pdfgen import canvas

	buffer = BytesIO()
	documento = canvas.Canvas(buffer, pagesize=letter)
	documento.setTitle(f"Comprobante {detalle.id}")
	documento.drawString(72, 740, "ChronoPay - Comprobante de nómina")
	documento.drawString(72, 710, f"Empleado: {detalle.usuario.get_full_name() or detalle.usuario.username}")
	documento.drawString(72, 690, f"Período: {detalle.nomina.periodo_inicio} a {detalle.nomina.periodo_fin}")
	documento.drawString(72, 650, f"Salario base: {detalle.salario_base:,.2f}")
	documento.drawString(72, 630, f"Recargos: {detalle.recargos:,.2f}")
	documento.drawString(72, 610, f"Novedades: {detalle.novedades:,.2f}")
	documento.drawString(72, 590, f"Retención: {detalle.retencion_fuente:,.2f}")
	documento.drawString(72, 550, f"Total neto: {detalle.total_neto:,.2f}")
	documento.save()
	response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
	response["Content-Disposition"] = f'attachment; filename="comprobante-{detalle.id}.pdf"'
	return response
