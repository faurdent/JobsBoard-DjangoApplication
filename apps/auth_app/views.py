from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import QuerySet
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

from apps.auth_app.forms import SignUpEmployerForm, SignUpJobSeekerForm
from apps.auth_app.models import JobSeeker, Employer, User
from apps.job_board.models import CompanyOwnership, VacancyResponse


class EmployerSignUpView(CreateView):
    form_class = SignUpEmployerForm
    model = Employer
    template_name = "auth/sign_up_employer.html"
    success_url = reverse_lazy("login")


class JobSeekerSignUpView(CreateView):
    form_class = SignUpJobSeekerForm
    model = JobSeeker
    template_name = "auth/sign_up_jobseeker.html"
    success_url = reverse_lazy("login")


class LoginUserView(LoginView):
    template_name = "auth/_auth_form.html"


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "auth/user_detail.html"
    context_object_name = "user_profile"

    def get_object(self, queryset=None):
        username = self.kwargs.get("username")
        queryset: QuerySet[User] = self.get_queryset()
        if user := queryset.filter(username=username).select_related().first():
            return user
        else:
            return redirect("not_found")


class MyProfileView(ProfileView):
    template_name = "auth/my_profile.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user: User = self.request.user
        match user.account_type:
            case User.Types.EMPLOYER:
                context.update({"owned_companies": CompanyOwnership.objects.filter(owner=user.employer_profile).all()})
            case User.Types.JOBSEEKER:
                context.update({"responses_on_vacancies": VacancyResponse.objects.filter(user=user).all()})
            case User.Types.EMPLOYEE:
                context.update({"employee_info": user.employee_profile})
        return context
