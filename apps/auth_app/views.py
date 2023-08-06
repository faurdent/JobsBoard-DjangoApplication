from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import QuerySet
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from apps.auth_app.forms import SignUpEmployerForm, SignUpJobSeekerForm, LoginForm, UpdateProfileForm
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
    template_name = "auth/login_form.html"
    form_class = LoginForm


class BaseProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "auth/user_profile.html"
    context_object_name = "user_profile"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object:
            return redirect("not_found")
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_object(self, queryset=None):
        username = self.kwargs.get("username")
        queryset: QuerySet[User] = self.get_queryset()
        if user := queryset.filter(username=username).select_related().first():
            return user


class ProfileView(BaseProfileView):
    def get(self, request, *args, **kwargs):
        if self.kwargs["username"] == request.user.username:
            return redirect("me")
        return super().get(request, *args, **kwargs)


class MyProfileView(BaseProfileView):
    template_name = "auth/my_profile.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user: User = self.request.user
        match user.account_type:
            case User.Types.EMPLOYER:
                owned_companies = CompanyOwnership.objects.filter(owner=user.employer_profile)
                context.update({
                    "owned_companies": owned_companies.filter(is_creator=False).all(),
                    "created_companies": owned_companies.filter(is_creator=True).all()
                })
            case User.Types.JOBSEEKER:
                context.update({"responses_on_vacancies": VacancyResponse.objects.filter(user=user).all()})
            case User.Types.EMPLOYEE:
                context.update({"employee_info": user.employee_profile})
        return context


class UpdateProfile(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UpdateProfileForm
    template_name = "auth/update_profile.html"

    def get_object(self, queryset=None):
        return self.request.user
