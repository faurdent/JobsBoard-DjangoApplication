from django import forms

from apps.auth_app.models import User
from apps.job_board.models import Company, Vacancy


class CreateCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ("name", "description")


class CreateVacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ("name", "description", "company", "position")

    def __init__(self, user: User, **kwargs):
        super().__init__(**kwargs)
        self.fields["company"].queryset = self._get_users_companies(user)

    def _get_users_companies(self, user: User):
        if user.account_type == User.Types.JOBSEEKER:
            return [] # TODO: Return HR current company
        return user.employer_profile.companies
