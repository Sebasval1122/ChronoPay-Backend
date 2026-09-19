from django.urls import path

from .views import RegistroEmpresaView


urlpatterns = [
    path("registro/", RegistroEmpresaView.as_view(), name="registro-empresa"),
]
