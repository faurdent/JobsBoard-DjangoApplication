from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.handlers.wsgi import WSGIRequest
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView, ListView, UpdateView, DeleteView

from apps.auth_app.models import JobSeekerProfile, User
from apps.auth_app.models.models import EmployeeProfile, Employee, EmployerProfile
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
        context.update({"is_company_owner": False, "is_creator": False})
        if self.request.user.account_type == User.Types.EMPLOYER:
            employer_profile = self.request.user.employer_profile
            if ownership := CompanyOwnership.objects.filter(
                    company=company, owner=employer_profile
            ).first():
                context.update({"is_company_owner": True, "is_creator": ownership.is_creator})
        context.update({
            "workers_count": company.workers.count(),
            "owners_count": company.owners.count(),
            "vacancies_count": company.vacancies.count(),
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.object = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object:
            return redirect("not_found")
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_object(self, queryset=None):
        return Vacancy.objects.filter(pk=self.kwargs["pk"], is_closed=False).first()

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

    def get_queryset(self):
        return Vacancy.objects.filter(is_closed=False).all()


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
        ).first() or self.vacancy.is_closed:
            return redirect("not_found")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.vacancy.users_responded.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"vacancy_name": self.vacancy.name})
        return context


class AcceptJobSeeker(LoginRequiredMixin, View):
    def post(self, request: WSGIRequest, *args, **kwargs):
        vacancy_response: VacancyResponse = VacancyResponse.objects.filter(
            user_id=self.kwargs["user_pk"], vacancy_id=self.kwargs["vacancy_pk"]
        ).first()
        if not vacancy_response:
            return redirect("not_found")
        with transaction.atomic():
            vacancy_response.status = VacancyResponse.ResponseStatus.ACCEPTED
            vacancy_response.vacancy.is_closed = True
            vacancy_response.user.account_type = User.Types.EMPLOYEE
            self._save_related_data(vacancy_response)
            EmployeeProfile.objects.create(
                user=vacancy_response.user,
                company=vacancy_response.vacancy.company,
                position=vacancy_response.vacancy.position
            )
        return redirect("all_employees", pk=vacancy_response.vacancy.company.pk)

    def _save_related_data(self, vacancy_response: VacancyResponse):
        vacancy_response.save()
        vacancy_response.vacancy.save()
        vacancy_response.user.save()


class RejectJobSeeker(LoginRequiredMixin, View):
    def post(self, request: WSGIRequest, *args, **kwargs):
        vacancy_response: VacancyResponse = VacancyResponse.objects.filter(
            user_id=self.kwargs["user_pk"], vacancy_id=self.kwargs["vacancy_pk"]
        ).first()
        if not vacancy_response:
            return redirect("not_found")
        vacancy_response.status = VacancyResponse.ResponseStatus.REJECTED
        vacancy_response.save()
        return redirect("view_responses", pk=self.kwargs["vacancy_pk"])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"company": self.company})
        return context


class FireEmployeeView(LoginRequiredMixin, View):
    def post(self, request: WSGIRequest, *args, **kwargs):
        employee = Employee.objects.filter(pk=self.kwargs["user_pk"]).first()
        if not employee:
            return redirect("not_found")
        employee.account_type = User.Types.JOBSEEKER
        employee.employee_profile.delete()
        employee.save()
        return redirect("all_employees", pk=self.kwargs["company_pk"])


class EmployerCompaniesView(LoginRequiredMixin, ListView):
    model = Company
    context_object_name = "companies"
    template_name = "job_board/employer_companies.html"

    def get(self, request, *args, **kwargs):
        if self.request.user.account_type != User.Types.EMPLOYER:
            return redirect("not_found")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.employer_profile.companies.all()


class CompanyInfoAbstractView(ListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = None

    def get(self, request, *args, **kwargs):
        self.company = Company.objects.filter(pk=self.kwargs["pk"]).first()
        if not self.company:
            return redirect("not_found")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "company": self.company,
            }
        )
        if self.request.user.account_type == User.Types.EMPLOYER:
            context.update(
                {"is_owner": CompanyOwnership.objects.filter(company=self.company,
                                                             owner=self.request.user.employer_profile).exists()}
            )
        return context


class CompanyVacanciesView(CompanyInfoAbstractView):
    model = Vacancy
    template_name = "job_board/company_vacancies.html"
    context_object_name = "vacancies"

    def get_queryset(self):
        return self.company.vacancies.all()


class CompanyEmployeesView(CompanyInfoAbstractView):
    model = Employee
    context_object_name = "employees"
    template_name = "job_board/view_all_employees.html"

    def get_queryset(self):
        return self.company.employees.all()


class CompanyOwnersView(CompanyInfoAbstractView):
    model = EmployeeProfile
    context_object_name = "owners"
    template_name = "job_board/company_owners.html"

    def get_queryset(self):
        return self.company.owners.all()


class AddOwnerView(LoginRequiredMixin, CreateView):
    model = CompanyOwnership
