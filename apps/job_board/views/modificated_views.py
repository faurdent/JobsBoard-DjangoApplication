from django.views.generic import TemplateView

from apps.auth_app.models import JobSeekerProfile
from apps.job_board.models import Company, Vacancy


class IndexView(TemplateView):

    def get_context_data(self, **kwargs):
        return {
            "companies_count": Company.objects.all().count(),
            "job_seekers_count": JobSeekerProfile.objects.filter(cv__isnull=True).count(),
            "vacancies_count": Vacancy.objects.filter(is_closed=False).count(),
        }
