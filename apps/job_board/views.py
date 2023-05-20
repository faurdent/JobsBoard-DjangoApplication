from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView, CreateView, DetailView, ListView, UpdateView

from apps.auth_app.models import JobSeekerProfile, User
from apps.job_board.forms import CompanyForm, CreateVacancyForm
from apps.job_board.models import Company, Vacancy, CompanyOwnership


class IndexView(TemplateView):

    def get_context_data(self, **kwargs):
        return {
            "companies_count": Company.objects.all().count(),
            "job_seekers_count": JobSeekerProfile.objects.filter(cv__isnull=True).count(),
            "vacancies_count": Vacancy.objects.all().count(),
        }


class IndexJobSeekerView(IndexView):
    template_name = "job_board/index.html"


class IndexEmployerView(IndexView):
    template_name = "job_board/index_employer.html"


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
        if form.is_valid():
            company = form.save()
            CompanyOwnership.objects.create(company=company, owner=request.user.employer_profile, is_creator=True)
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
        if self.request.user.account_type != User.Types.EMPLOYER:
            context.update({"is_company_owner": False})
        else:
            employer_profile = self.request.user.employer_profile
            if employer_profile.companies.filter(
                    owners__companyownership__company_id=company.pk
            ).first():
                context.update({"is_company_owner": True})
            else:
                context.update({"is_company_owner": False})
        context.update({
            "workers_count": company.workers.count(),
            "owners_count": company.owners.count(),
            "vacancies_count": company.vacancies.count(),
        })
        return context


class ViewCompanies(ListView):
    model = Company
    context_object_name = "companies"
    template_name = "job_board/view_all_companies.html"


class CreateVacancy(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = "job_board.add_vacancy"
    model = Vacancy
    form_class = CreateVacancyForm
    template_name = "job_board/create_vacancy_form.html"

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.form_class
        return form_class(self.request.user, **self.get_form_kwargs())


class UpdateVacancy:
    pass


class DetailVacancy(DetailView):
    model = Vacancy
    template_name = "job_board/detail_vacancy.html"
    context_object_name = "vacancy"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vacancy: Vacancy = self.object
        if vacancy.company.owners.filter(user=self.request.user).first():
            context.update({"can_change_vacancy": True})
        else:
            context.update({"can_change_vacancy": False})
        return context


class ViewVacancies:
    pass


class EntityNotFoundView(TemplateView):
    template_name = "job_board/error_template.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"error": "Page not found", "error_message": "You don't have such record."})
        return context
