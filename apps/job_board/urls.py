from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexJobSeekerView.as_view(), name="home"),
    path("employer", views.IndexEmployerView.as_view(), name="employer_home"),
    path("create-company", views.CreateCompany.as_view(), name="create_company"),
    path("company-profile/<int:pk>", views.DetailCompany.as_view(), name="company_details")
]
