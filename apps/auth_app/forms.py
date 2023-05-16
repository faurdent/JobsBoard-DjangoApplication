from django.contrib.auth.forms import UserCreationForm

from apps.auth_app.models import Employer, JobSeeker


class SignUpEmployerForm(UserCreationForm):
    class Meta:
        model = Employer
        fields = ('username', 'email', 'password1', 'password2')


class SignUpJobSeekerForm(UserCreationForm):
    class Meta:
        model = JobSeeker
        fields = ('username', 'email', 'password1', 'password2')
