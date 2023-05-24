from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView, ListView, UpdateView

from apps.auth_app.models import JobSeekerProfile, User
from apps.job_board.forms import CompanyForm, CreateVacancyForm, UpdateVacancyForm
from apps.job_board.models import Company, Vacancy, CompanyOwnership, VacancyResponse


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
    template_name = "job_board/vacancy_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"title": "Create vacancy", "message": "Create vacancy for your company"})
        return context

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.form_class
        return form_class(self.request.user, **self.get_form_kwargs())


class UpdateVacancy(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    form_class = UpdateVacancyForm
    model = Vacancy
    permission_required = "job_board.change_vacancy"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"title": "Update vacancy", "message": "Update vacancy"})
        return context


class DetailVacancy(DetailView):
    model = Vacancy
    template_name = "job_board/detail_vacancy.html"
    context_object_name = "vacancy"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "is_responded": False,
            "can_change_vacancy": False,
        })
        vacancy: Vacancy = self.object
        user: User = self.request.user
        match user.account_type:
            case user.Types.JOBSEEKER:
                context.update({
                    "is_responded": bool(vacancy.users_responded.filter(user=user).first())
                })
            case user.Types.EMPLOYER:
                context.update({
                    "can_change_vacancy": bool(vacancy.company.owners.filter(user=self.request.user).first())
                })
        return context


class ViewVacancies(ListView):
    model = Vacancy
    context_object_name = "vacancies"
    template_name = "job_board/view_all_vacancies.html"


class EntityNotFoundView(TemplateView):
    template_name = "job_board/error_template.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"error": "Page not found", "error_message": "You don't have such record."})
        return context


class VacancyResponseView(LoginRequiredMixin, View):
    def post(self, request: WSGIRequest, *args, **kwargs):
        vacancy = Vacancy.objects.filter(pk=self.kwargs["pk"]).first()
        if not vacancy:
            return redirect("not_found")
        if existing_response := VacancyResponse.objects.filter(
                user=request.user, vacancy=vacancy
        ).first():
            existing_response.delete()
        else:
            vacancy_response = VacancyResponse.objects.create(user=request.user, vacancy=vacancy)
            vacancy.users_responded.add(vacancy_response)
        return redirect("vacancy_details", pk=vacancy.pk)


class ResponsesView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = VacancyResponse
    permission_required = "job_board.view_vacancyresponse"
    context_object_name = "vacancy_responses"
    template_name = "job_board/view_vacancy_responses.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vacancy = None

    def get(self, request, *args, **kwargs):
        self.vacancy = get_object_or_404(Vacancy, pk=self.kwargs["pk"])
        if not CompanyOwnership.objects.filter(
                company=self.vacancy.company, owner=self.request.user.employer_profile
        ).first():
            return redirect("not_found")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.vacancy.users_responded.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"vacancy_name": self.vacancy.name})
        return context
