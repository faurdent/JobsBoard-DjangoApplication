from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, CreateView

from apps.auth_app.models import User
from apps.job_board.forms import UpdateVacancyForm, CreateVacancyForm
from apps.job_board.models import Vacancy, CompanyOwnership, VacancyResponse


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
        vacancies = Vacancy.objects.filter(is_closed=False)
        if position_name := self.request.GET.get("position-name", ""):
            return vacancies.filter(name__icontains=position_name).all()
        return vacancies.all()


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
