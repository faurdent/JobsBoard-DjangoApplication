from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView

from apps.auth_app.models import JobSeekerProfile, User
from apps.job_board.models import Company, Vacancy, CompanyOwnership


class IndexAbstractView(TemplateView):

    def get_context_data(self, **kwargs):
        return {
            "companies_count": Company.objects.all().count(),
            "job_seekers_count": JobSeekerProfile.objects.filter(cv__isnull=True).count(),
            "vacancies_count": Vacancy.objects.filter(is_closed=False).count(),
        }


class CompanyInfoAbstractView(ListView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = None

    def get(self, request, *args, **kwargs):
        self.company = Company.objects.filter(pk=self.kwargs["pk"]).first()
        if not self.company:
            return redirect("not_found")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "company": self.company,
            }
        )
        if self.request.user.account_type == User.Types.EMPLOYER:
            context.update(
                {"is_owner": CompanyOwnership.objects.filter(company=self.company,
                                                             owner=self.request.user.employer_profile).exists()}
            )
        return context
