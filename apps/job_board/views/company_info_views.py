from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import ListView

from apps.auth_app.models import EmployerProfile, User
from apps.auth_app.models.models import Employee
from apps.job_board.models import Vacancy, Company
from apps.job_board.views.modificated_views import CompanyInfoAbstractView


class CompanyVacanciesView(CompanyInfoAbstractView):
    model = Vacancy
    template_name = "job_board/company_vacancies.html"
    context_object_name = "vacancies"

    def get_queryset(self):
        return self.company.vacancies.filter(is_closed=False).all()


class CompanyEmployeesView(CompanyInfoAbstractView):
    model = Employee
    context_object_name = "employees"
    template_name = "job_board/view_all_employees.html"

    def get_queryset(self):
        return self.company.employees.all()


class CompanyOwnersView(CompanyInfoAbstractView):
    model = EmployerProfile
    context_object_name = "owners"
    template_name = "job_board/company_owners.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"creator": self.queryset.filter(has_company=True).first()})
        return context

    def get_queryset(self):
        self.queryset = self.company.owners.all()
        return self.queryset.filter(has_company=False).all()


class EmployerCompaniesView(LoginRequiredMixin, ListView):
    model = Company
    context_object_name = "companies"
    template_name = "job_board/employer_companies.html"

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and user != User.Types.EMPLOYER:
            return redirect("not_found")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.employer_profile.companies.all()
