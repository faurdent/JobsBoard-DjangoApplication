from django import forms

from apps.auth_app.models import User
from apps.job_board.models import Company, Vacancy


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ("name", "description")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
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

    def _get_users_companies(self, user: User):
        if user.account_type == User.Types.JOBSEEKER:
            return []  # TODO: Return HR current company
        return user.employer_profile.companies


class UpdateVacancyForm(BaseVacancyForm):
    pass
