from django.urls import path

from .views import CompanyRegistrationView


urlpatterns = [
    path("registro/", CompanyRegistrationView.as_view(), name="registro-company"),
]
