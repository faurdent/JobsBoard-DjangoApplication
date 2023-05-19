from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

from apps.auth_app.models import Employer, JobSeeker


class SignUpEmployerForm(UserCreationForm):
    def save(self, commit=True):
        employer = super().save(commit)
        owner_group = Group.objects.get(name="Owner")
        employer.groups.add(owner_group)
        return employer

    class Meta:
        model = Employer
        fields = ('username', 'email', 'password1', 'password2')


class SignUpJobSeekerForm(UserCreationForm):
    class Meta:
        model = JobSeeker
        fields = ('username', 'email', 'password1', 'password2')
