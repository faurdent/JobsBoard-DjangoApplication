from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField
from django.contrib.auth.models import Group
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apps.auth_app.models import Employer, JobSeeker, User


class LoginForm(AuthenticationForm):
    username = UsernameField(
        widget=forms.TextInput(attrs={"class": "form-control", "autofocus": True})
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "current-password"}),
    )


class BaseUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'type': 'password'}),
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'type': 'password'}),
    )

    class Meta:
        fields = ('username', 'email', 'password1', 'password2', "avatar")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }


class SignUpEmployerForm(BaseUserCreationForm):
    def save(self, commit=True):
        with transaction.atomic():
            employer = super().save(commit)
            owner_group = Group.objects.get(name="Owner")
            employer.groups.add(owner_group)
            return employer

    class Meta(BaseUserCreationForm.Meta):
        model = Employer


class SignUpJobSeekerForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = JobSeeker


class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "bio", "avatar")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "autofocus": True}),
            "bio": forms.Textarea(attrs={"class": "form-control"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }
