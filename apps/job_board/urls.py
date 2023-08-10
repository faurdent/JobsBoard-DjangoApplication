from django.urls import path

from . import views

index = [
    path("", views.IndexJobSeekerView.as_view(), name="home"),
    path("employer", views.IndexEmployerView.as_view(), name="employer_home"),
]

company_crud = [
    path("create-company", views.CreateCompany.as_view(), name="create_company"),
    path("company-profile/<int:pk>", views.DetailCompany.as_view(), name="company_details"),
    path("companies", views.ViewCompanies.as_view(), name="all_companies"),
    path("update-company/<int:pk>", views.UpdateCompany.as_view(), name="update_company"),
    path("delete-company/<int:pk>", views.DeleteCompany.as_view(), name="delete_company"),
]

vacancy_crud = [
    path("create-vacancy", views.CreateVacancy.as_view(), name="create_vacancy"),
    path("detail-vacancy/<int:pk>", views.DetailVacancy.as_view(), name="vacancy_details"),
    path("update-vacancy/<int:pk>", views.UpdateVacancy.as_view(), name="update_vacancy"),
    path("all-vacancies", views.ViewVacancies.as_view(), name="all_vacancies"),
    path("vacancy-responses/<int:pk>", views.ResponsesView.as_view(), name="view_responses"),
]

actions = [
    path("change-response-status/<int:pk>", views.VacancyResponseView.as_view(), name="change_response"),
    path("reject-response/<int:vacancy_pk>/<int:user_pk>", views.RejectJobSeeker.as_view(), name="reject_jobseeker"),
    path("accept-response/<int:vacancy_pk>/<int:user_pk>", views.AcceptJobSeeker.as_view(), name="accept_jobseeker"),
    path("fire-employee/<int:company_pk>/<int:user_pk>", views.FireEmployeeView.as_view(), name="fire_employee"),
    path("request-ownership/<int:company_pk>", views.RequestCompanyOwnership.as_view(), name="request_ownership")
]

company_info = [
    path("company-vacancies/<int:pk>", views.CompanyVacanciesView.as_view(), name="company_vacancies"),
    path("my-companies", views.EmployerCompaniesView.as_view(), name="my_companies"),
    path("company-owners/<int:pk>", views.CompanyOwnersView.as_view(), name="company_owners"),
    path("company-employees/<int:pk>", views.CompanyEmployeesView.as_view(), name="company_employees"),
]

errors = [
    path("errors/404", views.EntityNotFoundView.as_view(), name="not_found"),
]

urlpatterns = index + company_crud + vacancy_crud + actions + company_info + errors
