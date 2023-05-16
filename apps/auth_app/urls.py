from django.urls import path
from apps.auth_app.views import JobSeekerSignUpView, EmployerSignUpView, LoginUserView, MyProfileView, ProfileView


urlpatterns = [
    path("sign-up/job-seeker", JobSeekerSignUpView.as_view(), name="register_jobseeker"),
    path("sign-up/employer", EmployerSignUpView.as_view(), name="register_employer"),
    path("login", LoginUserView.as_view(), name="login"),
    path("me", MyProfileView.as_view(), name="me"),
    path("profile/<str:username>", ProfileView.as_view(), name="profile")
]
