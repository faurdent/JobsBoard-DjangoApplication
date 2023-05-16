from django.urls import path
from apps.auth_app.views import JobSeekerSignUpView, EmployerSignUpView


urlpatterns = [
    path("sign-up/job-seeker", JobSeekerSignUpView.as_view(), name="register_jobseeker"),
    path("sign-up/employer", EmployerSignUpView.as_view(), name="register_employer"),
]
