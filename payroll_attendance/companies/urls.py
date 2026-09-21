from django.urls import path

from .views import CompanyRegistrationView


urlpatterns = [
    path("register/", CompanyRegistrationView.as_view(), name="registro-company"),
]
