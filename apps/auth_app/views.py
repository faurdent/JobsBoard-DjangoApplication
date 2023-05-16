from django.views.generic import CreateView
from apps.auth_app.models import JobSeeker, Employer
from apps.auth_app.forms import SignUpEmployerForm, SignUpJobSeekerForm


class EmployerSignUpView(CreateView):
    form_class = SignUpEmployerForm
    model = Employer
    template_name = "auth/sign_up_employer.html"
    success_url = "/"


class JobSeekerSignUpView(CreateView):
    form_class = SignUpJobSeekerForm
    model = JobSeeker
    template_name = "auth/sign_up_jobseeker.html"
    success_url = "/"
