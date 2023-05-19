from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView, CreateView, DetailView

from apps.auth_app.models import Employer, JobSeeker, JobSeekerProfile
from apps.job_board.forms import CreateCompanyForm
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
    template_name = "job_board/create_company_form.html"
    form_class = CreateCompanyForm
    permission_required = "job_board.add_company"
    model = Company
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None
    def post(self, request, *args, **kwargs):
        form: CreateCompanyForm = self.get_form()
        if form.is_valid():
            company = form.save()
            CompanyOwnership.objects.create(company=company, owner=request.user.employer_profile, is_creator=True)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class UpdateCompany:
    pass


class DetailCompany(DetailView):
    model = Company
    template_name = "job_board/company_details.html"
    context_object_name = "company"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employer_companies = self.request.user.employer_profile.companies.all()
        q = self.object
        if self.object in employer_companies:
            print("")
        return context


class ViewCompanies:
    pass


class CreateVacancy:
    pass


class UpdateVacancy:
    pass


class DetailVacancy:
    pass


class ViewVacancies:
    pass
