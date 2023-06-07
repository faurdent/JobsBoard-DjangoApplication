from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView, UpdateView, CreateView

from apps.auth_app.models import EmployerProfile, User
from apps.job_board.forms import CompanyForm
from apps.job_board.models import Company, CompanyOwnership


class CreateCompany(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name = "job_board/company_form.html"
    form_class = CompanyForm
    permission_required = "job_board.add_company"
    model = Company

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None

    def post(self, request, *args, **kwargs):
        form: CompanyForm = self.get_form()
        employer_profile = self.request.user.employer_profile
        if form.is_valid():
            company = form.save()
            employer_profile.has_company = True
            employer_profile.save()
            CompanyOwnership.objects.create(company=company, owner=employer_profile, is_creator=True)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class UpdateCompany(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    permission_required = "job_board.change_company"
    template_name = "job_board/company_form.html"

    def get(self, request, *args, **kwargs):
        if self._is_creator():
            return super().get(request, *args, **kwargs)
        return redirect("not_found")

    def post(self, request, *args, **kwargs):
        if self._is_creator():
            return super().post(request, *args, **kwargs)
        return redirect("not_found")

    def _is_creator(self):
        company: Company = self.get_object()
        return bool(
            CompanyOwnership.objects.filter(
                company=company, owner=self.request.user.employer_profile, is_creator=True
            ).first()
        )


class DetailCompany(DetailView):
    model = Company
    template_name = "job_board/company_details.html"
    context_object_name = "company"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company: Company = self.object
        user: User = self.request.user
        context.update({"is_company_owner": False, "is_creator": False})
        if user.account_type == User.Types.EMPLOYER:
            employer_profile = self.request.user.employer_profile
            if ownership := CompanyOwnership.objects.filter(
                    company=company, owner=employer_profile
            ).first():
                context.update({"is_company_owner": True, "is_creator": ownership.is_creator})
        context.update({
            "workers_count": company.employees.count(),
            "owners_count": company.owners.count(),
            "vacancies_count": company.vacancies.filter(is_closed=False).count(),
        })
        return context


class DeleteCompany(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Company
    permission_required = "job_board.delete_company"
    success_url = reverse_lazy("my_companies")

    def post(self, request, *args, **kwargs):
        employer_profile: EmployerProfile = request.user.employer_profile
        with transaction.atomic():
            response = super().post(request, *args, **kwargs)
            if employer_profile.companies.count() == 0:
                employer_profile.has_company = False
                employer_profile.save()
        return response


class ViewCompanies(ListView):
    model = Company
    context_object_name = "companies"
    template_name = "job_board/view_all_companies.html"
