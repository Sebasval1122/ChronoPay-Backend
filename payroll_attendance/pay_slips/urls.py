from django.urls import path

from .views import ComprobanteDetalleView


urlpatterns = [
	path("<int:detalle_id>/pdf/", ComprobanteDetalleView.as_view(), name="comprobante-pdf"),
]
