from django import forms

from apps.auth_app.models import User
from apps.job_board.models import Company, Vacancy, PositionType


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ("name", "description", "logo")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "logo": forms.FileInput(attrs={"class": "form-control"}),
        }


class BaseVacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
        }
        fields = ("name", "description")


class CreateVacancyForm(BaseVacancyForm):
    class Meta(BaseVacancyForm.Meta):
        fields = (*BaseVacancyForm.Meta.fields, "company", "position")
        widgets = {
            **BaseVacancyForm.Meta.widgets,
            "company": forms.Select(attrs={"class": "form-control"}),
            "position": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, user: User, **kwargs):
        super().__init__(**kwargs)
        self.fields["company"].queryset = self._get_users_companies(user)
        self.fields["position"].queryset = self._get_positions(user)

    def _get_users_companies(self, user: User):
        if user.account_type == User.Types.EMPLOYEE:
            return Company.objects.filter(pk=user.employee_profile.company.pk)
        return user.employer_profile.companies

    def _get_positions(self, user: User):
        if user.account_type == User.Types.EMPLOYEE:
            # Only Owner can post another HR vacancy
            return PositionType.objects.exclude(name="HR").all()
        return PositionType.objects.all()


class UpdateVacancyForm(BaseVacancyForm):
    pass
