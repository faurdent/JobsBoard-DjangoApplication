from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import QuerySet
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

from apps.auth_app.forms import SignUpEmployerForm, SignUpJobSeekerForm
from apps.auth_app.models import JobSeeker, Employer, User


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
            raise Http404


class MyProfileView(ProfileView):
    template_name = "auth/my_profile.html"

    def get_object(self, queryset=None):
        return self.request.user
