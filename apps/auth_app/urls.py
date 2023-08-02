from django.urls import path
from apps.auth_app import views


urlpatterns = [
    path("sign-up/job-seeker", views.JobSeekerSignUpView.as_view(), name="register_jobseeker"),
    path("sign-up/employer", views.EmployerSignUpView.as_view(), name="register_employer"),
    path("login", views.LoginUserView.as_view(), name="login"),
    path("me", views.MyProfileView.as_view(), name="me"),
    path("profile/<str:username>", views.ProfileView.as_view(), name="profile"),
    path("me/update", views.UpdateProfile.as_view(), name="update-profile")
]
