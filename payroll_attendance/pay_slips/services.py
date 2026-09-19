from io import BytesIO

from django.http import HttpResponse


def generate_pay_slip_pdf(detalle):
	"""Genera un comprobante PDF sencillo sin depender de plantillas HTML."""
	from reportlab.lib.pagesizes import letter
	from reportlab.pdfgen import canvas

	buffer = BytesIO()
	documento = canvas.Canvas(buffer, pagesize=letter)
	documento.setTitle(f"Comprobante {detalle.id}")
	documento.drawString(72, 740, "ChronoPay - Comprobante de nómina")
	documento.drawString(72, 710, f"Empleado: {detalle.user.get_full_name() or detalle.user.username}")
	documento.drawString(72, 690, f"Período: {detalle.payroll.period_start} a {detalle.payroll.period_end}")
	documento.drawString(72, 650, f"Salario base: {detalle.base_salary:,.2f}")
	documento.drawString(72, 630, f"Recargos: {detalle.surcharges:,.2f}")
	documento.drawString(72, 610, f"Novedades: {detalle.work_events:,.2f}")
	documento.drawString(72, 590, f"Retención: {detalle.withholding:,.2f}")
	documento.drawString(72, 550, f"Total neto: {detalle.net_total:,.2f}")
	documento.save()
	response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
	response["Content-Disposition"] = f'attachment; filename="comprobante-{detalle.id}.pdf"'
	return response
