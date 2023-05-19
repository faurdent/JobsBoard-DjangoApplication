from django import forms

from apps.job_board.models import Company


class CreateCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ("name", "description")
